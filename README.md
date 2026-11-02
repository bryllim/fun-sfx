# FUN SFX

Sound effects for videos edited with agents.

A portable resource collection for agent-assisted video editing.
Code and documentation are MIT licensed. Recording rights are unverified;
recordings are excluded from MIT. See [ASSET_LICENSE.md](ASSET_LICENSE.md).

## Collection

The pack includes all 71 supplied recordings under `assets/originals/`.
Original bytes are preserved with portable filenames. Audio from the two MP4s
is also available as stereo 48 kHz WAV under `assets/audio/`.

## Tools

Use Python 3.10+ to search or verify the catalog. Export also needs FFmpeg.

```sh
python3 scripts/sfx.py search whoosh
python3 scripts/sfx.py show tape-rewind-sound-effect
python3 scripts/sfx.py export tape-rewind-sound-effect output/rewind.wav --duration 0.5
python3 scripts/sfx.py verify
```

`catalog.json` stores file paths, duration, format, tags, and checksums.
The importer builds a new pack from a source folder without overwriting an
existing collection. The renderer regenerates readable catalog documents.

## Agent skill

Keep this folder together and copy it to your agent's skills directory as
`fun-sfx`. In Codex, use `~/.codex/skills/fun-sfx` or the skills directory in
your customized CODEX_HOME. Read `SKILL.md` for discovery and editing guidance.
See `references/editing.md` for cue-sheet fields and video mixing recipes.
