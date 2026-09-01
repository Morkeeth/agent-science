# Ship receipt — AS-SHIP-4 · 2026-09-02

**Lane:** submit pack + gate + receipt  
**Branch:** `cursor/as-ship-4-submit-pack-837b`  
**Base:** `main` @ pull through `1729470`

---

## SHIPPED

- **Devpost §0 rewrite** — `docs/SUBMISSION-PACK-2026-08-29.md`: M&E fact-check / E&O lead → truth-layer pivot → hosted A=1→B=0 + `/visibility/ui` → refuse constraint → clearance as one vertical
- **Compound number sync** — pitch docs use hosted **A=1 → B=0**; offline anchor A=2→B=1 labeled explicitly where historical
- **`SUBMISSION.md`** — video row: ✅ built (98 s), Oscar uploads
- **`docs/STATUS.md`** — phase 6/7 honest: video built, Devpost paste ready, upload ⛔
- **`docs/DEVPOST-READY.md`** — §0 lead order note
- **`hack.md`** — NOW = AS-SHIP-4; track-brief-on-Devpost ¶1 checkbox checked
- **Files touched:** `PITCH.md`, `docs/PITCH-TOMORROW.md`, `docs/VIDEO-SCRIPT-2026-08-29.md`, submission pack, STATUS, DEVPOST-READY, hack.md

**Not shipped (Oscar outward):** video upload · Devpost submit · logged-out page verify · deploy

---

## VERIFIED (commands + output)

| Claim | Command | Output |
|-------|---------|--------|
| Full gate | `bash scripts/full_gate.sh` | `=== FULL GATE OK === 2026-09-01T20:18:19Z` · exit 0 |
| Privacy | `bash scripts/privacy_grep.sh` | `PRIVACY OK: 0 hits` |
| Docs gate | (in full_gate step 5) | `ALL 127/127 match SUBMISSION-PACK` |
| Long run | (in full_gate step 7) | `COMPOUND PASS` · subject `longrun-0901-2018` A parallel=0 B parallel=0 corpus_hits=1 |
| Stranger trial | (in full_gate step 8) | `=== Trial OK ===` |
| Video duration | `ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 demo/demo-final.mp4` | `98.000000` (≤180 s) |
| Pitch doc grep | `rg 'A=2|2 Parallel' docs/ PITCH.md SUBMISSION.md README.md` | Only offline-anchor mentions in SUBMISSION-PACK + VIDEO-SCRIPT (hosted lead is A=1→B=0) |
| Sealed compound (object) | `grep -E 'parallel_api_calls|1.*0' docs/SEALED-PREDICTION-2026-08-31.md` | Run A **1** · Run B **0** Parallel · corpus_hits **1** |

---

## WRONG (honest failures)

1. **Tonight's long run did not re-measure A=1→B=0** — `long_run_goal.sh` on warm shelf showed A=0, B=0 Parallel (valid per sealed doc when shelf is hot). Sealed A=1→B=0 remains from `longrun-0831-1320` (2026-08-31), not re-run cold this session.
2. **Video not verified on Devpost** — file exists at 98 s; no public URL; logged-out page unchecked (Oscar gate).
3. **Devpost not submitted** — paste block ready; form not filled.
4. **Hosted stats drift** — trial reported **303 claims**, hit rate **0.615**; STATUS still cites ~265 / ~0.80 until refreshed at object after deploy.
5. **Orphan-works full script Run B** — still **503/504** on hosted; do not claim on video (unchanged).
6. **Did not merge other lanes' branches** — this PR is docs-only on top of `main` post AS-SHIP-1 video land; no IDE conflict scan performed.

---

## OSCAR_GATES (upload video, Devpost, deploy if UX lane landed)

| Gate | Action | Artifact |
|------|--------|----------|
| Video upload | YouTube/Vimeo public ≤3 min | `demo/demo-final.mp4` → `submission/VIDEO-URL.txt` |
| Devpost | Paste `SUBMISSION-PACK` §0 lead + form fields from `DEVPOST-READY.md` | https://agentic-cinema.devpost.com/ |
| Logged-out verify | Video plays on live entry page | Screenshot → STATUS session log |
| Deploy | Only if UX lane needs it | `./deploy.sh` |

---

## Merge-ready PR summary

**Title:** AS-SHIP-4 — Devpost §0 track-brief lead, compound A=1→B=0 sync, full gate receipt

**Summary:** Freezes Devpost paste order (M&E/E&O → truth layer), fixes compound number contradictions in pitch docs, marks video as built (Oscar uploads), runs full gate + privacy grep, updates STATUS phase 6/7 honestly.

**Conflicts:** None expected with docs-only diff on current `main`. Do not merge AS-SHIP-1/2 lanes without Oscar review (`demo-final.mp4`, `COLD-SCRIPTS.md` owned elsewhere).
