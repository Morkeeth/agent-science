#!/usr/bin/env python3
"""Prove ADK is selected on the /clear engine path — real packages, no live model.

Uses the real google-adk import for availability, then stubs only the network
runner so we do not spend Gemini. engine must be stamped adk.

Usage: python3 scripts/prove_adk_clear_path.py
"""
from __future__ import annotations

import importlib
import json
import os
import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> int:
    from cloud import agent as adk_agent

    if not adk_agent.adk_available():
        print("RED: google-adk not importable — pip install -r requirements.txt")
        return 1
    version = adk_agent.adk_version()
    if version != "2.7.1":
        print(f"RED: expected google-adk==2.7.1, got {version!r}")
        return 1

    os.environ["AGENT_BUILDER"] = "1"
    os.environ.setdefault("GCP_PROJECT", "hack-fleet")
    svc = importlib.reload(importlib.import_module("cloud.service"))

    fake = {
        "ok": True,
        "engine": "adk",
        "adk_version": version,
        "claims_extracted": 1,
        "adk_tool_calls": ["clear_script_tool"],
    }
    # Real availability; only the live runner is stubbed.
    assert adk_agent.adk_available() is True
    with patch.object(svc.adk_agent, "run_clearance", return_value=dict(fake)) as run:
        out = svc._run_clearance(
            "In Zephyr-prove the Archive passed Regulation Z for orphan media.",
            "adk-prove",
            "gemini-3.5-flash-lite",
        )
    run.assert_called_once()
    assert out.get("engine") == "adk", out
    assert out.get("adk_version") == version, out

    receipt = {
        "engine": out["engine"],
        "adk_version": out.get("adk_version"),
        "adk_tool_calls": out.get("adk_tool_calls"),
        "claims_extracted": out.get("claims_extracted"),
        "adk_available_real": True,
        "runner": "stubbed-no-network",
    }
    print(json.dumps(receipt, indent=2))
    print("PROVE_ADK_CLEAR_PATH OK · engine=adk · real google-adk import")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
