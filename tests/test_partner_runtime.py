"""Partner integrations — prove all four partners are wired at import/call sites.

Does not call live APIs. Checks entrypoints exist and default path references them.
"""
from __future__ import annotations

import importlib
import inspect
import os
import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def t_gemini_entrypoint_exists():
    from clearance import gemini
    assert hasattr(gemini, "GeminiLocator")
    assert hasattr(gemini, "call")
    assert hasattr(gemini, "vertex_project")
    src = inspect.getsource(gemini.GeminiLocator.propose)
    assert "verify" not in src or "clearance.verify" not in src


def t_parallel_entrypoint_wired_in_facts():
    from clearance import facts, search
    assert hasattr(search, "find_sources")
    src = inspect.getsource(facts.judge_claim)
    assert "find_sources" in src
    assert "_search.find_sources" in src or "search.find_sources" in src


def t_gcp_service_health_shape():
    svc = importlib.import_module("cloud.service")
    src = inspect.getsource(svc)
    assert "engine_default" in src
    assert "gemini_path" in src or "parallel" in src
    assert "_run_clearance" in src


def t_adk_default_engine_wired():
    saved = os.environ.get("AGENT_BUILDER")
    try:
        os.environ["AGENT_BUILDER"] = "1"
        svc = importlib.reload(importlib.import_module("cloud.service"))
        from cloud import agent as adk_agent
        assert hasattr(adk_agent, "run_clearance")
        assert hasattr(adk_agent, "adk_available")
        with patch.object(adk_agent, "adk_available", return_value=True):
            with patch.object(adk_agent, "run_clearance", return_value={"engine": "adk"}):
                out = svc._run_clearance("x", "y", "m")
        assert out["engine"] == "adk"
    finally:
        if saved is None:
            os.environ.pop("AGENT_BUILDER", None)
        else:
            os.environ["AGENT_BUILDER"] = saved
        importlib.reload(importlib.import_module("cloud.service"))


def t_deploy_sh_secret_manager_not_plaintext_env():
    deploy = (ROOT / "deploy.sh").read_text()
    assert "--set-secrets" in deploy
    assert "PARALLEL_API_KEY" in deploy
    assert "parallel-api-key" in deploy or "PARALLEL_SECRET" in deploy
    # Gemini via ADC — no plaintext key in deploy env vars
    assert "GEMINI_API_KEY" not in deploy.split("--set-env-vars")[1].split("--set-secrets")[0]


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
