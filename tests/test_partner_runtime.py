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


def adk_agent_mod():
    from cloud import agent as adk_agent
    return adk_agent


def t_partner_health_exposes_engine_and_parallel_fields():
    """Stripped private-workspace health is the defect this control catches."""
    from cloud import partners

    with patch.dict(
        os.environ,
        {"AGENT_BUILDER": "1", "GCP_PROJECT": "hack-fleet", "PARALLEL_API_KEY": "pk-test"},
        clear=False,
    ):
        with patch.object(adk_agent_mod(), "adk_available", return_value=True):
            with patch.object(adk_agent_mod(), "adk_version", return_value="2.7.1"):
                h = partners.health(mode="private-workspaces", revision="local-test")
    for field in (
        "ok",
        "gemini",
        "gemini_path",
        "parallel",
        "parallel_sdk",
        "agent_builder",
        "engine_default",
        "mode",
        "revision",
    ):
        assert field in h, f"missing {field}"
    assert h["mode"] == "private-workspaces"
    assert h["engine_default"] == "adk"
    assert h["gemini_path"].startswith("vertex:")
    assert h["parallel"] is True


def t_naive_ok_only_arm_greens_stripped_liveness():
    """Baseline arm any team ships in two hours — GREEN on the defect payload.

    Measured 2026-09-07 and again 2026-09-12 against live Cloud Run: docs that
    only checked ok/service stayed green while partner fields were gone. This
    control freezes that failure mode so we cannot forget it.
    """
    sys.path.insert(0, str(ROOT / "scripts"))
    import watch_hosted_partner_health as watch

    stripped = {
        "ok": True,
        "service": "agent-science",
        "mode": "private-workspaces",
        "revision": "agent-science-00028-hed",
    }
    assert watch.naive_ok_only(stripped) is True
    ok, missing = watch.partner_admissible(stripped)
    assert ok is False
    assert "engine_default" in missing
    assert "gemini" in missing
    assert "parallel" in missing


def t_partner_manifest_checklist_not_hardcoded_true_without_wiring():
    from cloud import partners

    saved = os.environ.pop("PARALLEL_API_KEY", None)
    try:
        with patch.dict(os.environ, {"AGENT_BUILDER": "0"}, clear=False):
            with patch(
                "clearance.search.last_verified_receipt",
                return_value={
                    "verified_search_id": None,
                    "verified_calls_logged": 0,
                    "last_verified_utc": None,
                },
            ):
                with patch.object(adk_agent_mod(), "adk_available", return_value=False):
                    m = partners.manifest(gemini_path="none", adk_default=False)
        tc = m["track_checklist"]
        assert tc["parallel_search_at_runtime"] is False
        assert tc["gemini_at_runtime"] is False
        assert tc["adk_agent_builder"] is False
        assert tc["clearance_requires_workspace_token"] is True
    finally:
        if saved is not None:
            os.environ["PARALLEL_API_KEY"] = saved


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
    assert "partners" in src or "engine_default" in src
    assert "_run_clearance" in src
    from cloud import partners
    assert callable(partners.health)


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
    env_block = deploy.split("--set-env-vars")[1].split("--set-secrets")[0]
    assert "GEMINI_API_KEY" not in env_block
    assert "AGENT_BUILDER=1" in env_block
    assert "GCP_PROJECT=" in env_block
    assert "GOOGLE_CLOUD_LOCATION=global" in env_block


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

        search.RECEIPTS = d / "absent.jsonl"
        out = search.last_verified_receipt()
        assert out["verified_search_id"] is None
        assert out["verified_calls_logged"] == 0

        log = d / "no_ids.jsonl"
        log.write_text(
            json.dumps({"at": "2026-01-01T00:00:00+00:00", "source": "parallel", "search_id": None})
            + "\n{ this is not json\n"
        )
        search.RECEIPTS = log
        out = search.last_verified_receipt()
        assert out["verified_search_id"] is None, "a cache-hit receipt is not proof of a live call"
        assert out["verified_calls_logged"] == 0

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


def t_case_http_exposes_public_partner_routes():
    src = (ROOT / "cloud" / "case_http.py").read_text()
    assert "partner_surface.health" in src
    assert "partner_surface.manifest" in src
    assert "def clear_script" in src
    assert "/api/clear" in src or "base == '/clear'" in src


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
