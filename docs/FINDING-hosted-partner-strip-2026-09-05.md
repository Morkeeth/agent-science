# FINDING — hosted partner strip · 2026-09-05

**Object measured:** live Cloud Run URL  
`https://agent-science-568004190078.us-central1.run.app`  
**Revision:** `agent-science-00026-zel`  
**Command:** `curl -sS …/health` · `bash scripts/verify_partners_hosted.sh`

## What went red

Private-workspaces deploy (`AGENT_SCIENCE_HOSTED=1`) routed **every** HTTP path through
`WorkspaceHTTP`. That handler's `/health` returned only:

```json
{"ok": true, "service": "agent-science", "mode": "private-workspaces", "revision": "agent-science-00026-zel"}
```

Missing at the object: `gemini`, `gemini_path`, `parallel`, `parallel_sdk`, `agent_builder`,
`engine_default`. `GET /partners` and `POST /clear` redirected to `/login` (303) or were
unreachable for the partner verify script.

`bash scripts/verify_partners_hosted.sh` → **exit 1**  
`AssertionError: gemini: expected True, got None`

## Why docs looked green

Partner receipts from 2026-08-30 … 2026-09-03 measured an earlier desk revision. Local
`test_partner_runtime.py` only checked that `cloud/service.py` *contained* the strings —
it never started the server with `AGENT_SCIENCE_HOSTED=1` and asked `/health`. A nearer
proxy (source grep) answered faster than the hosted object.

## Fix (this branch)

Dual surface on one process:

| Path | Auth | Role |
|------|------|------|
| `/health`, `/partners`, `/`, `/clear`, registry/visibility UIs | public | partner track + clearance desk |
| `/cases`, `/api/cases`, `/login` | workspace token/session | private research |

Shared builder: `cloud/partner_status.py`. Control:
`python3 tests/test_hosted_partner_surfaces.py` (5 tests) — fails if the 00026 shape returns.

## Still Oscar

`bash deploy.sh` is Oscar's click. Until the candidate revision is promoted, **live hosted
remains partner-dark**. Local + unit controls prove the code path; live re-verify after deploy:

```bash
bash scripts/verify_partners_hosted.sh
```
