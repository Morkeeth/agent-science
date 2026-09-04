# Cloud receipt — NIGHTPLAN 2026-09-05c · Lane C

**Branch:** `cursor/nightplan-lane-c-daily-e6e2`  
**Base:** `cursor/nightplan-research-engine-b1eb` @ `f5508932ed8df0023bf5e31512aef3981d672bf6`  
**HEAD at receipt write:** `70735abea704b8af76d15645601d8f1683db92d5` (re-check with `git rev-parse HEAD`)  
**Session:** cloud agent · 2026-09-04/05 overnight · Lane C

## Status

Lane C daily surface landed: followed questions, explicit ranked update runs, versioned experiment protocols, first-use docs. Signature line retained: **What would change this answer?** Did not edit Lane B `study.py` or claim-graph insides of `research_run.py`.

## Commands (stranger / offline)

```bash
bash scripts/demo_research_day_two.sh
# → DEMO OK · material=1 · top=decision_review_required · quiet_empty=True
#    · observation protocol status=planned
#    · code_protocol status=linked · experiment valid=True

bash scripts/demo_research_challenge.sh
# → DEMO OK · kind=challenge · CONTESTED (Lane A still green)

python3 scripts/eval_updates_ranking_baseline.py
# → ranked_wins_vs_naive_and_null=True · ranked FP=0 · naive FP=1 · silent TP=0

python3 -m pytest -q tests/test_research_follow.py
# → 9 passed

# First-use map
# docs/FIRST-USE-RESEARCH.md
```

## Verified at object (commands run this session)

| Claim | Command | Result |
|-------|---------|--------|
| Follow + ranked updates + experiment-plan tests | `python3 -m pytest -q tests/test_research_follow.py` | **9 passed** exit 0 |
| Lane A still green | `python3 -m pytest -q tests/test_research_run.py` | **7 passed** (16 total with follow) exit 0 |
| Day-two change report (fixture) | `bash scripts/demo_research_day_two.sh` | exit **0** · `material=1` · `quiet_empty=True` · observation `planned` · code_change `linked` + `valid=True` |
| Challenge demo still works | `bash scripts/demo_research_challenge.sh` | exit **0** · `claim_states=['CONTESTED']` |
| Ranked beats naive + null | `PYTHONPATH=. python3 scripts/eval_updates_ranking_baseline.py` | exit **0** · ranked FP **0** · naive FP **1** · silent TP **0** · equal TP **2** vs naive |
| Plan cannot be renamed to result | `…::test_experiment_plan_is_not_a_result` | passed · `mark_as_result` raises |
| CLI help exposes commands | `python3 -m clearance research follow\|updates\|experiment-plan --help` | exit 0 |

## What landed

- `clearance/follow.py` — followed-question store; `checked_online` only after live fetches
- `clearance/updates.py` — explicit update runs; effect-ranked change reports; meaningful empty
- `clearance/experiment_protocol.py` — versioned protocols; execute links measured experiment; refuse plan→result rename
- Thin CLI/MCP edges — `research follow|unfollow|updates|experiment-plan` · MCP `science_research` actions
- `scripts/demo_research_day_two.sh` · `scripts/eval_updates_ranking_baseline.py`
- `docs/FIRST-USE-RESEARCH.md` · README command map · `full_gate.sh` includes follow suite
- `tests/test_research_follow.py` — 9 executed controls

## Oscar-only leftovers (stop at the door)

- USE BAR — cloud cannot claim
- Film / Devpost / key rotation / hosted redeploy with secrets
- Live Parallel/Perplexity field pass (no keys on this VM)
- Public push of release candidate — Oscar reviews
- Aggregated `NIGHTRUN-2026-09-05.md` closeout after lanes merge

## Known limits (honest)

- Offline fixtures prove the day-two loop, not web quality
- `checked_online` requires `--live` plus actual `new_fetches`; snapshot reuse never claims online
- Observation/manual protocols remain `planned` until a real runner exists
- Ranked arm beats naive on this four-fixture precision check only — not a general superiority claim
- MCP `experiment-plan` execute still requires a local trusted acceptance script; agents cannot choose arbitrary code
