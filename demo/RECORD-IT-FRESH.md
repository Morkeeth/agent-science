# Record it fresh · Agent Science

## Option A — Pre-built (fastest)

```bash
cd agent-science   # after git clone
./film/build.sh
open demo/demo-final.mp4
```

Upload to YouTube/Vimeo. Paste URL in Devpost.

## Option B — Live screen record (stronger for judges)

1. **QuickTime** → New Screen Recording → microphone on
2. Open tabs from `demo/FILM-AND-SUBMIT.md`
3. Follow teleprompter table; **lead with /visibility/ui**
4. Export ≤180s; upload public

## Option C — Flipbook scout only (feedback, not submit)

Flipbook scout (optional sibling repo):

```bash
# Requires flipbook installed separately — see film/README.md
./film/build.sh
```

Scout reel ≠ Devpost unless you mux voice with `./film/build.sh`.

## Audio

- Pre-rendered: `demo/voiceover.mp3` (from `./film/build.sh`)
- Re-render one paragraph: run `./film/build.sh` (uses local Kokoro if installed) or re-run `python3 film/split_voice.py` then render parts per `film/README.md`

## Check before upload

```bash
./film/preflight.sh
ffprobe demo/demo-final.mp4
```
