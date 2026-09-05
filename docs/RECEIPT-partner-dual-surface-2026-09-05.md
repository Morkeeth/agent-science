# RECEIPT — partner dual surface · 2026-09-05

**Branch:** `cursor/partner-hosted-dual-surface-fe44`  
**Head:** `c46a569`  
**Scope:** restore partner admissibility beside private workspaces; do not run `deploy.sh`.

## Finding at the hosted object (before fix)

```bash
curl -sS https://agent-science-568004190078.us-central1.run.app/health
# {"ok": true, "service": "agent-science", "mode": "private-workspaces",
#  "revision": "agent-science-00026-zel"}

bash scripts/verify_partners_hosted.sh
# AssertionError: gemini: expected True, got None · exit 1
```

Write-up: `docs/FINDING-hosted-partner-strip-2026-09-05.md`

## What shipped (code)

| Item | Path |
|------|------|
| Shared health/partners builder | `cloud/partner_status.py` |
| Dual-surface routing | `cloud/service.py` — workspace paths → WorkspaceHTTP; desk+partners public |
| Defense-in-depth health | `cloud/case_http.py` |
| Deploy checklist (desk + workspace) | `deploy.sh` — `AGENT_BUILDER=1`, corpus GCS, Vertex project, candidate tag |
| Control suite | `tests/test_hosted_partner_surfaces.py` (5) |
| Local prove (no deploy) | `bash scripts/demo_partner_dual_surface.sh` |
| Partner doc refresh | `docs/PARTNER-INTEGRATIONS-2026-08-30.md` |
| Design partner gate note | `docs/DESIGN-PARTNER-LOOP.md` |
| Live compound | **BLOCKED** — `docs/BLOCKED-live-compound-2026-09-05.md` |

## Verified (commands run)

```text
python3 tests/test_watch_it_go_red.py
→ 72 passed, 0 failed

python3 tests/test_hosted_partner_surfaces.py
→ Ran 5 tests · OK

bash scripts/demo_partner_dual_surface.sh
→ health mode=private-workspaces+public-desk · partners OK · /clear≠401 · /api/cases=401

python3 -m unittest tests.test_hosted_flow -q
→ Ran 13 tests · OK

python3 tests/test_partner_runtime.py          → 7/7
python3 tests/test_adk_default_path.py         → 5/5
python3 tests/test_parallel_integration.py     → 6/6
python3 scripts/bench_check_docs.py            → 133/133 match SUBMISSION-PACK
python3 scripts/compound_exhibit_receipt.py    → exit 0 · A=2→B=1 · corpus_hits B=2
python3 scripts/eval_refusal_baseline.py       → baseline 5/6 · shipping 6/6 · delta +1
python3 scripts/eval_refusal_ablation.py       → ablation 5/6 · shipping 6/6 · delta +1
python3 scripts/eval_scorer_symmetry.py        → baseline 5/6 · shipping 6/6
python3 scripts/eval_verify_holdout.py         → HOLDOUT OK — 4 files
```

## Compound fixture note

Re-running the offline exhibit against pre-change `compound-mini-B.txt` (rephrased
overlapping claims) went **RED**: A=2→B=3, corpus_hits=0. That matches the 2026-09-04
assertion-keyed integrity rule. Fixtures now share identical lines for overlapping
facts; rephrasing correctly spends Parallel.

## Not verified on live hosted (Oscar)

`deploy.sh` not run. Until candidate promotion, public URL remains partner-dark.
After Oscar deploy:

```bash
bash scripts/verify_partners_hosted.sh
# expect mode=private-workspaces+public-desk · engine_default=adk
```
