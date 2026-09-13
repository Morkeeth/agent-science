# RECEIPT — ADK on default path · 2026-08-30

**Status:** proved locally 2026-08-30; **re-proved 2026-09-13** via `bash scripts/verify_partners_local.sh` (`engine_default: adk`, `adk_version: 2.7.1`). Hosted `/health` must regain partner fields after Oscar redeploys the private-workspaces fix — see `docs/FINDING-hosted-partner-surfaces-2026-09-13.md`.

## What was verified

| Check | Command | Result |
|-------|---------|--------|
| Engine selection controls | `python3 tests/test_adk_default_path.py` | **5/5 passed** (re-run 2026-09-13) |
| ADK importable | `python3 -c "from importlib.metadata import version; print(version('google-adk'))"` | **2.7.1** (this VM 2026-09-13) |
| Local desk /health | `bash scripts/verify_partners_local.sh` | `"engine_default": "adk"` |
| Fallback stamps error | `t_run_clearance_falls_back_to_direct_and_stamps_error` | `engine: direct`, `adk_error` present |

## Local /health shape (this VM, 2026-09-13)

```bash
bash scripts/verify_partners_local.sh
```

```json
{
  "ok": true,
  "service": "agent-science",
  "gemini": true,
  "gemini_path": "vertex:hack-fleet",
  "parallel": false,
  "parallel_sdk": true,
  "parallel_sdk_version": "1.3.2",
  "parallel_transport": "parallel-web",
  "agent_builder": true,
  "adk_version": "2.7.1",
  "engine_default": "adk"
}
```

## Hosted /health (measured 2026-09-13 — RED for partners)

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

Partner fields absent until Oscar deploys the 2026-09-13 case_http fix. Historical 2026-08-30 hosted shape with `engine_default: adk` is **not** the current revision.

## What is NOT proved here

- **Live ADK model call on this VM** — no Vertex ADC or Gemini key locally; tool path proved by engine-selection tests and Aug 23 receipt (`docs/RECEIPT-agent-builder.md`).
- **Hosted partner health green** — blocked on Oscar `deploy.sh`.
