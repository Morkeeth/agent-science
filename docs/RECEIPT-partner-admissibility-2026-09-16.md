# RECEIPT — Partner admissibility night · 2026-09-16

**Branch:** `cursor/partner-health-admissibility-8356`  
**Slice:** Restore partner proof on private-workspaces hosted path; refresh partner doc; re-derive eval/SUBMISSION counts; design-partner loop for auth desk.

## Finding (embarrassing — kept)

Live `/health` on revision `agent-science-00028-hed` returned only `{ok, service, mode, revision}`. Partner fields required by `verify_partners_hosted.sh` and the Sep 9 admissibility story were absent. Documented in `docs/FINDING-hosted-health-partner-strip-2026-09-16.md`.

```bash
curl -sS https://agent-science-568004190078.us-central1.run.app/health | python3 -m json.tool
# → no gemini / parallel / engine_default
```

## Shipped in tree

| Item | Object |
|------|--------|
| Shared `cloud.partners.health_payload()` | used by local desk + WorkspaceHTTP |
| Public hosted `/health` + `/partners` | `cloud/case_http.py` before auth |
| Local prove script | `bash scripts/prove_partner_health_local.sh` |
| Hosted verify honesty | `scripts/verify_partners_hosted.sh` — fails on stripped health; `/clear` needs token |
| Partner doc | `docs/PARTNER-INTEGRATIONS-2026-08-30.md` |
| Design partner loop | `docs/DESIGN-PARTNER-LOOP.md` (login + local clear paths) |
| Live compound | `docs/BLOCKED-live-compound-2026-09-16.md` (exact missing creds) |

## Commands run (done-when)

```text
git pull origin main
python3 tests/test_watch_it_go_red.py                          → 72 passed, 0 failed
python3 tests/test_adk_default_path.py                         → 5/5 passed
python3 tests/test_partner_runtime.py                          → 7/7 passed
python3 tests/test_parallel_integration.py                     → 6/6 passed
python3 -m unittest tests.test_hosted_flow -v                  → 15 tests OK
bash scripts/prove_partner_health_local.sh                     → PROVE_PARTNER_HEALTH_LOCAL OK
python3 scripts/bench_check_docs.py                            → ALL 128/128 match
python3 scripts/eval_refusal_baseline.py                       → baseline 5/6=0.833 · shipping 6/6=1.000 · delta +1
python3 scripts/eval_refusal_ablation.py                       → ablation 5/6 · shipping 6/6 · delta +1
```

Local hosted prove sample (`engine_default: adk`, `gemini: true`, `parallel: true`, `mode: private-workspaces`).

## Still RED / Oscar

- Live URL until `deploy.sh` — health still stripped on `00028-hed`
- Live `/clear` compound — no `PARALLEL_API_KEY` / workspace token on this VM
- Key rotation — Oscar only (`AS-KEYS-ROTATE`)
