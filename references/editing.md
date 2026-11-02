# Editing with FUN SFX

## Timing and selection

Use whooshes for motion, impacts for emphasis, interface sounds for on-screen
actions, and reactions for deliberate comedic beats. These are starting points;
the footage and the user's style determine the choice. Search by literal sound
or mood (`whoosh`, `awkward`, `success`, `sad`, `epic`) and audition first.

The catalog stores whole-file durations, not cue boundaries. Listen for leading
silence and line up the audible transient with the visual event. For a whoosh,
its lead-in may start before the cut. Long recordings can contain multiple cues.
Some assets contain dialogue, profanity, recognizable music, or jumpscares;
filename-derived tags are incomplete and are not content ratings.

Start effects quietly under speech, then adjust by ear. Short edge fades can
prevent clicks but may soften an impact's attack; use `--fade-ms 0` if needed.
Gain is a manual adjustment, not automatic loudness normalization or clipping
protection. Listen to the final mix at a sensible level and inspect its peaks.

## Reproducible cue sheet

Keep the sound ID and the source offset separate from placement on the video
timeline. For example, this is an editing plan, not an executable input file:

```json
{
  "video": "input.mp4",
  "cues": [
    {
      "id": "vine-boom-sound-effect-longer-verison-for-real",
      "source_start_seconds": 0.0,
      "duration_seconds": 0.8,
      "timeline_start_seconds": 2.5,
      "gain_db": -10,
      "purpose": "Emphasize the reaction close-up"
    }
  ]
}
```

## FFmpeg fallback

Prefer the user's existing editor when available. These examples assume an MP4
video with compatible video codec and a cue already exported as `cue.wav`.
They create a new file and refuse overwrites. Adapt paths and timing to the edit.

For a video **with an existing audio track**, delay the cue 2.5 seconds and mix
it with the original audio for the original audio track's duration:

```sh
ffmpeg -n -i input.mp4 -i cue.wav \
  -filter_complex "[1:a:0]adelay=2500:all=1[sfx];[0:a:0][sfx]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95:level=0:latency=1[mix]" \
  -map 0:v:0 -map "[mix]" -c:v copy -c:a aac -b:a 192k output.mp4
```

For a **silent video**, add the delayed cue and pad it so the audio lasts through
the video. `-shortest` ends the padded audio at the end of the video:

```sh
ffmpeg -n -i silent.mp4 -i cue.wav \
  -filter_complex "[1:a:0]adelay=2500:all=1,apad[mix]" \
  -map 0:v:0 -map "[mix]" -c:v copy -c:a aac -b:a 192k -shortest output.mp4
```

The examples select the first video and audio tracks; preserve other tracks,
subtitles, or metadata if the user's project needs them. For many cues, use
separate input labels and delays, then one mix. Verify the output duration,
dialogue clarity, sync, clipping, and unintended tail truncation.

## Catalog fields

`catalog.json` schema version 1 stores a `sounds` array. Each record has a stable
filename-derived `id`, original filename, title, category, tags, and portable
paths relative to the skill root. `original` and `audio` hold duration in seconds,
codec, sample rate, channels, and bytes. Hashes use SHA-256. MP4 originals point
to a separate extracted WAV through `audio_path`; MP3s are used directly without
re-encoding. Discovery commands add absolute paths for the current installation.

`license_status`, `license`, `author`, and `source_url` track provenance. Every
supplied recording currently has unverified rights. Update these fields only
from actual evidence; derivative WAVs inherit the underlying recording's rights.

