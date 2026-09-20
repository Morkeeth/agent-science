# RECEIPT — Partner call-proof honesty night · 2026-09-20

**Branch:** `cursor/partner-integrations-night-6950`  
**Slice:** Partner admissibility — callable health (not env presence), call-proof script,
PeriodCheck baseline, live RED watch. Deploy remains Oscar.

## Shipped

| Item | Object |
|------|--------|
| Gemini health honesty | `cloud/partners.py` `resolve_gemini_path` requires token/API key |
| `gemini_configured` + receipt fields on `/health` | `verified_search_id`, `verified_calls_logged`, `last_verified_utc` |
| Checklist not hardcoded Parallel | `track_checklist.parallel_search_at_runtime` ← key presence |
| RED control | `t_gemini_project_env_alone_is_not_callable` |
| Call-proof prove | `python3 scripts/prove_partner_calls_local.py` |
| Live RED watch | `bash scripts/watch_hosted_partner_health.sh` (`EXPECT_STATE=red`) |
| PeriodCheck baseline | `docs/BASELINE-periodcheck-partner-proof-2026-09-20.md` |
| Finding | `docs/FINDING-gemini-health-env-alone-2026-09-20.md` |

## Commands run (done-when)

```text
python3 tests/test_watch_it_go_red.py                 → 72 passed, 0 failed
python3 tests/test_adk_default_path.py                → 5/5 passed
python3 tests/test_partner_runtime.py                 → 9/9 passed
python3 -m unittest tests.test_hosted_flow -v         → OK
bash scripts/prove_partner_health_local.sh            → PROVE_PARTNER_HEALTH_LOCAL OK
python3 scripts/prove_partner_calls_local.py          → PROVE_PARTNER_CALLS_LOCAL OK
bash scripts/watch_hosted_partner_health.sh           → WATCH RED OK (00028-hed)
python3 scripts/bench_check_docs.py                   → (after pack update)
python3 scripts/eval_refusal_baseline.py              → baseline 5/6 · shipping 6/6 · delta +1
python3 scripts/eval_refusal_ablation.py              → ablation 5/6 · shipping 6/6 · delta +1
```

## Live still RED / BLOCKED

- Hosted `/health` partner fields — until Oscar `deploy.sh`
- Live Parallel / compound — no `PARALLEL_API_KEY` / `WORKSPACE_TOKEN` on this VM
- Key rotation — Oscar (`AS-KEYS-ROTATE`)
