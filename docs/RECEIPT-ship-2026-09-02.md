# Receipt — ship night 2026-09-02

## AS-SHIP-1 · Film rebuild · truth-layer video

**Branch:** `cursor/as-ship-film-2026-09-01`  
**Built:** 2026-09-01 UTC  
**Duration:** 103.56s (≤180s cap)

### Frame checks

| Check | Command | Result |
|-------|---------|--------|
| SCOUT bug confirmed (before) | `ffmpeg -ss 5 -i demo/demo-final.mp4 -frames:v 1 /tmp/before.png` (pre-rebuild) | Frame showed "SCOUT" + "documentary" + "insured" |
| Frame 0 hook | `ffmpeg -ss 0 -i demo/demo-final.mp4 -frames:v 1 /tmp/f0-new.png` | "Your agent websearches. You get one answer." — no SCOUT |
| Frame 5 clean | `ffmpeg -ss 5 -i demo/demo-final.mp4 -frames:v 1 /tmp/f5v2.png` | Same hook card; sha256 differs from `/tmp/before.png` |
| ~15s visibility | `ffmpeg -ss 15 -i demo/demo-final.mp4 -frames:v 1 /tmp/f15v2.png` | `/visibility/ui` screenshot; CONTRARY_TO_RESEARCH in pane |
| ~22s CONTRARY | `ffmpeg -ss 22 -i demo/demo-final.mp4 -frames:v 1 /tmp/f22v2.png` | CONTRARY TO RESEARCH stamp overlay |
| Duration cap | `ffprobe -v error -show_entries format=duration -of csv=p=0 demo/demo-final.mp4` | `103.560000` |
| Preflight | `./film/preflight.sh` | **PREFLIGHT PASS** |
| Submission copy | `cmp demo/demo-final.mp4 submission/demo-final.mp4` | identical |

### Compound numbers

| Source | A → B | Command |
|--------|-------|---------|
| `docs/SEALED-PREDICTION-2026-08-31.md` | 1 → 0 | `grep parallel_api_calls docs/SEALED-PREDICTION-2026-08-31.md` |
| `demo/voiceover.txt` | one Parallel / zero Parallel | `grep -n Parallel demo/voiceover.txt` |
| `docs/PITCH-TOMORROW.md` | **1 → 0** (fixed from 2→1) | `grep -n 'Run A' docs/PITCH-TOMORROW.md` |
| `film/numbers.env` | PARALLEL_A=1 PARALLEL_B=0 | `source film/numbers.env && echo $PARALLEL_A $PARALLEL_B` |

### SHIPPED

- `film/render_reel.py` — HTML + screenshot reel fallback when flipbook sibling repo absent
- `film/build.sh` — uses `render_reel.py` fallback; muxes existing `demo/voiceover.mp3` when Kokoro absent
- `film/preflight.sh` — 90s curl retries for flaky Cloud Run cold starts
- Rebuilt `demo/demo-final.mp4` and `submission/demo-final.mp4` — truth-layer hook, visibility @15s, CONTRARY @22s
- `docs/PITCH-TOMORROW.md` — compound proof aligned to sealed A=1→B=0

### WRONG

- **Flipbook sibling repo absent** on cloud VM (`~/CODE/flipbook`); built via `render_reel.py` instead of `flipbook/examples/agent-science.json`. Oscar's machine with flipbook may produce a different pixel layout — re-run `./film/build.sh` there if flipbook is preferred.
- **Kokoro voice-generation absent**; reused pre-built `demo/voiceover.mp3` (truth-layer script already correct). Re-voicing requires `~/CODE/voice-generation`.
- **`scripts/capture_screens.py` timed out** on first `networkidle` pass; reel used existing `docs/assets/screens/*.png`. Fresh screens not re-captured this run.
- **Preflight hosted checks are flaky** without retries — Cloud Run returned 0 bytes / 45–90s timeouts on several attempts before PASS on retry-enabled run.
- **No OCR binary** in VM for automated "documentary/SCOUT/insured" string grep on PNGs; frame checks verified by extracted PNG inspection + hash diff vs pre-rebuild frame.
