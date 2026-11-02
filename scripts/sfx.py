#!/usr/bin/env python3
"""Search, inspect, verify, and export FUN SFX recordings. No Python dependencies."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

def asset_path(relative):
    path = (ROOT / relative).resolve()
    if not path.is_relative_to((ROOT / 'assets').resolve()):
        raise ValueError(f'Asset path is outside assets/: {relative}')
    return path

def digest(path):
    result = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(block)
    return result.hexdigest()

def finite(value):
    number = float(value)
    if not math.isfinite(number):
        raise argparse.ArgumentTypeError('Must be a finite number')
    return number

def resolved(sound):
    return {**sound, 'absolute_audio_path': str(asset_path(sound['audio_path'])), 'absolute_original_path': str(asset_path(sound['original_path']))}

def export(sound, args):
    if not shutil.which('ffmpeg'):
        raise ValueError('Export needs ffmpeg on PATH')
    length = sound['audio']['duration_seconds']
    if args.start < 0 or args.start >= length:
        raise ValueError(f'--start must be >= 0 and < {length} seconds')
    duration = args.duration if args.duration is not None else length - args.start
    if duration <= 0 or args.start + duration > length + 0.001:
        raise ValueError('Excerpt duration must be positive and fit within the recording')
    if args.fade_ms < 0:
        raise ValueError('--fade-ms must be nonnegative')
    output = args.output.expanduser().resolve()
    if output.suffix.lower() != '.wav':
        raise ValueError('Output must have a .wav extension')
    if output.exists():
        raise ValueError(f'Output already exists: {output}')
    if output.is_relative_to((ROOT / 'assets').resolve()):
        raise ValueError('Write exports outside bundled assets/')
    fade = min(args.fade_ms / 1000, duration / 2)
    filters = [f'atrim=start={args.start}:duration={duration}', 'asetpts=PTS-STARTPTS', f'volume={args.gain_db}dB']
    if fade:
        filters += [f'afade=t=in:st=0:d={fade}', f'afade=t=out:st={duration-fade}:d={fade}']
    output.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-nostdin', '-n', '-i', str(asset_path(sound['audio_path'])), '-map', '0:a:0', '-vn', '-af', ','.join(filters), '-ar', '48000', '-ac', '2', '-c:a', 'pcm_s16le', str(output)], check=True)
    print(json.dumps({'id': sound['id'], 'output': str(output), 'source_start_seconds': args.start, 'requested_duration_seconds': duration, 'gain_db': args.gain_db, 'fade_ms': fade * 1000, 'license_status': sound['license_status'], 'ownership_notice': sound.get('ownership_notice')}, indent=2))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    for name in ('list', 'search'):
        command = commands.add_parser(name, help='List all sounds' if name == 'list' else 'Search names, tags, and recommended use cases')
        if name == 'search':
            command.add_argument('query')
        command.add_argument('--category')
        command.add_argument('--max-duration', type=finite, help='Maximum duration in seconds')
        command.add_argument('--json', action='store_true')
    show = commands.add_parser('show', help='Print a complete record as JSON')
    show.add_argument('id')
    commands.add_parser('verify', help='Verify count, unique IDs, all files, and SHA-256 checksums')
    render = commands.add_parser('export', help='Export a trimmed stereo 48 kHz WAV; never overwrite')
    render.add_argument('id')
    render.add_argument('output', type=Path)
    render.add_argument('--start', type=finite, default=0)
    render.add_argument('--duration', type=finite)
    render.add_argument('--gain-db', type=finite, default=0)
    render.add_argument('--fade-ms', type=finite, default=10)
    args = parser.parse_args()
    try:
        catalog = json.loads((ROOT / 'catalog.json').read_text(encoding='utf-8'))
        if catalog.get('schema_version') != 1:
            raise ValueError('Unsupported catalog schema')
        sounds = catalog['sounds']
        if catalog.get('ownership_notice'):
            print(catalog['ownership_notice'], file=sys.stderr)
            for sound in sounds:
                sound['ownership_notice'] = catalog['ownership_notice']
        if args.command in ('list', 'search'):
            tokens = getattr(args, 'query', '').casefold().split()
            matches = []
            for sound in sounds:
                usage = sound.get('usage', {})
                # Negative guidance must not recommend a sound for a use it warns against.
                haystack = ' '.join([sound['id'], sound['title'], sound['category'], *sound['tags'], usage.get('intent', ''), *usage.get('use_when', []), usage.get('example', '')]).casefold()
                if not all(token in haystack for token in tokens):
                    continue
                if args.category and sound['category'] != args.category:
                    continue
                if args.max_duration is not None and sound['audio']['duration_seconds'] > args.max_duration:
                    continue
                matches.append(resolved(sound))
            if args.json:
                print(json.dumps(matches, ensure_ascii=False, indent=2))
            else:
                for sound in matches:
                    print(f"{sound['id']}\t{sound['category']}\t{sound['audio']['duration_seconds']:.2f}s\t{sound.get('usage', {}).get('intent', '')}\t{sound['absolute_audio_path']}")
                print(f'{len(matches)} sound(s). Recording rights: unverified.', file=sys.stderr)
        elif args.command == 'verify':
            failures, seen, checked = [], set(), set()
            if catalog['count'] != len(sounds):
                failures.append('Catalog count mismatch')
            for sound in sounds:
                if sound['id'] in seen:
                    failures.append(f"Duplicate ID: {sound['id']}")
                seen.add(sound['id'])
                for kind in ('original', 'audio'):
                    path = asset_path(sound[f'{kind}_path'])
                    if not path.is_file() or digest(path) != sound[f'{kind}_sha256']:
                        failures.append(f"Missing or changed: {sound[f'{kind}_path']}")
                    checked.add(path)
            actual = {p.resolve() for p in (ROOT / 'assets').rglob('*') if p.is_file() and p.name != '.DS_Store'}
            failures.extend(f'Uncataloged asset: {p.relative_to(ROOT)}' for p in sorted(actual - checked))
            print(json.dumps({'ok': not failures, 'recordings': len(sounds), 'unique_files': len(checked), 'failures': failures}, indent=2))
            return 1 if failures else 0
        else:
            sound = next((item for item in sounds if item['id'] == args.id), None)
            if sound is None:
                raise ValueError(f'Unknown sound ID: {args.id}; use search or list')
            if args.command == 'show':
                print(json.dumps(resolved(sound), ensure_ascii=False, indent=2))
            else:
                export(sound, args)
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as error:
        print(f'FUN SFX: {error}', file=sys.stderr)
        return 1
    return 0

if __name__ == '__main__':
    sys.exit(main())
