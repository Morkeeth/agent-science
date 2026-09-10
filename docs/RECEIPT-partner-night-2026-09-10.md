# RECEIPT — Partner night wave · 2026-09-10

**Branch intent:** restore public partner proof on private-workspaces hosted mode without reopening shared `/clear`.

**Commit:** `41425aa` on `cursor/partner-hosted-surfaces-54ba`

## Shipped

| Item | Object |
|------|--------|
| Shared `health_payload()` | `cloud/partners.py` |
| Hosted `/health` partner fields | `cloud/case_http.py` |
| Public `/partners` | `cloud/case_http.py` (no auth) |
| Local desk uses same payload | `cloud/service.py` |
| Verify script dual-mode | `scripts/verify_partners_hosted.sh` |
| Film preflight names stripped health | `film/preflight.sh` |
| RED→GREEN control | `tests/test_hosted_flow.py` · `test_partner_runtime.py` |
| Finding at live URL | `docs/FINDING-hosted-partner-surfaces-2026-09-10.md` |
| Stale compound finding + fix | `docs/FINDING-compound-exhibit-stale-2026-09-10.md` |
| Partner doc + design-partner loop | docs |
| Live compound | `docs/BLOCKED-live-compound-2026-09-10.md` |
| Promise line | README opening (outcome · proof · constraint) |
| SUBMISSION-PACK | partner_runtime **8/8** · total **129/129** |

## Commands run (this VM)

```text
git pull && python3 tests/test_watch_it_go_red.py          → 72/72
python3 tests/test_partner_runtime.py                     → 8/8
python3 tests/test_adk_default_path.py                    → 5/5
python3 tests/test_parallel_integration.py                → 6/6
python3 -m unittest tests.test_hosted_flow                → 14/14 OK
python3 scripts/bench_check_docs.py                       → 129/129
python3 scripts/eval_refusal_baseline.py                  → baseline 5/6, shipping 6/6, delta +1
python3 scripts/eval_refusal_ablation.py                  → ablation 5/6, shipping 6/6, delta +1
python3 scripts/compound_exhibit_receipt.py; echo EXIT:$? → first RED EXIT 3; after fix EXIT 0 (A=2→B=1, hits=2)
bash scripts/verify_partners_hosted.sh                    → FAIL on live 00028 (finding)
bash film/preflight.sh; echo EXIT:$?                      → EXIT 1 (stripped health + gated UIs)
```

## Local hosted-mode prove (no deploy)

With `AGENT_SCIENCE_HOSTED=1`, mocked/real ADK+SDK, temp workspace:

- `GET /health` → `engine_default: adk`, `gemini: true`, `parallel: true`, `mode: private-workspaces`
- `GET /partners` → 200 JSON track checklist
- `POST /clear` → 401 (boundary held)

## Still blocked until Oscar deploy

Live URL still serves revision `agent-science-00028-hed` without partner fields. This receipt proves the **code path**; it does not claim the public revision is fixed.
