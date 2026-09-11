# FINDING — Hosted partner proof went dark under private-workspaces

**Date:** 2026-09-11 · **Object:** live Cloud Run + `cloud/case_http.py`  
**Revision measured:** `agent-science-00028-hed`  
**URL:** https://agent-science-568004190078.us-central1.run.app/health

## Claim that failed

Docs, receipts, STATUS, PITCH, and `verify_partners_hosted.sh` treated hosted
`GET /health` as proving all four partners (`gemini`, `parallel`, `agent_builder`,
`engine_default: adk`). That claim was **false at the live object** on 2026-09-11.

## What was measured (command → output)

```bash
curl -sS https://agent-science-568004190078.us-central1.run.app/health | python3 -m json.tool
```

```json
{
    "ok": true,
    "service": "agent-science",
    "mode": "private-workspaces",
    "revision": "agent-science-00028-hed"
}
```

Missing on live: `gemini`, `gemini_path`, `parallel`, `parallel_sdk`,
`agent_builder`, `engine_default`, `adk_version`.

```bash
bash scripts/verify_partners_hosted.sh
# EXIT 1 — AssertionError: gemini: expected True, got None
```

```bash
curl -sS -o /dev/null -w '%{http_code}' https://agent-science-568004190078.us-central1.run.app/partners
# 303 → /login  (HTML sign-in page)
```

## Root cause (opened at the object, not by title)

`cloud/service.py` still builds the full partner health payload for the **local**
desk. Under `AGENT_SCIENCE_HOSTED=1` / `K_SERVICE`, every GET/POST is handed to
`WorkspaceHTTP`, whose `/health` stub returned only liveness:

```python
# cloud/case_http.py (before fix)
return self.send(200, {'ok': True, 'service': 'agent-science',
                       'mode': 'private-workspaces',
                       'revision': os.getenv('K_REVISION', 'local')})
```

`/partners` fell through to the auth gate → 303 login. Private research routes
(`/search`, `/clear`, `/ingest`) being local-only is intentional product boundary
(AGENTS.md). Stripping **partner admissibility** from public `/health` and
`/partners` was not — and it made STATUS/receipts read green for days.

## Control watched RED first

Local reproduction before the fix (same stub):

```text
health body: {ok, service, mode, revision}
missing partner fields: [gemini, parallel, parallel_sdk, agent_builder, engine_default, gemini_path]
RED
CONTROL WATCHED RED as expected
```

## Fix shipped (this branch — needs Oscar deploy to heal live)

1. `cloud/partners.health_payload()` — single builder for local + hosted health.
2. `WorkspaceHTTP` serves full health + public `/partners` **before** auth.
3. `/clear` / `/search` remain gated (anonymous still 401/303).
4. `scripts/verify_partners_hosted.sh` — fails loudly on stripped health; on
   private-workspaces without `AGENT_SCIENCE_WORKSPACE_TOKEN`, proves public
   surfaces and reports clear/compound **BLOCKED** instead of false-green.
5. `scripts/prove_partners_local.sh` — cold local proof, no deploy.

## What is still BLOCKED until Oscar

| Item | Why |
|------|-----|
| Live `/health` partner fields | Deploy not run (Oscar only) — rev 00028 still stripped |
| Live anonymous `/clear` Parallel call | Product: private-workspaces; needs workspace bearer |
| Live compound A/B on hosted | Same; also orphan-works 504 history |
| `PARALLEL_API_KEY` / Gemini on this VM | No keys in env — live compound not attempted |

## Lesson

A nearer proxy (STATUS saying `engine_default: adk`, old receipts) answered
faster than opening live `/health`. Opening the URL was the ambitious move and
the one that caught the lie.
