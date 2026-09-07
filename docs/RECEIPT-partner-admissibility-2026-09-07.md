# RECEIPT — Partner admissibility on private workspaces · 2026-09-07

**Branch:** `cursor/partner-admissibility-hosted-68f4`  
**Slice:** restore partner-admissible public surfaces + auth-gated clearance without undoing private workspaces.

## SHIPPED

| Item | Evidence |
|------|----------|
| Shared `cloud/partners.py` health + honest checklist | `python3 tests/test_partner_runtime.py` → **10/10** |
| Hosted `WorkspaceHTTP` public `/health` + `/partners` | `python3 -m unittest tests.test_hosted_flow` → **15 OK** |
| Auth-gated `POST /api/clear` with request_id idempotency | same suite · `test_auth_clear_uses_adk_path_and_is_idempotent` |
| `deploy.sh` Vertex/ADK non-secret env | `t_deploy_sh_secret_manager_not_plaintext_env` |
| Compound probes use `/api/clear` + token when set | `scripts/compound_*_hosted_probe.py` |
| Partner verify script fails on stripped health | measured against live URL (RED) + finding doc |
| Offline compound fixture aligned to exact-assertion integrity | `compound_exhibit_receipt.py` → A=2→B=1, hits=2, exit 0 |
| SUBMISSION-PACK counts | **131/131** after partner suite grew 7→10 |
| Design partner loop updated for login + token clear | `docs/DESIGN-PARTNER-LOOP.md` |
| Partner integrations doc rewritten for dual-mode | `docs/PARTNER-INTEGRATIONS-2026-08-30.md` |

## VERIFIED (commands run)

```text
python3 tests/test_watch_it_go_red.py          # 72/72
python3 tests/test_partner_runtime.py          # 10/10
python3 tests/test_parallel_integration.py     # 6/6
python3 tests/test_adk_default_path.py         # 5/5
python3 -m unittest tests.test_hosted_flow     # 15 OK
python3 scripts/bench_check_docs.py            # 131/131 (after pack update)
python3 scripts/eval_refusal_baseline.py       # baseline 5/6 shipping 6/6 delta +1
python3 scripts/eval_refusal_ablation.py       # ablation 5/6 shipping 6/6 delta +1
python3 scripts/eval_scorer_symmetry.py        # baseline 5/6 vs shipping 6/6
python3 scripts/eval_verify_holdout.py         # HOLDOUT OK 4 files
curl -s …/health                               # live still stripped (RED finding)
bash scripts/verify_partners_hosted.sh         # RED on live until redeploy
```

## BLOCKED / WRONG

- **Live hosted** still revision `00026-zel` with stripped health — Oscar must `bash deploy.sh` then promote.
- **No keys on this VM** — cannot run live Parallel orphan-works A/B here; offline eval + compound exhibit remain authoritative.
- **Auth-gated clear on live** needs `AGENT_SCIENCE_WORKSPACE_TOKEN` from Secret Manager — not present in this agent env.
- Promise-line README rewrite skipped: product ruling keeps CLI/MCP as front door; clearance promise remains in PITCH/SUBMISSION-PACK.
