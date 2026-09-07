# RECEIPT — partner dual surface re-land · 2026-09-07

**Branch:** `cursor/partner-dual-surface-night-5b82`  
**Scope:** prior dual-surface fix never reached `main`; re-landed tonight; measured live RED vs local shipping; secret-scanner leak in demo fixed; baseline eval shipped.

## Finding at the hosted object (still true tonight)

```bash
curl -sS https://agent-science-568004190078.us-central1.run.app/health | python3 -m json.tool
```

```json
{
    "ok": true,
    "service": "agent-science",
    "mode": "private-workspaces",
    "revision": "agent-science-00026-zel"
}
```

```bash
bash scripts/verify_partners_hosted.sh
# AssertionError: gemini: expected True, got None
```

Write-up: `docs/FINDING-hosted-partner-strip-2026-09-05.md`

## Baseline arm that embarrasses us

```bash
python3 scripts/eval_hosted_partner_surface.py
```

| Target | Naive (ok+service) | Shipping (partner fields + public /partners + /clear≠401 + /api/cases=401) |
|--------|--------------------|-------------------------------------------------------------------------------|
| Live `00026-zel` | **PASS** | **FAIL** |
| Local dual-surface server | PASS | **PASS** |

Naive wins on live. That is the finding. Shipping wins only after this code is deployed.

## What shipped (code on this branch)

| Item | Path |
|------|------|
| Shared health/partners builder | `cloud/partner_status.py` |
| Dual-surface routing | `cloud/service.py` |
| Defense-in-depth health | `cloud/case_http.py` |
| Deploy checklist (desk + workspace) | `deploy.sh` |
| Control suite | `tests/test_hosted_partner_surfaces.py` (5) |
| Local prove (no key export) | `bash scripts/demo_partner_dual_surface.sh` |
| Baseline eval | `python3 scripts/eval_hosted_partner_surface.py` |
| Partner doc | `docs/PARTNER-INTEGRATIONS-2026-08-30.md` |
| AGENTS hosted boundary honesty | `AGENTS.md` |

## Verified (commands run 2026-09-07)

```text
python3 tests/test_watch_it_go_red.py
→ 72 passed, 0 failed
  (earlier: FAIL on demo PARALLEL_API_KEY export — fixed, re-run green)

python3 tests/test_hosted_partner_surfaces.py → 5/5 OK
bash scripts/demo_partner_dual_surface.sh
→ mode=private-workspaces+public-desk · partners OK · /clear=503 · /api/cases=401

PYTHONPATH=. python3 tests/test_hosted_flow.py → 13/13 OK
python3 tests/test_partner_runtime.py → 7/7
python3 tests/test_adk_default_path.py → 5/5
python3 tests/test_parallel_integration.py → 6/6
python3 scripts/bench_check_docs.py → 133/133 match SUBMISSION-PACK
python3 scripts/compound_exhibit_receipt.py → A=2→B=1 · corpus_hits B=2
python3 scripts/eval_refusal_baseline.py → baseline 5/6 · shipping 6/6 · delta +1
python3 scripts/eval_hosted_partner_surface.py
→ live naive PASS / shipping FAIL · local-fix shipping PASS
bash scripts/verify_partners_hosted.sh → RED on live 00026 (expected until Oscar deploy)
```

## Wrong / not verified

- Did not run `deploy.sh` (Oscar only). Live URL remains partner-dark until candidate promote.
- Local `/clear` returns 503 without Vertex/Gemini — proves desk routing, not a live ADK model call on this VM.
- `parallel: false` on local demo (no key export by design); Parallel runtime proof still needs Oscar deploy with Secret Manager.
- Prior branch `cursor/partner-hosted-dual-surface-fe44` shipped the same dual surface on 2026-09-05 and never merged — tonight re-landed onto current `main` plus the baseline eval and the secret-scanner fix the earlier demo lacked.
