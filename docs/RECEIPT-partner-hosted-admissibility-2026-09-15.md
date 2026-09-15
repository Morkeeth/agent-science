# RECEIPT — Partner hosted admissibility restore · 2026-09-15

**Slice:** Restore public `/health` + `/partners` partner fields on the private-workspace Cloud Run path.  
**Branch:** `cursor/partner-hosted-admissibility-d158`

## Finding (opened the hosted object)

```bash
curl -s https://agent-science-568004190078.us-central1.run.app/health | python3 -m json.tool
```

**Live revision `agent-science-00028-hed` returned only:**

```json
{
  "ok": true,
  "service": "agent-science",
  "mode": "private-workspaces",
  "revision": "agent-science-00028-hed"
}
```

Missing: `engine_default`, `parallel_sdk`, `gemini_path`, `agent_builder`.  
`GET /partners` redirected to login. `POST /clear` → **401**.  
Docs and `verify_partners_hosted.sh` claimed a surface that the live object no longer served.

Root cause: `cloud/service.py` routes all Cloud Run traffic through `WorkspaceHTTP`, whose `/health` was a thin liveness stub.

## What shipped

| Change | Object |
|--------|--------|
| Shared `health_payload()` + `partner_manifest_for_runtime()` | `cloud/partners.py` |
| Hosted `/health` + anonymous `/partners` | `cloud/case_http.py` |
| Local desk uses same payload builder | `cloud/service.py` |
| Hosted regression control | `tests/test_partner_runtime.py` · `tests/test_hosted_flow.py` |
| Verify script matches workspace boundary | `scripts/verify_partners_hosted.sh` |

## Verified at object (this VM)

```bash
python3 tests/test_adk_default_path.py          # 5/5
python3 tests/test_partner_runtime.py           # 8/8
python3 tests/test_parallel_integration.py      # 6/6
python3 -m unittest tests.test_hosted_flow.HostedFlow.test_anonymous_partner_health_and_manifest
python3 tests/test_watch_it_go_red.py           # 72/72
```

Local desk HTTP (no `K_SERVICE`):

```bash
PORT=8765 AGENT_BUILDER=1 GCP_PROJECT=hack-fleet PARALLEL_API_KEY=pk-live-abc python3 cloud/service.py
curl -s localhost:8765/health
```

Returned `engine_default: adk`, `adk_version: 2.7.1`, `parallel_sdk: true`, `mode: local-desk`.

## Still BLOCKED until Oscar deploy

- Live hosted `/health` remains thin until this revision is deployed and promoted.
- Live Parallel on hosted needs `AGENT_SCIENCE_WORKSPACE_TOKEN` (never in URL).
- Live orphan-works compound: no `PARALLEL_API_KEY` / `GEMINI_API_KEY` on this agent VM — see `docs/BLOCKED-live-compound-2026-09-15.md`.

## Naive baseline (embarrassing arm)

A competent team shipping private workspaces often leaves `/health` as `{ok:true}`. That arm is what revision `00028-hed` served. It fails track admissibility: partners are not provable at the hosted URL. This slice beats that baseline by restoring the partner fields without reopening public `/clear`.

## Compound exhibit re-derived (same night)

```bash
python3 scripts/compound_exhibit_receipt.py
```

First re-run with the old offline B claim wording failed at the object (**A=2→B=3**, `corpus_hits=0`). Cause: `corpus.recall` requires exact normalized assertion text — paraphrase is not a hit. Fixed the offline claim list so overlapping B claims reuse A's assertion text (script narration may still differ). Re-run: **A=2→B=1 Parallel**, **corpus_hits=2**, exit 0.
