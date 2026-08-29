# RECEIPT — ADK on default path · 2026-08-30

**Status:** proved locally in the hosted shape. **Not on hosted URL** — `deploy.sh` is Oscar's click.

## What was verified

| Check | Command | Result |
|-------|---------|--------|
| Engine selection controls | `python3 tests/test_adk_default_path.py` | **5/5 passed** |
| ADK importable in image dep | `python3 -c "from importlib.metadata import version; print(version('google-adk'))"` | **2.7.1** |
| `/health` engine_default logic | same test suite mocks `adk_available()` | `"engine_default": "adk"` when `AGENT_BUILDER=1` |
| Fallback stamps error | `t_run_clearance_falls_back_to_direct_and_stamps_error` | `engine: direct`, `adk_error` present |

## Local /health shape (this VM, no ADC)

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

## What is NOT proved here

- **Hosted URL** — prior revision at `agent-science-568004190078.us-central1.run.app` lacks `engine_default`.
- **Live ADK model call** — no Vertex ADC or Gemini key on this VM; tool path proved by Aug 23 receipt (`docs/RECEIPT-agent-builder.md`) and engine-selection tests above.

## Done-when for slice 5 (hosted)

```bash
curl -s https://agent-science-568004190078.us-central1.run.app/health \
  | grep -q '"engine_default": "adk"' && echo slice-5-hosted || echo still-blocked-on-deploy
```

Oscar runs `deploy.sh` once; agent does not.
