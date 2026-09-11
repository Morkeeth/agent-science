# RECEIPT — Partner hosted proof dark → local restore · 2026-09-11

**Branch:** `cursor/partner-hosted-proof-1bc9`  
**Slice:** Restore partner admissibility on private-workspaces; prove RED on live; ship local GREEN.

## Commands run

### Live RED (pre-deploy — still true on rev 00028)

```bash
curl -sS https://agent-science-568004190078.us-central1.run.app/health | python3 -m json.tool
# {ok, service, mode: private-workspaces, revision: agent-science-00028-hed}
# missing: gemini, parallel, engine_default, …

bash scripts/verify_partners_hosted.sh
# EXIT 1 — FAIL: /health missing partner fields […] — FINDING-hosted-partner-proof-dark-2026-09-11.md
```

### Local GREEN (this commit)

```bash
bash scripts/prove_partners_local.sh
# engine_default: adk · agent_builder: true · adk_version: 2.7.1
# anonymous /clear stays 401 · PROVE_PARTNERS_LOCAL OK

python3 tests/test_partner_runtime.py          # 8/8
python3 tests/test_adk_default_path.py         # 5/5
python3 tests/test_parallel_integration.py     # 6/6
python3 -m unittest tests.test_hosted_flow -q  # OK (incl. anonymous partner surfaces)
python3 tests/test_watch_it_go_red.py          # 72/72
python3 scripts/eval_refusal_baseline.py       # baseline 5/6 · shipping 6/6 · delta +1
python3 scripts/eval_refusal_ablation.py       # ablation 5/6 · shipping 6/6 · delta +1
```

### ADK import on this VM (after `pip install google-adk==2.7.1`)

```text
adk_available True
version 2.7.1
prove_partners_local → engine_default: adk
```

## BLOCKED

| Item | Exact missing / reason |
|------|------------------------|
| Live health partner fields | Oscar `deploy.sh` not run — outward act |
| Live `/clear` Parallel | No `AGENT_SCIENCE_WORKSPACE_TOKEN`; public clear gated |
| Live compound orphan-works | No `PARALLEL_API_KEY` / `GEMINI_API_KEY` on this VM; historic 504 |

## Docs touched

- `docs/FINDING-hosted-partner-proof-dark-2026-09-11.md`
- `docs/PARTNER-INTEGRATIONS-2026-08-30.md`
- `docs/DESIGN-PARTNER-LOOP.md`
- `hack.md` NOW + LOG
