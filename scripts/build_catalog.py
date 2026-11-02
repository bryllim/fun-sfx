#!/usr/bin/env python3
"""Import a folder into a new FUN SFX pack. Standard library + FFmpeg/ffprobe."""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import unicodedata
from render_catalog import write_docs

ROOT = Path(__file__).resolve().parents[1]
EXTENSIONS = {'.mp3', '.mp4', '.wav', '.m4a', '.aac', '.ogg', '.flac', '.aiff', '.aif', '.webm'}
# Filename hints, not acoustic analysis or a statement of rights.
RULES = [
    ('transition', ['whoosh', 'whoop', 'vanish', 'rewind', 'vhs', 'tv turn'], ['transition', 'movement', 'cut']),
    ('impact', ['bamboo', 'bass boost', 'vine boom', 'splat', 'falling', 'muda'], ['impact', 'hit', 'emphasis']),
    ('interface', ['camera', 'ding', 'buzzer', 'windows', 'typing', 'typewriter', 'alarm', 'spotlight'], ['interface', 'notification', 'punctuation']),
    ('ambience', ['cricket', 'underwater', 'vacuum', 'applause', 'snore'], ['ambience', 'background', 'pause']),
    ('game', ['fortnite', 'minecraft', 'zelda', 'pokeball', 'freddys', 'enemy spotted'], ['game', 'reaction']),
    ('music', ['choir', 'harmonica', 'sax', 'violin', 'theme', 'song', 'music', 'illuminati'], ['music', 'sting', 'mood']),
]
HINTS = [
    (['awkward', 'cricket', 'pause'], ['awkward', 'silence', 'comedy']),
    (['sad', 'disappointed', 'violin', 'harmonica'], ['sad', 'fail', 'disappointment']),
    (['wow', 'huh', 'what', 'oh my', 'yoooo', 'faah'], ['surprise', 'reaction']),
    (['scream', 'freddys', 'help me'], ['scream', 'tension']),
    (['applause', 'yeah baby', 'ding', 'get item'], ['success', 'celebration']),
    (['choir', 'ultra instinct', 'epic', 'heavens'], ['epic', 'reveal']),
    (['fuck', 'f_ck', 'shit', 'wtf'], ['explicit-language-likely']),
]

def checksum(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()

def probe(path):
    result = subprocess.run(['ffprobe', '-v', 'error', '-show_format', '-show_streams', '-of', 'json', str(path)], check=True, capture_output=True, text=True)
    data = json.loads(result.stdout)
    audio = next((s for s in data['streams'] if s['codec_type'] == 'audio'), None)
    if audio is None:
        raise ValueError(f'No audio stream: {path.name}')
    return {
        'duration_seconds': round(float(audio.get('duration') or data['format']['duration']), 6),
        'codec': audio['codec_name'], 'sample_rate_hz': int(audio['sample_rate']),
        'channels': audio['channels'], 'size_bytes': path.stat().st_size,
    }

def slug(name):
    ascii_name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '-', ascii_name).strip('-') or 'sound'

def classify(name):
    lower = name.lower()
    category, tags = 'reaction', ['reaction', 'meme', 'comedy']
    for group, keywords, defaults in RULES:
        if any(word in lower for word in keywords):
            category, tags = group, list(defaults)
            break
    for keywords, hints in HINTS:
        if any(word in lower for word in keywords):
            tags.extend(hints)
    return category, sorted(set(tags))

def import_one(item):
    source, identifier = item
    original = ROOT / 'assets' / 'originals' / (identifier + source.suffix.lower())
    shutil.copy2(source, original)
    audio = original
    if source.suffix.lower() in {'.mp4', '.webm'}:
        audio = ROOT / 'assets' / 'audio' / (identifier + '.wav')
        subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-nostdin', '-n', '-i', str(original), '-map', '0:a:0', '-vn', '-ar', '48000', '-ac', '2', '-c:a', 'pcm_s16le', str(audio)], check=True)
    category, tags = classify(source.stem)
    return {
        'id': identifier, 'title': source.stem, 'original_filename': source.name,
        'category': category, 'tags': tags, 'annotation_basis': 'filename; not auditioned',
        'original_path': original.relative_to(ROOT).as_posix(),
        'audio_path': audio.relative_to(ROOT).as_posix(),
        'original_sha256': checksum(original), 'audio_sha256': checksum(audio),
        'original': probe(original), 'audio': probe(audio),
        'license_status': 'unverified', 'license': None, 'author': None, 'source_url': None,
    }

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path, help='Source folder; scanned recursively')
    args = parser.parse_args()
    source = args.source.resolve()
    if not source.is_dir():
        parser.error('Source must be a directory')
    if (ROOT / 'catalog.json').exists() or any((ROOT / 'assets').rglob('*.*')):
        parser.error('Import requires an empty pack; existing catalog/assets are never overwritten')
    for tool in ('ffmpeg', 'ffprobe'):
        if shutil.which(tool) is None:
            parser.error(f'{tool} is required on PATH')
    sources = sorted((p for p in source.rglob('*') if p.is_file() and p.suffix.lower() in EXTENSIONS and not p.is_relative_to(ROOT)), key=lambda p: p.relative_to(source).as_posix().casefold())
    if not sources:
        parser.error('No supported media files found outside the destination pack')
    used, items = set(), []
    for path in sources:
        base = slug(path.stem)
        identifier, index = base, 2
        while identifier in used:
            identifier, index = f'{base}-{index}', index + 1
        used.add(identifier)
        items.append((path, identifier))
    for directory in ('assets/originals', 'assets/audio', 'references'):
        (ROOT / directory).mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=4) as executor:
        records = list(executor.map(import_one, items))
    catalog = {'schema_version': 1, 'name': 'FUN SFX', 'source_collection': source.name, 'annotation_basis': 'filename; not auditioned', 'asset_license_status': 'unverified', 'count': len(records), 'sounds': records}
    (ROOT / 'catalog.json').write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    write_docs(ROOT, catalog)
    print(json.dumps({'imported': len(records), 'categories': dict(Counter(s['category'] for s in records)), 'original_bytes': sum(s['original']['size_bytes'] for s in records), 'duration_seconds': round(sum(s['audio']['duration_seconds'] for s in records), 2)}, indent=2))

if __name__ == '__main__':
    main()
