# RECEIPT — AS-SHIP-4 submit pack + gate + receipt

**Lane:** AS-SHIP-4 · **Branch:** `cursor/as-ship-4-submit-pack-96b0` · **Date:** 2026-09-02 UTC  
**Objective:** Freeze Devpost submission pack, fix number contradictions, run full gate, write ship receipt.

---

## SHIPPED

| Item | What changed |
|------|----------------|
| Devpost paste §0 | `docs/SUBMISSION-PACK-2026-08-29.md` — paragraph 1 now leads with **M&E fact-check / E&O track brief**, then truth-layer pivot, constraint, clearance-as-vertical |
| Compound numbers | Unified to **A=1 → B=0** in `PITCH.md`, `docs/PITCH-TOMORROW.md`, `SUBMISSION-PACK` §3 controls row, `docs/VIDEO-SCRIPT-2026-08-29.md` |
| `docs/DEVPOST-READY.md` | Inspiration block updated with track-brief-first lead |
| `SUBMISSION.md` | Video checklist → **✅ built · Oscar uploads** (`demo/demo-final.mp4`, 2.6 MB) |
| `docs/STATUS.md` | Phase 6/7 gates honest — video built, Devpost paste ready, submit still Oscar |
| `hack.md` | NOW slice AS-SHIP-4 · track-brief checkbox checked · full gate checkbox checked |
| This receipt | `docs/RECEIPT-ship-2026-09-02.md` |

**Not touched (per lane contract):** `demo/demo-final.mp4` · `docs/COLD-SCRIPTS.md` · outward acts

---

## VERIFIED (commands + output)

| Claim | Command | Output |
|-------|---------|--------|
| Full gate | `bash scripts/full_gate.sh` | `=== FULL GATE OK === 2026-09-01T20:24:08Z` · EXIT:0 |
| Privacy grep | `bash scripts/privacy_grep.sh` | `PRIVACY OK: 0 hits` |
| Pitch docs no A=2 | `rg 'A=2\|2 Parallel' docs/ PITCH.md SUBMISSION.md README.md` | **0 hits** (exit 1) |
| Docs gate | `python3 scripts/bench_check_docs.py` | `ALL 127/127 match SUBMISSION-PACK` |
| Video artifact | `ls -la demo/demo-final.mp4` | `-rw-r--r-- 2597670 bytes` |
| Hosted health | `curl -s …/health \| python3 -m json.tool` | `ok: true`, `engine_default: adk` |
| Long run compound | inside `full_gate.sh` step 7 | `passed=19 failed=0` · Run B `corpus_hits=1` |
| Stranger trial | inside `full_gate.sh` step 8 | `=== Trial OK ===` |
| Devpost §0 track brief | `head -90 docs/SUBMISSION-PACK-2026-08-29.md` | §0 title `TRACK BRIEF (lead with this)` |

---

## WRONG (honest failures)

| Issue | Detail |
|-------|--------|
| First full_gate attempt | Transient `JSONDecodeError` on `/health` during tmux run at 20:21Z — **failed before completion**. Re-run at 20:24Z passed. |
| Warm-shelf compound on this gate run | Long run subject `longrun-0901-2024` showed **A=0, B=0** Parallel (shelf already warm). Sealed prediction **A=1→B=0** is from prior run `longrun-0831-1320` — not re-measured tonight. |
| Video not verified at object | `demo/demo-final.mp4` exists (2.6 MB) but **duration/content not ffprobed** this lane — AS-SHIP-1 owns the file; we only confirmed presence + size. |
| Devpost not submitted | Paste block ready; **no logged-out Devpost page verify** — Oscar outward act. |
| Historical receipts still cite 2→1 | `docs/RECEIPT-live-compound-exhibit-2026-08-31.md`, `docs/BLOCKED-live-compound-exhibit-2026-08-30.md` — left as historical; not pitch-facing. |
| Elevator pitch in DEVPOST-READY form table | Still truth-layer lead (short field); full paste block §0 is authoritative for Devpost description. |

---

## OSCAR_GATES (upload video, Devpost, deploy if UX lane landed)

| # | Action | Artifact |
|---|--------|----------|
| 1 | Upload `demo/demo-final.mp4` to YouTube/Vimeo (≤180s) | `submission/README.md` |
| 2 | Paste Devpost description from `docs/SUBMISSION-PACK-2026-08-29.md` §0 (BEGIN/END block) | `docs/DEVPOST-READY.md` form fields |
| 3 | Fill video URL on Devpost + verify logged-out page plays | — |
| 4 | Note Devpost submission URL in `docs/STATUS.md` session log | — |

**Deploy:** not required this lane — hosted URL live at `agent-science-00018-n4s`.

---

## MERGE-READY PR SUMMARY

**Branch:** `cursor/as-ship-4-submit-pack-96b0` → `main`

**Files changed (docs only):**
- `docs/SUBMISSION-PACK-2026-08-29.md` — §0 track-brief lead, §3 compound row
- `docs/DEVPOST-READY.md` — inspiration lead
- `docs/STATUS.md` — phase 6/7 honest + gate stamp
- `docs/PITCH-TOMORROW.md` — compound proof numbers
- `docs/VIDEO-SCRIPT-2026-08-29.md` — hosted vs offline compound note
- `PITCH.md` — compound proof line
- `SUBMISSION.md` — video built status
- `hack.md` — NOW slice + track-brief checkbox
- `docs/RECEIPT-ship-2026-09-02.md` — this file

**Conflicts to resolve in IDE (if merging parallel lanes):**
- `hack.md` NOW section — other lanes may have appended slices
- `docs/STATUS.md` session log — append-only
- `docs/SUBMISSION-PACK-2026-08-29.md` — check §0 if another lane edited paste block

**Gate before merge:** `bash scripts/full_gate.sh` → FULL GATE OK
