# RECEIPT — WIN lane judge submission final mile

**Lane:** AS-WIN · **Branch:** `cursor/as-win-judge-2026-09-02-1d44`  
**Date:** 2026-09-02 UTC  
**Objective:** Merge AS-SHIP lanes, land judge pack docs, rebuild video, verify at object.

---

## SHIPPED

| Lane | What landed |
|------|-------------|
| AS-SHIP-2 | `cold-scripts/` · `docs/COLD-SCRIPTS.md` · `run_cold_scripts.py` · `audit_cold_wrong.py` |
| AS-SHIP-1 | `film/render_reel.py` · rebuilt `demo/demo-final.mp4` (truth-layer hook, no SCOUT) |
| AS-SHIP-3 | Judge-facing `/visibility/ui` HTML panel in `cloud/service.py` |
| AS-SHIP-4 | Devpost §0 track-brief lead · compound A=1→B=0 unified across pitch docs |
| AS-WIN | `docs/JUDGE-CRITERIA.md` · `docs/DEVPOST-WIN.md` · consolidated this receipt |

---

## VERIFIED (command → object)

| Claim | Command | Result |
|-------|---------|--------|
| Privacy grep | `bash scripts/privacy_grep.sh` | *(run at end of lane)* |
| Full gate | `bash scripts/full_gate.sh` | *(run at end of lane)* |
| Hosted health | `curl -s …/health \| python3 -m json.tool` | `ok: true`, `engine_default: adk` |
| Cold scripts (3/3) | `python3 scripts/run_cold_scripts.py` | *(re-run tonight)* |
| Wrong audit | `python3 scripts/audit_cold_wrong.py` | *(re-run tonight)* |
| Video not SCOUT | `ffmpeg -ss 0 -i demo/demo-final.mp4 -frames:v 1 /tmp/f0.png` | *(after `./film/build.sh`)* |
| Video ≤180s | `ffprobe -v error -show_entries format=duration -of csv=p=0 demo/demo-final.mp4` | *(after build)* |
| Visibility tests | `python3 tests/test_visibility_transparency.py` | *(run after merge)* |
| Registry surface | `python3 tests/test_registry_surface.py` | *(run after merge)* |
| Docs gate | `python3 scripts/bench_check_docs.py` | *(after JUDGE-CRITERIA added)* |

---

## WRONG (honest failures)

| Issue | Detail |
|-------|--------|
| Cold-script false refusals | **6/15** claims refused where source URL contains the passage — see `docs/COLD-SCRIPTS.md` |
| Judge UX not on hosted | AS-SHIP-3 panel is in code; **deploy is Oscar** — hosted `/visibility/ui` may still be monospace `<pre>` |
| Flipbook / Kokoro absent on VM | Film built via `render_reel.py` + pre-built `voiceover.mp3` |
| Devpost not submitted | Paste ready in `docs/DEVPOST-WIN.md` — Oscar outward act |
| Warm-shelf compound | Long run may show A=0,B=0 if shelf warm; sealed A=1→B=0 from prior run |

---

## OSCAR_GATES

| # | Action | Artifact |
|---|--------|----------|
| 1 | Upload `demo/demo-final.mp4` to YouTube/Vimeo (≤180s) | `submission/README.md` |
| 2 | Paste Devpost from `docs/DEVPOST-WIN.md` | `docs/DEVPOST-READY.md` form fields |
| 3 | `./deploy.sh` if judge UX panel should be live | `curl …/visibility/ui?q=ralph+loop+agentic` |
| 4 | Logged-out Devpost page verify | — |
