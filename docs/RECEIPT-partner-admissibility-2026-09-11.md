# RECEIPT — partner admissibility night · 2026-09-11

**Branch:** `cursor/partner-hosted-admissibility-0c32`  
**North star obeys:** partners must be provable at runtime, not only in docs.

## SHIPPED

1. Shared `cloud/partners.health()` + public `/health` · `/partners` on hosted
   private-workspaces path (`cloud/case_http.py`).
2. RED control + baseline arm: naive stripped health **1/8** vs shipping **8/8**.
3. `scripts/verify_partners_hosted.sh` rewritten for workspace boundary
   (public health/partners; `/clear` local-only).
4. SUBMISSION-PACK counts re-derived: partner_runtime **8/8**, total **129/129**.
5. Design-partner loop corrected away from dead public `/clear` URL.
6. Finding doc naming the regression at object.
7. Offline compound exhibit repaired under exact-assertion reuse
   (`compound-mini-B` shares verbatim overlap; paraphrase correctly scored 0).
8. Workspace-aware `new_user_trial.sh` / `long_run_goal.sh` / `film/preflight.sh`.

## VERIFIED (commands run)

```text
python3 tests/test_watch_it_go_red.py          → 72 passed, 0 failed
python3 tests/test_partner_runtime.py          → 8/8 passed
python3 tests/test_parallel_integration.py     → 6/6 passed
python3 tests/test_adk_default_path.py         → 5/5 passed
python3 -m unittest tests.test_hosted_flow     → OK (14 tests)
python3 scripts/eval_partner_health_baseline.py
  → naive 1/8 · shipping 8/8 · live hosted 1/8 BLOCKED_DEPLOY
python3 scripts/eval_refusal_baseline.py       → baseline 5/6 · shipping 6/6 · delta +1
python3 scripts/eval_refusal_ablation.py       → ablation 5/6 · shipping 6/6 · delta +1
python3 scripts/bench_check_docs.py            → 129/129 match (after pack update)
curl -s …/health                               → stripped fields on live 00028-hed
pip install google-adk==2.7.1 parallel-web==1.3.2
python3 -c "from cloud import partners, agent; from clearance import search; \
  import os; os.environ.update(AGENT_BUILDER='1',GCP_PROJECT='hack-fleet',PARALLEL_API_KEY='pk-live-abc'); \
  print(agent.adk_available(), search.sdk_available(), partners.health()['engine_default'])"
  → True True adk
env -u PARALLEL_API_KEY python3 scripts/compound_exhibit_receipt.py
  → A=2→B=1 Parallel · corpus_hits B=2 · exit 0
bash scripts/new_user_trial.sh http://127.0.0.1:8765 → Trial OK (workspace path)
```

Local hosted simulation (AGENT_SCIENCE_HOSTED=1):

```text
GET /health  → 200 with gemini_path, parallel, engine_default, mode=private-workspaces
GET /partners → 200 track_checklist
POST /clear  → 401 (boundary held)
```

## BLOCKED

- Live Cloud Run still revision `agent-science-00028-hed` until Oscar deploy.
- Live orphan-works compound / Parallel call on hosted `/clear` — route is
  local-only by constitution; no PARALLEL_API_KEY / GEMINI_API_KEY on this VM
  for a local live clear either (`~/.config/keys/parallel.key` missing).

## WRONG / left broken

- Pre-redeploy, `bash scripts/verify_partners_hosted.sh` against live URL **fails**
  (correct — the object is still stripped). Do not tick hosted partner ✅ until
  Oscar redeploys and the script exits 0.
- This VM initially lacked `google-adk` / `parallel-web` in the bare interpreter;
  after `pip install google-adk==2.7.1 parallel-web==1.3.2`, local
  `partners.health()` reports `engine_default: adk`, `parallel_sdk: true`,
  `adk_version: 2.7.1` (command in receipt verify block above).
- DESIGN-PARTNER-LOOP previously instructed partners to POST public `/clear` on
  the hosted URL — that path was already dead; template corrected, outreach still
  Oscar-only.
