# Receipt — ship night · 2026-09-02

## AS-SHIP-1 · Film rebuild · truth-layer video

**Branch:** `cursor/as-ship-film-2026-09-01`  
**Duration:** 107.0s (`ffprobe demo/demo-final.mp4`)  
**Builder:** Cloud agent · flipbook sibling absent → `film/render_local.py`

### Frame checks

| Check | Command | Result |
|-------|---------|--------|
| No SCOUT/documentary/insured @ 5s | `ffmpeg -ss 5 -i demo/demo-final.mp4 -frames:v 1 /tmp/f5.png` + `strings /tmp/f5.png \| grep -iE 'documentary\|scout\|insured'` | **PASS** — hook text only |
| Frame 0 hook | `ffmpeg -ss 0 -i demo/demo-final.mp4 -frames:v 1 /tmp/f0.png` | **PASS** — "Your agent websearches. You get one answer." |
| Visibility @ ~15s | `ffmpeg -ss 15 -i demo/demo-final.mp4 -frames:v 1 /tmp/f15.png` | **PASS** — `/visibility/ui` screenshot, pane 1b caption |
| CONTRARY @ 34s | `ffmpeg -ss 34 -i demo/demo-final.mp4 -frames:v 1 /tmp/f34.png` | **PASS** — CONTRARY TO RESEARCH stamp |

### SHIPPED

- `film/agent-science.json` — truth-layer scene spec (hook → visibility → CONTRARY → compound A=1→B=0)
- `film/render_local.py` — Pillow + ffmpeg local renderer (flipbook sibling repo absent in cloud VM)
- `film/voice_edge.py` — edge-tts fallback when Kokoro unavailable
- `film/build.sh` — auto-fallback to local render + edge-tts; syncs `film/voiceover.txt` → `demo/voiceover.txt`
- `film/preflight.sh` — health/visibility retry for flaky Cloud Run cold starts
- `docs/assets/screens/*.png` — refreshed hosted captures (8 screens)
- `demo/demo-final.mp4` — rebuilt truth-layer reel (107s)
- `submission/demo-final.mp4` — copied
- `docs/PITCH-TOMORROW.md` — compound numbers fixed to A=1→B=0 (was A=2→B=1 in 30s pitch)
- `scripts/capture_screens.py` — `domcontentloaded` wait (networkidle timed out)

### VERIFIED

```bash
./film/build.sh                                    # WROTE demo/demo-final.mp4 107.0s
./film/preflight.sh                                # PREFLIGHT PASS
ffprobe -v error -show_entries format=duration -of csv=p=0 demo/demo-final.mp4   # 107.000000
grep '1 Parallel on run A, 0 on run B' demo/voiceover.txt film/voiceover.txt     # match
grep 'Run A \*\*1\*\* Parallel' docs/PITCH-TOMORROW.md                           # A=1→B=0
ls -la submission/demo-final.mp4                   # present
```

### WRONG

- **Flipbook sibling repo** (`~/CODE/flipbook`) not present in cloud VM and not public on GitHub — used `render_local.py` fallback instead of `flipbook render`. Scene timing/cues are approximated from `lay_voice.py`, not audited by flipbook `audit`.
- **Voice quality** — Kokoro unavailable; edge-tts (`en-US-GuyNeural`) used. Different timbre from prior Kokoro reel.
- **Preflight flakiness** — `/health` and `/visibility/ui` intermittently timeout on cold start; added retries in `preflight.sh` (5×45s). First preflight runs failed before retry patch.
- **strings-based frame OCR** — banned-word check uses `strings` on PNG, not true OCR; visual inspection used for confirmation.
- **Hosted claim count** — voiceover says 265 claims; live `/truths/ui` may show higher (284 in PITCH). Not re-recorded tonight.
- **Outward acts not done** — no YouTube upload, no Devpost submit (Oscar only per constitution).
