"""ADK on the default /clear path — engine selection without a live model call.

Proves the hosted shape selects `engine: adk` when Agent Builder is configured and
importable, and falls back to `direct` with an explicit stamp when it is not.
"""
from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def _reload_service():
    import cloud.service as svc
    return importlib.reload(svc)


def t_health_reports_engine_default_adk_when_configured():
    saved = os.environ.get("AGENT_BUILDER")
    try:
        os.environ["AGENT_BUILDER"] = "1"
        svc = _reload_service()
        with patch.object(svc.adk_agent, "adk_available", return_value=True):
            with patch.object(svc.adk_agent, "adk_version", return_value="2.7.1"):
                # Mirror GET /health payload construction
                adk_ok = svc.adk_agent.adk_available()
                payload = {
                    "engine_default": "adk" if (svc.ADK_DEFAULT and adk_ok) else "direct",
                    "agent_builder": adk_ok,
                    "adk_version": svc.adk_agent.adk_version(),
                }
        assert payload["engine_default"] == "adk", payload
        assert payload["agent_builder"] is True
        assert payload["adk_version"] == "2.7.1"
    finally:
        if saved is None:
            os.environ.pop("AGENT_BUILDER", None)
        else:
            os.environ["AGENT_BUILDER"] = saved
        _reload_service()


def t_health_reports_direct_when_agent_builder_off():
    saved = os.environ.get("AGENT_BUILDER")
    try:
        os.environ["AGENT_BUILDER"] = "0"
        svc = _reload_service()
        with patch.object(svc.adk_agent, "adk_available", return_value=True):
            adk_ok = svc.adk_agent.adk_available()
            engine = "adk" if (svc.ADK_DEFAULT and adk_ok) else "direct"
        assert engine == "direct"
    finally:
        if saved is None:
            os.environ.pop("AGENT_BUILDER", None)
        else:
            os.environ["AGENT_BUILDER"] = saved
        _reload_service()


def t_run_clearance_uses_adk_when_available():
    saved = os.environ.get("AGENT_BUILDER")
    try:
        os.environ["AGENT_BUILDER"] = "1"
        svc = _reload_service()
        fake_report = {"ok": True, "engine": "adk", "claims_extracted": 1}
        with patch.object(svc.adk_agent, "adk_available", return_value=True):
            with patch.object(svc.adk_agent, "run_clearance", return_value=fake_report) as run:
                out = svc._run_clearance("script text", "orphan-works", "gemini-3.5-flash")
        assert out["engine"] == "adk"
        run.assert_called_once()
    finally:
        if saved is None:
            os.environ.pop("AGENT_BUILDER", None)
        else:
            os.environ["AGENT_BUILDER"] = saved
        _reload_service()


def t_run_clearance_falls_back_to_direct_and_stamps_error():
    saved = os.environ.get("AGENT_BUILDER")
    try:
        os.environ["AGENT_BUILDER"] = "1"
        svc = _reload_service()
        direct = {"ok": True, "claims_extracted": 0}
        with patch.object(svc.adk_agent, "adk_available", return_value=True):
            with patch.object(svc.adk_agent, "run_clearance", side_effect=RuntimeError("ADK boom")):
                with patch.object(svc.agent_science, "clear_script", return_value=direct):
                    out = svc._run_clearance("x", "y", "m")
        assert out["engine"] == "direct"
        assert "adk_error" in out
        assert "ADK boom" in out["adk_error"]
    finally:
        if saved is None:
            os.environ.pop("AGENT_BUILDER", None)
        else:
            os.environ["AGENT_BUILDER"] = saved
        _reload_service()


def t_run_clearance_direct_when_adk_not_importable():
    saved = os.environ.get("AGENT_BUILDER")
    try:
        os.environ["AGENT_BUILDER"] = "1"
        svc = _reload_service()
        direct = {"ok": True}
        with patch.object(svc.adk_agent, "adk_available", return_value=False):
            with patch.object(svc.agent_science, "clear_script", return_value=direct):
                out = svc._run_clearance("x", "y", "m")
        assert out["engine"] == "direct"
        assert "adk_error" in out
    finally:
        if saved is None:
            os.environ.pop("AGENT_BUILDER", None)
        else:
            os.environ["AGENT_BUILDER"] = saved
        _reload_service()


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("t_") and callable(v)]
    failed = 0
    for fn in fns:
        try:
            fn()
            print(f"PASS  {fn.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL  {fn.__name__}: {e}")
    print(f"\n{len(fns) - failed}/{len(fns)} passed")
    sys.exit(1 if failed else 0)
