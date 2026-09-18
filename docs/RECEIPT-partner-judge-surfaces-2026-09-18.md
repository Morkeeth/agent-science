# RECEIPT — Partner + judge-surface night · 2026-09-18

**Branch:** `cursor/partner-admissibility-night-5719`  
**Slice:** Open live objects; fix hardcoded Parallel checklist; restore public
judge/film surfaces on WorkspaceHTTP; baseline-eval that can embarrass live;
refresh STATUS / SUBMISSION-PACK at object.

## Embarrassing findings (kept)

1. Live `/health` on `00028-hed` still stripped — naive `ok:true` PASS, shipping
   partner fields FAIL (`python3 scripts/eval_hosted_partner_baseline.py` exit 2).
2. `track_checklist.parallel_search_at_runtime` was **hardcoded True** with no key
   and no receipts — `docs/FINDING-partners-checklist-hardcoded-2026-09-18.md`.
3. `/truths/ui` + `/visibility/ui` → live **303**; even authed local → **404**
   (unmounted) — `docs/FINDING-hosted-judge-surfaces-missing-2026-09-18.md`.
4. `docs/STATUS.md` still claimed revision `00018-n4s` + `engine_default: adk`
   on live — corrected tonight against curl.

## Shipped in tree

| Item | Object |
|------|--------|
| Checklist measured | `cloud/partners.py` — runtime from key; `parallel_search_proven` from receipts |
| Public judge surfaces | `cloud/case_http.py` — truths / visibility / popular |
| Baseline eval | `scripts/eval_hosted_partner_baseline.py` |
| Local film prove | `scripts/prove_judge_surfaces_local.sh` |
| Controls | partner_runtime **8/8** · hosted_flow judge + checklist RED tests |
| Docs | STATUS · SUBMISSION-PACK 129 · partner doc · design-partner · findings |

## Commands run (done-when)

```text
python3 tests/test_watch_it_go_red.py                 → 72 passed, 0 failed
python3 tests/test_partner_runtime.py                 → 8/8 passed
python3 tests/test_adk_default_path.py                → 5/5
python3 -m unittest tests.test_hosted_flow -v         → OK (incl. new film + RED tests)
bash scripts/prove_partner_health_local.sh            → PROVE_PARTNER_HEALTH_LOCAL OK
bash scripts/prove_judge_surfaces_local.sh            → PROVE_JUDGE_SURFACES_LOCAL OK
python3 scripts/eval_hosted_partner_baseline.py       → exit 2 · naive PASS / shipping FAIL
python3 scripts/bench_check_docs.py                   → 129/129 match
python3 scripts/eval_refusal_baseline.py              → baseline 5/6 · shipping 6/6 · delta +1
python3 scripts/eval_refusal_ablation.py              → ablation 5/6 · shipping 6/6 · delta +1
curl -sS …/health                                     → revision 00028-hed stripped
```

## Still RED / Oscar

- Live URL until `deploy.sh` — health stripped · partners 303 · film 303
- Live `/clear` compound — no `PARALLEL_API_KEY` / `WORKSPACE_TOKEN` on this VM
- Key rotation — Oscar console (`AS-KEYS-ROTATE`)
- Film preflight on live — fails until deploy (correct control behaviour)
