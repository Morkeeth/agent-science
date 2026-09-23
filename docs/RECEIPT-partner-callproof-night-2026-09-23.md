# RECEIPT — Partner call-proof + judge surfaces night · 2026-09-23

**Branch:** `cursor/partner-callproof-honesty-c0b0` · tip `053ac58`  
**Slice:** Callable Gemini health ≠ env presence; Parallel checklist from key; PeriodCheck
baseline re-opened; public judge film surfaces on WorkspaceHTTP; naive baseline that
beats shipping on live.

## Embarrassing findings (kept)

1. **Live naive beats shipping** — `python3 scripts/eval_hosted_partner_baseline.py`
   → naive **3/3**, shipping **0/3**, exit 2 on `agent-science-00028-hed`.
2. **`gemini: true` from `GCP_PROJECT` alone** (pre-fix) — no ADC token —
   `docs/FINDING-gemini-health-env-alone-2026-09-20.md` (reproduced tonight before land).
3. **Film surfaces 303** on live — `/truths/ui`, `/visibility/ui` — not merely auth-gated;
   WorkspaceHTTP never mounted them (`docs/FINDING-hosted-judge-surfaces-missing-2026-09-18.md`).
4. **PeriodCheck `/api/health` → 500** tonight while their `live-evaluation.json` still
   carries Parallel `search_id`s — they win published call proof; we win local call-proof
   + compound wedge only after deploy.

## Shipped in tree

| Item | Object |
|------|--------|
| Callable `resolve_gemini_path` + `gemini_configured` | `cloud/partners.py` |
| Receipt-backed `/health` Parallel fields | `verified_search_id` / `verified_calls_logged` |
| Checklist from key, not `True` | `track_checklist.parallel_search_at_runtime` |
| Call-proof script | `python3 scripts/prove_partner_calls_local.py` |
| Hosted RED watch | `bash scripts/watch_hosted_partner_health.sh` |
| Public judge surfaces | `cloud/case_http.py` `_public_judge_get` |
| Local film prove | `bash scripts/prove_judge_surfaces_local.sh` |
| Naive vs shipping baseline | `python3 scripts/eval_hosted_partner_baseline.py` |
| PeriodCheck baseline re-derived | `docs/BASELINE-periodcheck-partner-proof-2026-09-20.md` |
| SUBMISSION honesty | hosted partners **RED** until deploy |

## Commands run (done-when)

```text
python3 tests/test_watch_it_go_red.py                 → 72 passed, 0 failed
python3 tests/test_adk_default_path.py                → 5/5
python3 tests/test_partner_runtime.py                 → 9/9
python3 -m unittest tests.test_hosted_flow -v         → includes judge surfaces + checklist RED
bash scripts/prove_partner_health_local.sh            → PROVE_PARTNER_HEALTH_LOCAL OK
python3 scripts/prove_partner_calls_local.py          → PROVE_PARTNER_CALLS_LOCAL OK
bash scripts/prove_judge_surfaces_local.sh            → PROVE_JUDGE_SURFACES_LOCAL OK
bash scripts/watch_hosted_partner_health.sh           → WATCH RED OK
python3 scripts/eval_hosted_partner_baseline.py --offline-fixtures → OK
python3 scripts/eval_hosted_partner_baseline.py       → naive 3/3 · shipping 0/3 · exit 2
python3 scripts/bench_check_docs.py                   → (re-run after pack touch)
```

## Still RED / Oscar

- Live URL until `deploy.sh` — health stripped; partners/film 303
- Live `/clear` compound — no `PARALLEL_API_KEY` / `WORKSPACE_TOKEN` on this VM
- Key rotation — Oscar console (`AS-KEYS-ROTATE`)
