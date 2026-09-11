# RECEIPT — ADK on default path · 2026-08-30

**Status:** proved locally 2026-09-11 (`engine_default: adk` with real `google-adk==2.7.1` import).  
**Hosted:** 2026-08-30 green · **2026-09-11 RED** — private-workspaces stripped `/health` (FINDING); fix in tree awaiting Oscar deploy.

## What was verified

| Check | Command | Result |
|-------|---------|--------|
| Engine selection controls | `python3 tests/test_adk_default_path.py` | **5/5 passed** |
| ADK importable | `python3 -c "from cloud import agent as a; print(a.adk_available(), a.adk_version())"` | **True 2.7.1** (2026-09-11) |
| Shared health payload | `bash scripts/prove_partners_local.sh` | **`engine_default: adk`** · `agent_builder: true` |
| Fallback stamps error | `t_run_clearance_falls_back_to_direct_and_stamps_error` | `engine: direct`, `adk_error` present |

## Local prove (2026-09-11)

```bash
bash scripts/prove_partners_local.sh
```

```json
{
  "gemini": true,
  "parallel": true,
  "parallel_sdk": false,
  "agent_builder": true,
  "engine_default": "adk",
  "gemini_path": "vertex:hack-fleet",
  "mode": "private-workspaces",
  "adk_version": "2.7.1",
  "revision": "local"
}
```

## Hosted /health (measured 2026-09-11 — still broken until deploy)

```bash
curl -s https://agent-science-568004190078.us-central1.run.app/health | python3 -m json.tool
```

```json
{
  "ok": true,
  "service": "agent-science",
  "mode": "private-workspaces",
  "revision": "agent-science-00028-hed"
}
```

Partner fields absent — see `docs/FINDING-hosted-partner-proof-dark-2026-09-11.md`.

## What is NOT proved here

- **Live ADK model call on hosted `/clear`** — route gated; no workspace token on this VM.
- **Live health after fix** — requires Oscar `deploy.sh`.
