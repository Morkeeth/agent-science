# RECEIPT — Partner dual surface · 2026-09-08

**Branch:** `cursor/partner-dual-surface-night-6089` · **Commit:** `d3d35ae`  
**Slice:** restore partner-admissible public desk beside private workspaces; prove at object; leave hosted RED until Oscar deploy.

## SHIPPED

| Item | Evidence |
|------|----------|
| Dual-surface routing | `cloud/partner_status.py` · `cloud/service.py` routes workspace paths only to `WorkspaceHTTP` |
| Defense-in-depth health | `cloud/case_http.py` still emits partner fields if routing regresses |
| Local prove | `bash scripts/demo_partner_dual_surface.sh` |
| Verify --local | `bash scripts/verify_partners_hosted.sh --local` |
| Regression suite | `python3 tests/test_hosted_partner_surfaces.py` (5/5) |
| Compound integrity fix | `fixtures/scripts/compound-mini-B.txt` exact overlap · A=2→B=1 hits=2 |
| Baseline eval | `python3 scripts/eval_hosted_partner_surface.py` — naive beats shipping on live |
| Deploy checklist | `deploy.sh` dual-surface env + Secret Manager Parallel |
| Partner doc | `docs/PARTNER-INTEGRATIONS-2026-08-30.md` |
| Finding | `docs/FINDING-hosted-partner-strip-2026-09-08.md` |

## VERIFIED (commands run)

```text
python3 tests/test_watch_it_go_red.py
→ 72 passed, 0 failed

python3 tests/test_hosted_partner_surfaces.py
→ Ran 5 tests … OK

python3 tests/test_partner_runtime.py
→ 7/7 passed

python3 tests/test_parallel_integration.py
→ 6/6 passed

python3 -m unittest tests.test_hosted_flow -q
→ Ran 13 tests … OK

python3 tests/test_secret_surfaces.py
→ 6 passed, 0 failed

bash scripts/demo_partner_dual_surface.sh
→ mode=private-workspaces+public-desk · POST /clear ≠401 · GET /api/cases=401

bash scripts/verify_partners_hosted.sh --local
→ Partner hosted verify OK (local dual-surface fields)

python3 scripts/eval_hosted_partner_surface.py
→ live: naive_pass=True shipping_pass=False revision=agent-science-00028-hed
→ local-fix: shipping_pass=True

bash scripts/verify_partners_hosted.sh
→ RED: missing partner field gemini (liveness-only health)

python3 scripts/eval_refusal_baseline.py
→ baseline 5/6 · shipping 6/6 · delta +1

python3 scripts/bench_check_docs.py
→ ALL 133/133 match SUBMISSION-PACK

python3 scripts/compound_exhibit_receipt.py
→ A=2 → B=1 Parallel · corpus_hits B=2 · exit 0
  (before fixture fix tonight: A=2 → B=3 · hits=0 · exit 3)

bash scripts/verify_cold_clone.sh
→ cold-clone verify OK
```

## BLOCKED (Oscar)

- Live hosted still revision **00028-hed** — partner strip. Deploy is Oscar's click (`bash deploy.sh`).
- Live Parallel/Gemini compound on orphan-works — no keys on this VM; offline compound receipt authoritative after fixture fix.
- `google-adk` / `parallel-web` not installed in this agent image — local `engine_default` reports `direct` / `parallel_sdk=false`; Cloud Run image still pins both in `requirements.txt`.

## WRONG / honest gaps

- Earlier night receipts and hack.md NOW claimed hosted partners green; curling `/health` on 2026-09-08 falsified that.
- Offline compound docs still said A=2→B=1 while the command was A=2→B=3 until we re-ran it tonight.
- Local prove cannot stamp `engine: adk` without the ADK package in the image — ADK path is covered by unit tests with mocks + requirements pin, not by a live ADK import here.
- Prior dual-surface restore branches never merged to main — we re-landed the fix rather than discovering it first.
