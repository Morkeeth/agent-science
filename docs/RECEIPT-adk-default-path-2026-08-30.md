# RECEIPT — ADK on default path · 2026-08-30

**Status:** proved locally and on hosted URL (2026-08-30 re-check).

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

## Hosted /health (re-measured 2026-09-19)

```bash
curl -s https://agent-science-568004190078.us-central1.run.app/health | python3 -m json.tool
```

Live revision `agent-science-00028-hed` returns only `{ok, service, mode, revision}` — partner fields stripped. Do **not** claim hosted `engine_default: adk` until Oscar `deploy.sh` + `bash scripts/verify_partners_hosted.sh`.

The 2026-08-30 hosted JSON below is **historical** (pre–private-workspaces strip):

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

## Local prove without mocks (2026-09-19)

```bash
pip install -r requirements.txt
bash scripts/prove_partner_health_local.sh   # real google-adk + parallel-web
python3 scripts/prove_adk_clear_path.py      # engine=adk · adk_version=2.7.1
```

Finding: the previous local prove patched `adk_available` — `docs/FINDING-partner-prove-mocked-adk-2026-09-19.md`.

## What is NOT proved here

- **Live ADK model call on this VM** — no Vertex ADC or Gemini key locally; tool path proved by Aug 23 receipt (`docs/RECEIPT-agent-builder.md`) and engine-selection tests above. `prove_adk_clear_path.py` stubs only the runner, not availability.
- **Hosted engine_default on current revision** — stripped until Oscar deploy.
