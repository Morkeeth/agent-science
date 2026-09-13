# RECEIPT — Partner surfaces under private-workspaces · 2026-09-13

**Branch:** `cursor/partner-integrations-night-a6b1`  
**Status:** local GREEN · hosted RED until Oscar `deploy.sh` lands this commit

## What went wrong (object, not docs)

```bash
curl -s https://agent-science-568004190078.us-central1.run.app/health
# {"ok": true, "service": "agent-science", "mode": "private-workspaces",
#  "revision": "agent-science-00028-hed"}
# Missing: gemini, parallel, engine_default, agent_builder, …

curl -s -o /dev/null -w '%{http_code}\n' \
  https://agent-science-568004190078.us-central1.run.app/partners
# 303  (login redirect)
```

`bash scripts/verify_partners_hosted.sh` failed at health assertion
`gemini: expected True, got None` — while SUBMISSION-PACK / prior receipts still
claimed partner verify green. **Docs were not the object.**

## What shipped

| Change | Object |
|--------|--------|
| `cloud/partners.health_payload()` | shared judge-facing health |
| `cloud/case_http.py` public `/health` + `/partners` | hosted mode keeps partner fields |
| `scripts/verify_partners_local.sh` | local desk prove without deploy |
| `scripts/verify_partners_hosted.sh` | private-workspaces aware; `/clear` local-only |
| tests | `test_partner_runtime` **8/8** · hosted anonymous partner test |

## Commands run (this VM)

```text
python3 tests/test_watch_it_go_red.py          → 72 passed, 0 failed
python3 tests/test_adk_default_path.py         → 5/5 passed
python3 tests/test_partner_runtime.py          → 8/8 passed
python3 tests/test_parallel_integration.py     → 6/6 passed
bash scripts/verify_partners_local.sh          → Partner local verify OK
  /health engine_default=adk · parallel_sdk=true · adk_version=2.7.1
python3 scripts/eval_refusal_baseline.py       → baseline 5/6 · shipping 6/6 · delta +1
python3 scripts/eval_refusal_ablation.py       → ablation 5/6 · shipping 6/6 · delta +1
```

## Hosted after Oscar redeploy (not run tonight)

```bash
bash scripts/verify_partners_hosted.sh
# expect: health checks OK · mode=private-workspaces · partners checklist OK
# clear/compound: SKIP (local-only boundary)
```

## BLOCKED tonight

| Item | Exact missing credential / act |
|------|--------------------------------|
| Live Parallel `/clear` on this VM | `PARALLEL_API_KEY` unset · no `~/.config/keys/parallel.key` |
| Live Gemini model call | no ADC / `GEMINI_API_KEY` on this VM |
| Hosted partner verify green | Oscar must run `deploy.sh` with this commit |
| Orphan-works live A/B | same keys + hosted timeout finding still open |
| Outward acts | deploy / Devpost / video / key rotation — Oscar only |
