#!/usr/bin/env python3
"""Render the catalog and per-sound editing guide from catalog.json."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def table_text(value):
    return str(value).replace('|', '\\|').replace('\n', ' ')

def write_docs(root, catalog):
    sounds = catalog['sounds']
    guided = sum(bool(s.get('usage')) for s in sounds)
    reviewed = sum(s.get('audio_review', {}).get('status') == 'automated' for s in sounds)
    notice = ['> **Sound ownership:** ' + catalog['ownership_notice'], ''] if catalog.get('ownership_notice') else []
    overview = [
        '# FUN SFX catalog', '',
        *notice,
        f'{len(sounds)} recordings; {guided} individual editing guides; {reviewed} automated audio reviews.', '',
        'All recording rights are unverified. Read [the use-case guide](USE_CASES.md) for when to use each sound, timing, situations to avoid, and an example edit.', '',
        'Tags are filename-derived. Use cases are editorial recommendations, not verified descriptions of every recording. Review status is shown in each guide entry. Audition before selecting an excerpt.', '',
        '| ID | Category | Seconds | Suggested role | Audio |',
        '| --- | --- | ---: | --- | --- |',
    ]
    guide = [
        '# FUN SFX: when to use each sound', '',
        *notice,
        f'{guided} individual guides for {len(sounds)} recordings. Each recommendation describes an editing choice, not a mandatory use.', '',
        '## How to read this guide', '',
        '- **Use when** describes suitable scenes; **Example edit** shows one concrete application.',
        '- **Timing** describes placement relative to the visual event, not an exact source in/out point.',
        '- **Avoid when** describes poor creative matches; these are recommendations, not restrictions.',
        f'- **Automated audio review** means an audio-analysis model inspected the recording ({reviewed} files). It does not mean a human auditioned it. Its timestamps and speech recognition can be approximate or wrong.',
        '- **Filename-based recommendation** means audible contents have not been confirmed. Treat it as a candidate and audition before editing.',
        *(['- ' + catalog['audio_review_summary']['limitation']] if catalog.get('audio_review_summary', {}).get('limitation') else []),
        '- All recording rights remain unverified; see [ASSET_LICENSE.md](../ASSET_LICENSE.md).', '',
        '## Sound index', '',
    ]
    guide += [f"- [{table_text(s['title'])}](#{s['id']})" for s in sounds]
    for sound in sounds:
        usage = sound.get('usage')
        role = usage['intent'] if usage else 'No individual guidance yet'
        overview.append(f"| [`{sound['id']}`](USE_CASES.md#{sound['id']}) | {sound['category']} | {sound['audio']['duration_seconds']:.2f} | {table_text(role)} | [Listen](../{sound['audio_path']}) |")
        guide += ['', f"<a id=\"{sound['id']}\"></a>", '', f"## {sound['title']}", '', f"`{sound['id']}` · {sound['audio']['duration_seconds']:.2f} seconds · {sound['category']} · [Audio](../{sound['audio_path']})", '']
        if not usage:
            guide += ['No individual use-case guidance yet. Search filename tags and audition before choosing this recording.']
            continue
        review = sound.get('audio_review', {})
        if review.get('status') == 'automated':
            guide += ['**Evidence:** Automated audio review; editorial recommendations below.', '', '**Audio notes:** ' + review['summary'], '']
            if review.get('uncertainty'):
                guide += ['**Review limitation:** ' + review['uncertainty'], '']
        else:
            guide += ['**Evidence:** Filename-based recommendation; audible content has not been confirmed.', '']
        guide += [f"**Suggested role:** {usage['intent']}", '', '**Use when:**', '']
        guide += [f'- {item}' for item in usage['use_when']]
        guide += ['', '**Timing:** ' + usage['timing'], '', '**Avoid when:**', '']
        guide += [f'- {item}' for item in usage['avoid_when']]
        guide += ['', '**Example edit:** ' + usage['example']]
    (root / 'references').mkdir(exist_ok=True)
    for name, lines in [('CATALOG.md', overview), ('USE_CASES.md', guide)]:
        (root / 'references' / name).write_text('\n'.join(lines) + '\n', encoding='utf-8')

if __name__ == '__main__':
    write_docs(ROOT, json.loads((ROOT / 'catalog.json').read_text(encoding='utf-8')))
    print('Updated references/CATALOG.md and references/USE_CASES.md')
