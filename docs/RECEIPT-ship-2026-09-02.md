# RECEIPT — WIN lane judge submission final mile

**Lane:** AS-WIN · **Branch:** `cursor/as-win-judge-2026-09-02-1d44`  
**Date:** 2026-09-02 UTC  
**Objective:** Merge AS-SHIP lanes, land judge pack, rebuild video, verify at object.

---

## SHIPPED

| Lane | What landed |
|------|-------------|
| AS-SHIP-2 | `cold-scripts/` · `docs/COLD-SCRIPTS.md` · `run_cold_scripts.py` · `audit_cold_wrong.py` |
| AS-SHIP-1 | `film/render_reel.py` · `demo/demo-final.mp4` truth-layer hook (103.6s, no SCOUT) |
| AS-SHIP-3 | Judge-facing `/visibility/ui` HTML panel in `cloud/service.py` |
| AS-SHIP-4 | Devpost §0 track-brief lead · compound A=1→B=0 unified · 128/128 docs gate |
| AS-WIN | `docs/JUDGE-CRITERIA.md` · `docs/DEVPOST-WIN.md` · this receipt |

---

## VERIFIED (command → object)

| Claim | Command | Result |
|-------|---------|--------|
| Privacy grep | `bash scripts/privacy_grep.sh` | `PRIVACY OK: 0 hits` |
| Full gate | `bash scripts/full_gate.sh` | `=== FULL GATE OK === 2026-09-01T20:38:48Z` |
| Docs gate | `python3 scripts/bench_check_docs.py` | `ALL 128/128 match SUBMISSION-PACK` |
| Hosted health | `curl -s …/health \| python3 -m json.tool` | `ok: true`, `engine_default: adk` |
| Registry stats | `curl -s …/stats` | `n: 303`, `queries_logged: 239`, `hit_rate: 0.607` |
| Free tier | `curl -s '…/search?q=2012%2F28%2FEU&live=false'` | `label: SOURCED`, `cost_tier: free` |
| Video not SCOUT | `ffmpeg -ss 0 -i demo/demo-final.mp4 -frames:v 1 /tmp/f0.png` | truth-layer hook; no SCOUT in frame |
| Video ≤180s | `ffprobe … demo/demo-final.mp4` | `103.560000` |
| Visibility tests | `python3 tests/test_visibility_transparency.py` | **5/5** |
| Registry surface | `python3 tests/test_registry_surface.py` | **17/17** |
| Cold scripts (3/3) | `python3 scripts/run_cold_scripts.py` | 325.4s wall · 11 Parallel · 3/3 ok |
| Wrong audit | `python3 scripts/audit_cold_wrong.py` | `wrong_count=5` |
| Pitch docs no A=2 | `rg 'A=2\|2 Parallel' docs/ PITCH.md SUBMISSION.md README.md --glob '!docs/RECEIPT*'` | **0 hits** (exit 1) |
| Devpost ¶1 | `head -8 docs/DEVPOST-WIN.md` | track hook + truth layer |
| Long run compound | inside `full_gate.sh` step 7 | 19/19 · B `corpus_hits=1` · A=0 B=0 Parallel (warm shelf) |

---

## WRONG (honest failures)

| Issue | Detail |
|-------|--------|
| Cold-script false refusals | **5/15** claims refused where source URL contains passage — `python3 scripts/audit_cold_wrong.py` |
| Extraction non-determinism | Re-run changed script 1 (3→4 claims) and script 2 (4→3 claims) vs AS-SHIP-2 receipts |
| Judge UX not on hosted | Code merged; `curl …/visibility/ui \| grep -c '<pre>'` → **1** until `./deploy.sh` |
| Flipbook / Kokoro absent | Merged video from AS-SHIP-1; fresh `./film/build.sh` needs playwright on VM |
| Devpost not submitted | Paste in `docs/DEVPOST-WIN.md` — Oscar outward act |
| Warm-shelf compound | Long run A=0,B=0 Parallel; sealed A=1→B=0 from prior run `longrun-0831-1320` |

---

## OSCAR_GATES

| # | Action | Artifact |
|---|--------|----------|
| 1 | Upload `demo/demo-final.mp4` to YouTube/Vimeo (≤180s) | `submission/README.md` |
| 2 | Paste Devpost from `docs/DEVPOST-WIN.md` | `docs/DEVPOST-READY.md` |
| 3 | `./deploy.sh` — judge UX panel live | `curl …/visibility/ui?q=ralph+loop+agentic \| grep 'badge contrary'` |
| 4 | Logged-out Devpost page verify | — |
