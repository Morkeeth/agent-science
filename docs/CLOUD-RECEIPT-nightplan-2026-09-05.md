# Cloud receipt — NIGHTPLAN 2026-09-05 · Lane A

**Branch:** `cursor/nightplan-research-engine-b1eb`  
**Baseline (plan):** `69cc6b12a802789ebb0cfac8951233c6218dfc3f`  
**HEAD at receipt write:** run `git rev-parse origin/cursor/nightplan-research-engine-b1eb` (do not trust a stale hardcoded SHA)  
**Session:** cloud agent · 2026-09-04/05 overnight

## Status

Lane A (autonomous investigation) + minimal CLI/MCP surface landed. Challenge is a new investigation against a pinned answer version. Interrupt/resume preserves evidence and does not re-issue completed discovery fingerprints.

## Commands (stranger / offline)

```bash
bash scripts/demo_research_challenge.sh
# → DEMO OK · kind=challenge · claim_states include CONTESTED

python3 scripts/eval_research_challenge_baseline.py
# → naive_contradict_assessments=0 · adaptive_contradict_assessments=1 · adaptive_wins=true

python3 -m pytest -q tests/test_research_run.py
# → 7 passed

agent-science research "…" --plan-only
agent-science research challenge CASE_ID --max-steps N
agent-science research resume RUN_ID
```

## Verified at object (commands run this session)

| Claim | Command | Result |
|-------|---------|--------|
| Challenge revises answer to CONTESTED | `bash scripts/demo_research_challenge.sh` | exit 0 · `claim_states=['CONTESTED']` |
| Adaptive beats naive baseline on contradicts | `python3 scripts/eval_research_challenge_baseline.py` | naive 0 · adaptive 1 · wins true |
| Challenge = new investigation vs pin | `python3 -m pytest -q tests/test_research_run.py::test_challenge_is_new_investigation_against_pinned_version` | passed |
| Follow-up query from prior source gap | `…::test_followup_query_comes_from_prior_source_gap` | passed |
| Interrupt/resume preserves evidence; skips completed discovery | `…::test_interrupt_resume_preserves_evidence_and_skips_completed_discovery` | passed |
| CLI + MCP entry | `…::test_cli_research_challenge_resume_exit_zero` · `…::test_mcp_science_research_challenge` | passed |

HEAD at verification time will be the commit that adds this receipt (see git log on the branch).

## What landed

- `clearance/research_run.py` — ResearchRun persistence, question map, adaptive loop, challenge, resume/cancel, synthesis with strongest challenge + falsification condition
- `clearance/research_cli.py` — `research start|challenge|resume|show|list|cancel` (+ shorthand `research "question"`)
- MCP `science_research` tool
- `scripts/demo_research_challenge.sh` — cold offline demo
- `scripts/eval_research_challenge_baseline.py` — naive vs adaptive arm
- `tests/test_research_run.py` — 7 executed controls
- README section + `full_gate.sh` includes the new suite

## Oscar-only leftovers (stop at the door)

- USE BAR: Oscar uses results in every websearch — cloud cannot claim
- Film / Devpost / key rotation / hosted redeploy with secrets
- Live Parallel/Perplexity field pass for six topic families (no keys on this VM; `parallel_configured=false`)
- Lane B study identity / structured conditions / claim-relationship modules (not started)
- Lane C followed-question store, update ranking, experiment protocols (not started)
- Frozen 18-question eval set execution with held-out acceptance (schema only implied; not run live)
- Public push of release candidate — Oscar reviews

## Known limits (honest)

- Local planner is not a model reasoner; without Gemini/Parallel, live discovery is unavailable
- Challenge auto-assesses `contradicts` only when an exact contrary cue appears in a snapshot quote/span
- Provider cost remains `unknown` unless a provider returns billing
- Demo seeds fixtures via test doubles; it proves the loop, not web quality
