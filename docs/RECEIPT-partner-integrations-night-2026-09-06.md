# RECEIPT — partner integrations night · 2026-09-06

**Branch:** `cursor/partner-integrations-night-d9fb`  
**Slice:** Restore partner admissibility on hosted private-workspaces (health + public /partners); measure live RED; ship baseline eval.

## SHIPPED

1. Hosted `/health` partner fields via shared `cloud/partners.health_payload()`
2. Public `GET /partners` on private-workspaces (no auth)
3. `docs/FINDING-hosted-partner-surface-2026-09-06.md` — live loses to naive liveness
4. `scripts/eval_hosted_partner_surface.py` — baseline arm vs shipping
5. `scripts/verify_partners_hosted.sh --local` — structural prove without keys
6. `tests/test_hosted_partner_surface.py` — 3/3
7. Partner doc + design-partner loop + hack.md NOW honesty for desk boundary
8. BLOCKED compound doc naming exact missing credentials

## VERIFIED (commands run)

```text
$ python3 tests/test_watch_it_go_red.py
72 passed, 0 failed

$ PYTHONPATH=/workspace python3 tests/test_hosted_partner_surface.py -v
Ran 3 tests … OK

$ PYTHONPATH=/workspace python3 tests/test_partner_runtime.py
7/7 passed

$ PYTHONPATH=/workspace python3 tests/test_adk_default_path.py
5/5 passed

$ bash scripts/verify_partners_hosted.sh --local
=== Partner hosted verify OK ===

$ python3 scripts/eval_hosted_partner_surface.py
FINDING: live hosted loses to naive liveness — partner fields absent (revision=agent-science-00026-zel)
LOCAL FIX: shipping arm passes

$ python3 scripts/compound_exhibit_receipt.py
A=2 → B=1 Parallel · corpus_hits B=2 · exit 0
# also found paraphrase-reuse break; see FINDING-compound-paraphrase-reuse-2026-09-06.md

$ python3 scripts/bench_check_docs.py
ALL 128/128 match SUBMISSION-PACK

$ curl -s https://agent-science-568004190078.us-central1.run.app/health
{"ok": true, "service": "agent-science", "mode": "private-workspaces", "revision": "agent-science-00026-zel"}
# partner fields absent until Oscar deploy
```

## NOT verified on live after fix

Oscar deploy not run (constitution). Live shipping arm remains FAIL until revision promotes this code.
