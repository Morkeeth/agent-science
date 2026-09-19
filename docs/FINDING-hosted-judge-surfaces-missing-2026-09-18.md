# FINDING — hosted judge film surfaces missing · 2026-09-18

**Object:** live Cloud Run `agent-science-00028-hed` + local WorkspaceHTTP route table

## Measured at live URL

```bash
curl -sS -o /dev/null -w '%{http_code}\n' \
  https://agent-science-568004190078.us-central1.run.app/truths/ui
# → 303

curl -sS -o /dev/null -w '%{http_code}\n' \
  'https://agent-science-568004190078.us-central1.run.app/visibility/ui?q=ralph+loop+agentic'
# → 303

bash film/preflight.sh
# → PREFLIGHT FAIL: /health bad · visibility UI missing Transparency · truths ui down
```

## Measured on local private-workspaces (before fix)

Anonymous `/truths/ui` → **303** login.  
Bearer-authenticated `/truths/ui` → **404** (WorkspaceHTTP only mounted `/cases`).

So the film surfaces were not "auth gated" — they were **absent** from the hosted
handler. Docs and STATUS still described `/truths/ui` and `/visibility/ui` as live
judge faces (stale nearer proxy: an older revision / local desk).

## Fix in tree

`WorkspaceHTTP.route` serves public read-only:

| Path | Auth | Notes |
|------|------|-------|
| `/truths/ui` | public | film dashboard |
| `/visibility`, `/visibility/ui` | public | `live` defaults **false** |
| `/popular`, `/popular/ui` | public | flywheel face |
| `/health`, `/partners` | public | partner proof (prior fix) |
| `/search`, `/clear`, `/ingest`, `/registry` | shut | constitution / private-workspaces |

Prove: `bash scripts/prove_judge_surfaces_local.sh`  
Test: `HostedFlow.test_anonymous_judge_film_surfaces_public`

**Still RED on live until Oscar `deploy.sh`.**
