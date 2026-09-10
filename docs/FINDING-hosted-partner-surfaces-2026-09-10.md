# FINDING — Hosted partner surfaces stripped by private-workspaces · 2026-09-10

**Status:** RED at object on revision `agent-science-00028-hed` · fix in tree awaiting Oscar `deploy.sh`

## What was measured (not inferred)

```bash
curl -s https://agent-science-568004190078.us-central1.run.app/health | python3 -m json.tool
```

Returned:

```json
{
  "ok": true,
  "service": "agent-science",
  "mode": "private-workspaces",
  "revision": "agent-science-00028-hed"
}
```

Missing: `gemini`, `gemini_path`, `parallel`, `parallel_sdk`, `agent_builder`, `engine_default`.

```bash
curl -s -o /dev/null -w '%{http_code}\n' https://agent-science-568004190078.us-central1.run.app/partners
# → 303 → /login
curl -s -o /dev/null -w '%{http_code}\n' -X POST https://agent-science-568004190078.us-central1.run.app/clear \
  -H 'Content-Type: application/json' -d '{"script":"x","subject":"t"}'
# → 401
```

```bash
bash scripts/verify_partners_hosted.sh
# → EXIT 1  AssertionError: gemini: expected True, got None
```

## Naive baseline that would have passed

Reading `docs/PARTNER-INTEGRATIONS-2026-08-30.md` and older receipts claimed:

- `[x] hosted` ADK default path
- `/health` reports `engine_default: adk`
- `/partners` is the judge manifest

That baseline answers "did we once ship this?" It does **not** answer "is it true on the URL a judge opens tonight?" Opening the URL is slower; it is the object.

## Why it broke

`cloud/service.py` routes **all** GET/POST through `WorkspaceHTTP` when `K_SERVICE` or `AGENT_SCIENCE_HOSTED=1`. `case_http` intentionally gates shared `/clear`/`/search` (product boundary). Its `/health` was reduced to a four-field liveness stub — partner readiness disappeared with the desk.

## Fix (this branch — not live until Oscar deploy)

- `cloud/partners.py` · `health_payload()` shared by local desk and hosted mode
- Hosted `/health` restores partner fields + names `clear_path=local-desk` and `parallel_hosted_path=workspace-live-research`
- Hosted `/partners` is public again (no auth)
- Shared `/clear` stays 401 on hosted (boundary preserved)
- Control: `HostedFlow.test_anonymous_partner_health_and_manifest_are_public`

## What remains Oscar-only

1. `bash deploy.sh` (candidate revision, then promote)
2. Re-run `bash scripts/verify_partners_hosted.sh` against live URL
3. Expect health OK with partner fields; `/clear` gated OK; compound skipped on hosted
