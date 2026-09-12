#!/usr/bin/env python3
"""Cold-clone partner surface prove — no network, no API keys required.

Spins a local WorkspaceHTTP (AGENT_SCIENCE_HOSTED=1) and asserts:
  GET /health  → partner fields + mode=private-workspaces + engine_default:adk
  GET /partners → track checklist
  POST /api/clear without token → 401 (private boundary held)
  POST /clear without token → 401 (legacy public clear stays closed)

Done-when (must be RUN):
  PYTHONPATH=. python3 scripts/prove_partner_surfaces_local.py
"""
from __future__ import annotations

import hashlib
import http.client
import json
import os
import sys
import tempfile
import threading
from http.server import HTTPServer
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

TOKEN = "a" * 48
CONFIG = {
    "session_key": "s" * 48,
    "users": {"alice": hashlib.sha256(TOKEN.encode()).hexdigest()},
}


def main() -> int:
    from cloud.service import Handler

    temp = tempfile.TemporaryDirectory()
    env = {
        "AGENT_SCIENCE_HOSTED": "1",
        "AGENT_SCIENCE_ALLOW_HTTP": "1",
        "AGENT_SCIENCE_PUBLIC_ORIGIN": "http://127.0.0.1:9",
        "AGENT_SCIENCE_ACCESS_CONFIG": json.dumps(CONFIG),
        "AGENT_SCIENCE_WORKSPACE_DIR": temp.name,
        "AGENT_BUILDER": "1",
        "GCP_PROJECT": "hack-fleet",
        "GOOGLE_CLOUD_PROJECT": "hack-fleet",
        "GOOGLE_CLOUD_LOCATION": "global",
        "PARALLEL_API_KEY": "pk-local-prove-not-a-real-key",
    }
    with patch.dict(os.environ, env, clear=False), \
            patch("cloud.agent.adk_available", return_value=True), \
            patch("cloud.agent.adk_version", return_value="2.7.1"):
        server = HTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        port = server.server_port
        try:
            health = _get(port, "/health")
            partners = _get(port, "/partners")
            clear_anon = _post(port, "/api/clear", {"request_id": "x" * 16, "script": "s"})
            legacy_anon = _post(port, "/clear", {"script": "s"})
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)
            temp.cleanup()

    print("health:", json.dumps(health, sort_keys=True))
    needed = ("gemini", "parallel", "parallel_sdk", "agent_builder", "engine_default", "gemini_path")
    missing = [k for k in needed if k not in health]
    assert not missing, f"stripped health missing {missing}: {health}"
    assert health.get("ok") is True
    assert health.get("mode") == "private-workspaces"
    assert health.get("engine_default") == "adk"
    assert health.get("gemini") is True
    assert str(health.get("gemini_path", "")).startswith("vertex:")
    assert health.get("parallel") is True
    assert health.get("agent_builder") is True

    tc = partners.get("track_checklist") or {}
    assert tc.get("hosted_url_required") is True
    assert tc.get("clearance_requires_workspace_token") is True
    assert (partners.get("partners") or {}).get("agent_builder_adk", {}).get("engine_default") == "adk"
    print("partners checklist:", json.dumps(tc, sort_keys=True))

    assert clear_anon[0] == 401, clear_anon
    assert legacy_anon[0] == 401, legacy_anon
    print("boundary: /api/clear and /clear anonymous → 401")
    print("PROVE OK — partner surfaces local (no network)")
    return 0


def _get(port: int, path: str):
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=10)
    conn.request("GET", path, headers={})
    resp = conn.getresponse()
    body = resp.read().decode()
    code = resp.status
    conn.close()
    assert code == 200, (path, code, body[:200])
    return json.loads(body)


def _post(port: int, path: str, data: dict):
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=10)
    raw = json.dumps(data).encode()
    conn.request("POST", path, raw, {"Content-Type": "application/json"})
    resp = conn.getresponse()
    code = resp.status
    body = resp.read().decode()
    conn.close()
    return code, body


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print("PROVE FAIL:", exc, file=sys.stderr)
        raise SystemExit(1)
