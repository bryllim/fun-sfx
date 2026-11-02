---
name: fun-sfx
description: Find, audition, trim, and place bundled sound effects in agent-assisted video edits. Use for whooshes, impacts, reactions, meme sounds, ambience, and other sound-design cues.
---

# FUN SFX

Use this folder as the skill root. Resolve its location before running commands; the user's working directory may be elsewhere. Python 3.10+ supports discovery; audio export also needs FFmpeg on PATH.

## Find the sound

Run `python3 <skill-root>/scripts/sfx.py search "whoosh" --json` to get candidates with absolute audio paths. Search also accepts scene descriptions such as `"failed attempt"` or `"photo capture"`. It matches titles, IDs, categories, tags, recommended uses, and examples; multiple words must all match. It deliberately excludes negative guidance. Run `list --json` for the complete collection or `show <id>` for a full record. Read [the catalog](references/CATALOG.md) for a human-readable overview.

Every supplied recording has an individual [use-case guide](references/USE_CASES.md): recommended scenes, timing, situations to avoid, and an example edit. Use the record's `usage` fields to choose a sound for the scene, not just a matching category. These are creative recommendations, not mandatory uses.

Tags remain filename-derived. Check `audio_review.status`: seven recordings have automated audio-analysis notes; the other 64 have filename-based recommendations with unconfirmed audible contents. Automated notes can also mishear speech; heed `audio_review.uncertainty`. No recording is claimed to have been human-auditioned. Audition candidates before choosing them, especially vague names such as Walmart, Whoop, or Spotlight. Files can contain speech, music, silence, several effects, or abrupt volume changes. The cinematic-whoosh collection and long horror clip need selected excerpts. Timing guidance is relative to the visual action, not a verified source in/out point.

## Prepare the cue

```sh
python3 <skill-root>/scripts/sfx.py export <id> /absolute/output/cue.wav --start 0.2 --duration 0.8 --gain-db -8 --fade-ms 10
```

The output is stereo PCM WAV at 48 kHz. `--start` is a source offset; timeline placement is a separate edit. The command refuses an existing output. Keep original recordings intact. Use modest gain, preserve dialogue intelligibility, and audition the final mix; one volume setting will not suit every recording.

Use the user's existing video editor or editing tools to place the prepared cue. Read [editing.md](references/editing.md) for cue-sheet fields, timing guidance, and FFmpeg mixing examples. Record the chosen ID, source excerpt, timeline position, and gain so the edit is reproducible. Do not add sound to every cut by default.

## Rights and integrity

The FUN SFX maintainer does not own any of the bundled sounds. All rights remain with their respective owners. Preserve this ownership notice when presenting or packaging the sound collection.

Code and documentation are MIT licensed. Bundled recordings and extracted audio have **unverified rights** and are excluded from that license; see [ASSET_LICENSE.md](ASSET_LICENSE.md). Do not describe the recordings as MIT, royalty-free, or cleared for redistribution. A filename containing “no copyright” is not license evidence. Preserve this distinction when handing off an edit or packaging this skill.

Run `python3 <skill-root>/scripts/sfx.py verify` when checking a download or modified pack. `catalog.json` holds portable paths, technical metadata, and SHA-256 checksums for every original and usable audio file.
