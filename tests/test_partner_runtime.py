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
    assert hasattr(search, "integration_info")
    assert hasattr(search, "last_search_id")
    src = inspect.getsource(facts.judge_claim)
    assert "find_sources" in src
    assert "_search.find_sources" in src or "search.find_sources" in src


def t_gcp_service_health_shape():
    svc = importlib.import_module("cloud.service")
    src = inspect.getsource(svc)
    assert "health_payload" in src
    assert "_run_clearance" in src
    from cloud import partners
    with patch.dict(os.environ, {"AGENT_BUILDER": "1", "GCP_PROJECT": "hack-fleet",
                                 "PARALLEL_API_KEY": "pk-test"}):
        with patch.object(partners.adk_agent, "adk_available", return_value=True):
            with patch.object(partners.adk_agent, "adk_version", return_value="2.7.1"):
                payload = partners.health_payload(mode="private-workspaces", revision="r1")
    for key in ("ok", "gemini", "parallel", "agent_builder", "engine_default",
                "gemini_path", "mode", "revision"):
        assert key in payload, payload
    assert payload["engine_default"] == "adk"
    assert payload["mode"] == "private-workspaces"


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


def t_partner_manifest_survives_cold_start():
    """The Parallel proof must not read as unused on a fresh instance.

    live_calls/last_search_id are per-process. This control asserts the manifest
    also carries receipt-backed fields, and that they go red when the log has no
    real search_id. Added 2026-09-04.
    """
    import json
    import tempfile
    from clearance import search

    info = search.integration_info()
    for field in ("last_verified_utc", "verified_search_id", "verified_calls_logged"):
        assert field in info, f"{field} missing from /partners manifest"

    real = search.RECEIPTS
    try:
        d = Path(tempfile.mkdtemp())

        # Red 1: no log at all.
        search.RECEIPTS = d / "absent.jsonl"
        out = search.last_verified_receipt()
        assert out["verified_search_id"] is None
        assert out["verified_calls_logged"] == 0

        # Red 2: receipts exist but none carry a real search_id, plus a bad line.
        log = d / "no_ids.jsonl"
        log.write_text(
            json.dumps({"at": "2026-01-01T00:00:00+00:00", "source": "parallel", "search_id": None})
            + "\n{ this is not json\n"
        )
        search.RECEIPTS = log
        out = search.last_verified_receipt()
        assert out["verified_search_id"] is None, "a cache-hit receipt is not proof of a live call"
        assert out["verified_calls_logged"] == 0

        # Green: one real receipt, and the LAST one wins.
        log = d / "ids.jsonl"
        log.write_text(
            json.dumps({"at": "2026-01-01T00:00:00+00:00", "source": "parallel", "search_id": "search_old"})
            + "\n"
            + json.dumps({"at": "2026-02-02T00:00:00+00:00", "source": "parallel", "search_id": "search_new"})
            + "\n"
        )
        search.RECEIPTS = log
        out = search.last_verified_receipt()
        assert out["verified_search_id"] == "search_new"
        assert out["last_verified_utc"] == "2026-02-02T00:00:00+00:00"
        assert out["verified_calls_logged"] == 2
    finally:
        search.RECEIPTS = real


def t_requirements_pins_parallel_web():
    req = (ROOT / "requirements.txt").read_text()
    assert "parallel-web==" in req
    assert "google-adk==" in req


def _urllib_rest_health() -> dict:
    """Working Parallel via REST fallback — SDK wheel absent, key present."""
    return {
        "ok": True,
        "service": "agent-science",
        "gemini": True,
        "gemini_path": "vertex:hack-fleet",
        "parallel": True,
        "parallel_sdk": False,
        "parallel_sdk_version": None,
        "parallel_transport": "urllib-rest",
        "agent_builder": True,
        "engine_default": "adk",
    }


def t_shipping_health_accepts_urllib_rest_without_sdk():
    """SDK assert must not false-red a callable urllib-rest Parallel path.

    FINDING-parallel-sdk-assert-vs-urllib-2026-09-23: verify required
    parallel_sdk=True even when parallel=True and transport=urllib-rest.
    """
    from cloud.partners import shipping_health_ok

    ok, why = shipping_health_ok(_urllib_rest_health())
    assert ok, f"urllib-rest with key must be shipping-green, got: {why}"


def t_shipping_health_still_reds_stripped_or_uncallable_parallel():
    from cloud.partners import shipping_health_ok

    stripped = {"ok": True, "service": "agent-science", "mode": "private-workspaces"}
    ok, why = shipping_health_ok(stripped)
    assert not ok, "stripped health must stay red"
    assert "gemini" in why or "parallel" in why

    no_key = dict(_urllib_rest_health())
    no_key["parallel"] = False
    ok, why = shipping_health_ok(no_key)
    assert not ok, "parallel=false must stay red"
    assert "parallel" in why

    sdk_path = dict(_urllib_rest_health())
    sdk_path["parallel_sdk"] = True
    sdk_path["parallel_transport"] = "parallel-web"
    ok, why = shipping_health_ok(sdk_path)
    assert ok, f"SDK transport must stay green, got: {why}"


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
