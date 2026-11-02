# FUN SFX

**Sound effects for videos edited with agents.**

> **Sound ownership:** The FUN SFX maintainer does not own any of the bundled
> sounds. All rights remain with their respective owners. The MIT license covers
> only this project's code and documentation, not the sounds. Audio permissions
> remain unverified.

A portable agent skill with 71 supplied recordings, a searchable catalog, and
small tools for finding and preparing audio cues. Works with any agent that can
read `SKILL.md`, run Python, and pass audio files to an editing tool.

**License:** code and documentation are [MIT](LICENSE). The bundled recordings
have **unverified rights** and are excluded from MIT; see [ASSET_LICENSE.md](ASSET_LICENSE.md).
This collection is not a rights-cleared audio release.

## What's included

- All 71 source recordings, preserved byte-for-byte with portable filenames.
- Audio extracted from the two MP4s as stereo, 48 kHz PCM WAV.
- JSON and [readable catalogs](references/CATALOG.md) with durations, formats,
  searchable categories/tags, original filenames, and SHA-256 hashes.
- An [agent skill](SKILL.md), editing guidance, and search/trim/export tools.
- [Individual use-case guides for all 71 sounds](references/USE_CASES.md), each
  with suitable scenes, timing, situations to avoid, and an example edit.

MP3s remain in their original format. Audio is neither normalized nor combined
into one track. Tags are inferred from filenames. Seven recordings have automated
audio-analysis notes; 64 have filename-based recommendations because analysis
credits ran out. Every entry identifies its evidence level. Automated notes can
mishear speech and are not a substitute for auditioning the chosen excerpt.

## Use it

Requirements: Python 3.10 or newer. Search and verification use only Python's
standard library. Export requires FFmpeg; importing a new pack requires FFmpeg
and ffprobe. There are no Python packages to install.

From this project folder:

```sh
python3 scripts/sfx.py search "whoosh"
python3 scripts/sfx.py search "sad" --json
python3 scripts/sfx.py search "failed attempt" --json
python3 scripts/sfx.py search "photo capture"
python3 scripts/sfx.py list --category impact --max-duration 10
python3 scripts/sfx.py show tape-rewind-sound-effect
python3 scripts/sfx.py export tape-rewind-sound-effect output/rewind.wav --duration 0.5 --gain-db -8
python3 scripts/sfx.py verify
```

Search uses case-insensitive AND matching across ID, title, category, tags,
recommended uses, and example edits. It excludes situations to avoid, so a warning
against a use does not count as a recommendation. JSON results and `show` include
the full use-case guidance and evidence status alongside absolute paths.
Export accepts source start, duration,
gain in decibels, and edge fades; it writes stereo 48 kHz WAV and never overwrites
an existing output. See `python3 scripts/sfx.py export --help` for options.

## Install as an agent skill

Clone the project:

```sh
git clone https://github.com/bryllim/fun-sfx.git
cd fun-sfx
```

Keep the whole folder together: the skill depends on its catalog, scripts, and
assets. Place a copy in your agent's skills directory as `fun-sfx`. If that
location already contains a skill with this name, choose whether to replace it
before copying. For Codex, the default location is `~/.codex/skills/fun-sfx`;
use `$CODEX_HOME/skills/fun-sfx` when CODEX_HOME is customized.

For other agents, follow that agent's skill installation mechanism or point it
directly at this project's `SKILL.md`. The workflow does not require a particular
video editor, hosted API, or account.

Example requests:

> Use $fun-sfx to find a short whoosh for the transition at 00:04.2.

> Use $fun-sfx to suggest three reaction sounds for this edit, then prepare the one I pick.

> Use $fun-sfx to add a subtle impact on the reveal without obscuring dialogue.

## Project layout

```text
fun-sfx/
  SKILL.md               Agent instructions
  agents/openai.yaml     Codex display metadata
  catalog.json           Complete machine-readable inventory
  assets/originals/      All 71 original recordings, renamed only
  assets/audio/          WAV audio from the two MP4s
  scripts/sfx.py         List, search, inspect, verify, and export
  scripts/build_catalog.py  Import into an empty pack
  scripts/render_catalog.py  Regenerate readable guides from catalog.json
  references/CATALOG.md Human-readable inventory
  references/USE_CASES.md Individual scene, timing, and example guidance
  references/editing.md Timing, cue sheets, and mixing recipes
  LICENSE               MIT for code and documentation
  ASSET_LICENSE.md      Recording rights and provenance
```

## Contribute or publish

Code and documentation contributions use MIT. For recording contributions,
include the source URL, author, explicit redistribution license, and required
attribution. Preserve provenance and avoid re-encoding originals unnecessarily.

The importer scans a source folder recursively, creates collision-safe IDs,
copies all supported media, extracts MP4/WebM audio, and generates both catalogs.
It refuses to overwrite an existing catalog or asset pack. To build a new pack,
copy the code into an empty project without `catalog.json` or existing assets,
then run `python3 scripts/build_catalog.py /path/to/source-sounds`.
It does not establish recording licenses or merge into an existing collection.

To maintain existing guidance, edit each recording's `usage` and `audio_review`
fields in `catalog.json`, then run `python3 scripts/render_catalog.py`. The JSON
is the source of truth for both readable guides. A new import produces technical
metadata and filename tags only; its individual editorial guidance must be added
separately. Diffusion Studio is not required to use this pack.

Before publishing this complete pack, clear recording rights or exclude the
recordings. Publishing the MIT code and documentation separately is supported;
users can import their own authorized recordings. No remote repository or public
release is created by the import tools.
