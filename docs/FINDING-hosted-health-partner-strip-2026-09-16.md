# FINDING — hosted /health stripped partner proof · 2026-09-16

**Object:** `GET https://agent-science-568004190078.us-central1.run.app/health`  
**Revision measured:** `agent-science-00028-hed`  
**Command:**

```bash
curl -sS https://agent-science-568004190078.us-central1.run.app/health | python3 -m json.tool
```

**Observed body (only these keys):**

```json
{
  "ok": true,
  "service": "agent-science",
  "mode": "private-workspaces",
  "revision": "agent-science-00028-hed"
}
```

**Missing partner fields (admissibility):** `gemini`, `gemini_path`, `parallel`, `parallel_sdk`,
`agent_builder`, `engine_default`, `adk_version`.

**Why this is a false-green class defect:** `ok: true` satisfied a shallow liveness read while
`bash scripts/verify_partners_hosted.sh` still asserted `gemini: True`. On this revision the
script failed at the assertion (`got None`). Docs (`docs/PARTNER-INTEGRATIONS-2026-08-30.md`,
`film/preflight.sh`, hack.md PLAN slice 5) still claimed `engine_default: adk` on hosted health.

**Root cause at object:** `cloud/case_http.py` WorkspaceHTTP handled `/health` with a
liveness-only dict when `K_SERVICE` / `AGENT_SCIENCE_HOSTED=1` routed all traffic away from
`cloud/service.py`'s full health builder. `/partners` required workspace auth and returned the
login HTML (HTTP 200 after redirect follow), not the track manifest JSON.

**Fix in tree (this branch):** shared `cloud.partners.health_payload()`; WorkspaceHTTP serves
full partner `/health` and public `/partners` before auth. Local prove:

```bash
bash scripts/prove_partner_health_local.sh
python3 -m unittest tests.test_hosted_flow.HostedFlow.test_anonymous_health_exposes_partner_fields -v
```

**Still RED until Oscar deploy:** live URL continues to serve revision `00028-hed` until
`bash deploy.sh` (Oscar only). Do not claim hosted partner health green before re-running
`bash scripts/verify_partners_hosted.sh` against the new revision.
