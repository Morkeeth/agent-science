# RECEIPT — partner dual-surface restore · 2026-09-09

**Branch:** `cursor/partner-dual-surface-restore-57bd`  
**Object:** live hosted + local dual-surface fix  
**Deploy:** not run (Oscar only)

## What was true at start

```bash
curl -sS https://agent-science-568004190078.us-central1.run.app/health
# {"ok": true, "service": "agent-science", "mode": "private-workspaces",
#  "revision": "agent-science-00028-hed"}
bash scripts/verify_partners_hosted.sh
# AssertionError: gemini: expected True, got None
python3 tests/test_watch_it_go_red.py   # 72/72
```

Prior dual-surface commits (`90708f4`, `19cd462`, `9e4484d`) were **not** on `main`.

## Shipped on this branch

1. `cloud/partner_status.py` — shared health/partners payload + workspace path detection
2. `cloud/service.py` — dual-surface routing (public desk beside private `/cases`)
3. `cloud/case_http.py` — defense-in-depth `/health` still reports partners
4. `cloud/partners.py` — no hardcoded `parallel_search_at_runtime: True`
5. `deploy.sh` — dual-surface checklist, corpus GCS env, candidate verify instructions
6. Controls: `tests/test_hosted_partner_surfaces.py` · `scripts/demo_partner_dual_surface.sh` · `scripts/eval_hosted_partner_surface.py`
7. Docs: partner integrations, finding, design-partner loop, SUBMISSION-PACK honesty, AGENTS dual-surface, README/PITCH promise

## Verified (commands run)

```bash
python3 tests/test_watch_it_go_red.py                 # 72/72
python3 tests/test_hosted_partner_surfaces.py         # 5/5
python3 tests/test_partner_runtime.py                 # 7/7
python3 tests/test_parallel_integration.py            # 6/6
python3 tests/test_adk_default_path.py                # 5/5
python3 -m unittest tests.test_hosted_flow -q         # 13 OK
bash scripts/demo_partner_dual_surface.sh             # dual-surface local prove OK
python3 scripts/eval_hosted_partner_surface.py
# live: naive_pass=True shipping_pass=False (00028-hed)
# local-fix: naive_pass=True shipping_pass=True
python3 scripts/eval_refusal_baseline.py              # baseline 5/6 shipping 6/6 delta +1
python3 scripts/eval_refusal_ablation.py              # ablation 5/6 shipping 6/6 delta +1
python3 scripts/bench_check_docs.py                   # 128/128 match
python3 scripts/compound_exhibit_receipt.py           # A=2→B=1 Parallel · corpus_hits B=2
```

## Also fixed tonight

`fixtures/scripts/compound-mini-B.txt` had been paraphrased relative to A. Under exact
assertion identity that made offline compound go **A=2→B=3, corpus_hits=0** when re-measured.
Restored exact overlap + new BL claim; re-ran receipt → A=2→B=1, hits=2.

## BLOCKED

- Live compound orphan-works A/B — hosted partner surface dark + prior 504; no PARALLEL/GEMINI keys on this VM for a local live arm
- Hosted `engine_default: adk` — requires Oscar `deploy.sh` of this branch
- This VM: `google-adk` not installed → local `engine_default: direct` is honest

## Embarrassing finding kept

Naive liveness beats shipping on live hosted. Published in
`docs/FINDING-hosted-partner-strip-still-dark-2026-09-09.md`.
