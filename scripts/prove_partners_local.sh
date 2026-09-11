#!/usr/bin/env bash
# Local partner proof — no Cloud Run deploy required.
# Spins a temporary private-workspaces server and asserts partner fields.
# Also proves ADK default selection when Agent Builder is configured.
#
# Usage: bash scripts/prove_partners_local.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
STAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "=== prove_partners_local === $STAMP"

python3 - <<'PY'
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

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT))

from cloud.service import Handler  # noqa: E402
from cloud import partners as pm  # noqa: E402

TOKEN = "a" * 48
CONFIG = {
    "session_key": "s" * 48,
    "users": {"alice": hashlib.sha256(TOKEN.encode()).hexdigest()},
}


def get(path: str) -> tuple[int, object]:
    with tempfile.TemporaryDirectory() as tmp:
        merged = {
            "AGENT_SCIENCE_HOSTED": "1",
            "AGENT_SCIENCE_ALLOW_HTTP": "1",
            "AGENT_SCIENCE_PUBLIC_ORIGIN": "http://127.0.0.1",
            "AGENT_SCIENCE_ACCESS_CONFIG": json.dumps(CONFIG),
            "AGENT_SCIENCE_WORKSPACE_DIR": tmp,
            "GCP_PROJECT": "hack-fleet",
            "PARALLEL_API_KEY": "pk-local-proof-not-live",
            "AGENT_BUILDER": "1",
        }
        with patch.dict(os.environ, merged, clear=False):
            server = HTTPServer(("127.0.0.1", 0), Handler)
            threading.Thread(target=server.handle_request, daemon=True).start()
            conn = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
            conn.request("GET", path)
            resp = conn.getresponse()
            raw = resp.read().decode()
            code = resp.status
            conn.close()
            server.server_close()
            try:
                return code, json.loads(raw)
            except json.JSONDecodeError:
                return code, raw


def post_clear_anon() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        merged = {
            "AGENT_SCIENCE_HOSTED": "1",
            "AGENT_SCIENCE_ALLOW_HTTP": "1",
            "AGENT_SCIENCE_PUBLIC_ORIGIN": "http://127.0.0.1",
            "AGENT_SCIENCE_ACCESS_CONFIG": json.dumps(CONFIG),
            "AGENT_SCIENCE_WORKSPACE_DIR": tmp,
        }
        with patch.dict(os.environ, merged, clear=False):
            server = HTTPServer(("127.0.0.1", 0), Handler)
            threading.Thread(target=server.handle_request, daemon=True).start()
            conn = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
            payload = json.dumps({"script": "x", "subject": "y"}).encode()
            conn.request(
                "POST",
                "/clear",
                payload,
                {"Content-Type": "application/json", "Content-Length": str(len(payload))},
            )
            resp = conn.getresponse()
            code = resp.status
            resp.read()
            conn.close()
            server.server_close()
            return code


code, health = get("/health")
assert code == 200, health
required = [
    "gemini", "parallel", "parallel_sdk", "agent_builder",
    "engine_default", "gemini_path", "mode",
]
missing = [k for k in required if k not in health]
assert not missing, f"missing {missing} in {health}"
assert health["mode"] == "private-workspaces"
assert health["gemini"] is True
assert health["parallel"] is True
assert health["gemini_path"] == "vertex:hack-fleet"
assert health["engine_default"] in ("adk", "direct")
print("local hosted /health OK")
print(json.dumps({k: health[k] for k in required + ["adk_version", "revision"]}, indent=2))

code, partners = get("/partners")
assert code == 200, partners
tc = partners.get("track_checklist") or {}
for key in (
    "parallel_search_at_runtime",
    "gemini_at_runtime",
    "adk_agent_builder",
    "hosted_url_required",
):
    assert key in tc, partners
print("local hosted /partners OK")

code = post_clear_anon()
assert code == 401, f"anonymous /clear must be 401, got {code}"
print("anonymous /clear stays 401 OK")

with patch("cloud.agent.adk_available", return_value=True), patch(
    "cloud.agent.adk_version", return_value="2.7.1"
):
    h = pm.health_payload(mode="private-workspaces", revision="proof")
assert h["engine_default"] == "adk"
assert h["agent_builder"] is True
print("ADK default path selected when configured OK → engine_default=adk")
print("PROVE_PARTNERS_LOCAL OK")
PY

echo "=== prove_partners_local done === $STAMP"
