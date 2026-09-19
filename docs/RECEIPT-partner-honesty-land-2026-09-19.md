# RECEIPT — Partner honesty land on main · 2026-09-19

**Branch:** `cursor/partner-honesty-baseline-ab9b`  
**Commit tip:** `bc4ba68` (lands `eb6d425`+ onto main path; expands baseline H1–H6)  
**Origin:** cherry-picked unmerged `cursor/partner-admissibility-night-5719` (`eb6d425`+) onto `main`, then expanded the live baseline eval.  
**Slice:** Land checklist honesty + judge film surfaces that never reached `main`; re-measure at live objects; expand naive-vs-shipping baseline to `/partners` and `/truths/ui`.

## Why this night (bigger object)

`main` still had `parallel_search_at_runtime: True` hardcoded and no public
WorkspaceHTTP film routes. The Sep 18 fix lived only on
`origin/cursor/partner-admissibility-night-5719` — nearer docs claimed the
work was done; the object (`git merge-base --is-ancestor eb6d425 main` → false)
said otherwise.

## Embarrassing findings (re-derived 2026-09-19)

1. Live `/health` on `agent-science-00028-hed` still stripped — only
   `ok/service/mode/revision`.
2. Live `/partners`, `/truths/ui`, `/visibility/ui`, `/popular/ui` → **303**.
3. Expanded baseline: **naive 3/3 · shipping 0/3** (exit 2).
4. After land: no-key checklist correctly reports
   `parallel_search_at_runtime: false` (was True on main before this branch).

## Shipped in tree

| Item | Object |
|------|--------|
| Checklist measured | `cloud/partners.py` |
| Public judge surfaces | `cloud/case_http.py` — truths / visibility / popular |
| Expanded baseline | `scripts/eval_hosted_partner_baseline.py` — H1–H6 |
| Local proves | `prove_partner_health_local.sh` · `prove_judge_surfaces_local.sh` |
| Controls | partner_runtime **8/8** · hosted_flow 17 OK |

## Commands run (done-when)

```text
git pull origin main
python3 tests/test_watch_it_go_red.py                 → 72 passed, 0 failed
python3 tests/test_partner_runtime.py                 → 8/8 passed
python3 tests/test_adk_default_path.py                → 5/5
python3 -m unittest tests.test_hosted_flow -v         → Ran 17 tests · OK
bash scripts/prove_partner_health_local.sh            → PROVE_PARTNER_HEALTH_LOCAL OK
                                                   · engine_default=adk · parallel_sdk=true (after pip parallel-web==1.3.2)
bash scripts/prove_judge_surfaces_local.sh            → PROVE_JUDGE_SURFACES_LOCAL OK
python3 scripts/eval_hosted_partner_baseline.py       → exit 2 · naive 3/3 / shipping 0/3
python3 scripts/eval_hosted_partner_baseline.py --offline-fixtures → OFFLINE FIXTURES OK
python3 scripts/bench_check_docs.py                   → 129/129 match
bash scripts/verify_cold_clone.sh                     → cold-clone verify OK (steps 1–12)
python3 scripts/eval_refusal_baseline.py              → baseline 5/6=0.833 · shipping 6/6=1.000 · delta +1
python3 scripts/eval_refusal_ablation.py              → ablation 5/6 · shipping 6/6 · delta +1
curl -sS …/health                                     → revision 00028-hed stripped
curl -sS -o /dev/null -w '%{http_code}' …/partners    → 303
curl -sS -o /dev/null -w '%{http_code}' …/truths/ui   → 303
```

## Still RED / Oscar

- Live URL until `bash deploy.sh` — health stripped · partners/film 303
- Live `/clear` compound — no `PARALLEL_API_KEY` / `WORKSPACE_TOKEN` on this VM
- Key rotation — Oscar console (`AS-KEYS-ROTATE`)
- Do **not** claim hosted partners green until
  `bash scripts/verify_partners_hosted.sh` exits 0 (or 2 with token-only clear blocked)
