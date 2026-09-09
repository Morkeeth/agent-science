# RECEIPT — ADK on default path · 2026-08-30

**Status:** proved locally 2026-09-09 (dual-surface + real `google-adk` 2.7.1). Hosted live still stripped until Oscar deploys.

## What was verified

| Check | Command | Result |
|-------|---------|--------|
| Engine selection controls | `python3 tests/test_adk_default_path.py` | **5/5 passed** |
| ADK importable | `python3 -c "from cloud import agent as a; print(a.adk_available(), a.adk_version())"` | **True 2.7.1** |
| Dual-surface `/health` | `bash scripts/demo_partner_dual_surface.sh` | `"engine_default": "adk"`, `"mode": "private-workspaces+public-desk"` |
| `partner_status.health_payload` | object call after pip install | `"engine_default": "adk"`, `"agent_builder": true` |
| Fallback stamps error | `t_run_clearance_falls_back_to_direct_and_stamps_error` | `engine: direct`, `adk_error` present |

## Local dual-surface /health (2026-09-09)

```bash
bash scripts/demo_partner_dual_surface.sh
```

```json
{
  "mode": "private-workspaces+public-desk",
  "gemini_path": "vertex:hack-fleet",
  "agent_builder": true,
  "adk_version": "2.7.1",
  "engine_default": "adk",
  "public_desk": true
}
```

Hosted `00028-hed` still lacks these fields — see `docs/FINDING-hosted-partner-strip-still-dark-2026-09-09.md`.

## Local /health shape (this VM, no ADC) — original 2026-08-30 control

```bash
python3 - <<'PY'
import os, json
from unittest.mock import patch
os.environ["AGENT_BUILDER"] = "1"
os.environ["GCP_PROJECT"] = "hack-fleet"
import importlib
from cloud import service as svc
importlib.reload(svc)
with patch.object(svc.adk_agent, "adk_available", return_value=True):
    with patch.object(svc.adk_agent, "adk_version", return_value="2.7.1"):
        adk_ok = svc.adk_agent.adk_available()
        print(json.dumps({
            "ok": True,
            "service": "agent-science",
            "agent_builder": adk_ok,
            "adk_version": svc.adk_agent.adk_version(),
            "engine_default": "adk" if (svc.ADK_DEFAULT and adk_ok) else "direct",
        }, indent=2))
PY
```

Output on this run:

```json
{
  "ok": true,
  "service": "agent-science",
  "agent_builder": true,
  "adk_version": "2.7.1",
  "engine_default": "adk"
}
```

## Hosted /health (measured 2026-08-30)

```bash
curl -s https://agent-science-568004190078.us-central1.run.app/health | python3 -m json.tool
```

```json
{
  "ok": true,
  "service": "agent-science",
  "gemini": true,
  "gemini_path": "vertex:hack-fleet",
  "parallel": true,
  "agent_builder": true,
  "adk_version": "2.7.1",
  "engine_default": "adk"
}
```

## What is NOT proved here

- **Live ADK model call on this VM** — no Vertex ADC or Gemini key locally; tool path proved by Aug 23 receipt (`docs/RECEIPT-agent-builder.md`) and engine-selection tests above.
