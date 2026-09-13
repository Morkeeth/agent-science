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
    assert "engine_default" in src or "health_payload" in src
    assert "gemini_path" in src or "health_payload" in src or "parallel" in src
    assert "_run_clearance" in src
    from cloud import partners
    with patch.object(partners.adk_agent, "adk_available", return_value=True):
        with patch.object(partners.adk_agent, "adk_version", return_value="2.7.1"):
            with patch.dict(os.environ, {"AGENT_BUILDER": "1", "GCP_PROJECT": "hack-fleet"}, clear=False):
                payload = partners.health_payload()
    assert payload["engine_default"] == "adk"
    assert payload["gemini"] is True
    assert payload["gemini_path"].startswith("vertex:")


def t_hosted_private_workspaces_exposes_partner_health_and_partners():
    """Hosted mode must not strip partner fields from /health or gate /partners.

    Measured RED on 2026-09-13 against rev agent-science-00028-hed before this fix:
    /health returned only ok/service/mode/revision; /partners returned 303 to login.
    """
    import hashlib
    import http.client
    import json
    import tempfile
    import threading
    from http.server import HTTPServer

    from cloud.service import Handler

    token = "a" * 48
    config = {
        "session_key": "s" * 48,
        "users": {"alice": hashlib.sha256(token.encode()).hexdigest()},
    }
    origin = "http://127.0.0.1:18770"
    temp = tempfile.TemporaryDirectory()
    env = patch.dict(
        os.environ,
        {
            "AGENT_SCIENCE_HOSTED": "1",
            "AGENT_SCIENCE_ALLOW_HTTP": "1",
            "AGENT_SCIENCE_PUBLIC_ORIGIN": origin,
            "AGENT_SCIENCE_ACCESS_CONFIG": json.dumps(config),
            "AGENT_SCIENCE_WORKSPACE_DIR": temp.name,
            "AGENT_BUILDER": "1",
            "GCP_PROJECT": "hack-fleet",
            "PARALLEL_API_KEY": "pk-live-abc-fixture",
        },
        clear=False,
    )
    env.start()
    server = HTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        from cloud import partners

        with patch.object(partners.adk_agent, "adk_available", return_value=True):
            with patch.object(partners.adk_agent, "adk_version", return_value="2.7.1"):
                conn = http.client.HTTPConnection(
                    "127.0.0.1", server.server_port, timeout=10
                )
                conn.request("GET", "/health")
                resp = conn.getresponse()
                health = json.loads(resp.read().decode())
                assert resp.status == 200, health
                assert health.get("mode") == "private-workspaces", health
                assert health.get("engine_default") == "adk", health
                assert health.get("gemini") is True, health
                assert health.get("parallel") is True, health
                assert health.get("agent_builder") is True, health
                conn.close()

                conn = http.client.HTTPConnection(
                    "127.0.0.1", server.server_port, timeout=10
                )
                conn.request("GET", "/partners")
                resp = conn.getresponse()
                body = json.loads(resp.read().decode())
                assert resp.status == 200, body
                assert "partners" in body, body
                assert body["track_checklist"]["adk_agent_builder"] is True
                conn.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join()
        env.stop()
        temp.cleanup()


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
