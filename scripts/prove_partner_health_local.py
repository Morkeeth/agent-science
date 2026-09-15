#!/usr/bin/env python3
"""Prove partner /health + /partners on private-workspace HTTP without deploy."""
from __future__ import annotations

import json
import os
import sys
import tempfile
import threading
import time
import urllib.request
from http.server import HTTPServer
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from cloud import partners
from cloud.service import Handler


def serve(port: int, *, hosted: bool) -> HTTPServer:
    env = {
        "AGENT_BUILDER": "1",
        "GCP_PROJECT": "hack-fleet",
        "PARALLEL_API_KEY": "pk-live-abc",
        "PORT": str(port),
    }
    if hosted:
        env.update({
            "AGENT_SCIENCE_HOSTED": "1",
            "AGENT_SCIENCE_ALLOW_HTTP": "1",
            "AGENT_SCIENCE_PUBLIC_ORIGIN": f"http://127.0.0.1:{port}",
            "AGENT_SCIENCE_ACCESS_CONFIG": json.dumps({
                "session_key": "s" * 48,
                "users": {},
            }),
            "AGENT_SCIENCE_WORKSPACE_DIR": tempfile.mkdtemp(),
        })
    else:
        for k in ("AGENT_SCIENCE_HOSTED", "K_SERVICE"):
            os.environ.pop(k, None)
    os.environ.update(env)
    return HTTPServer(("127.0.0.1", port), Handler)


def get(port: int, path: str):
    with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=5) as r:
        return r.status, json.loads(r.read().decode())


def main() -> None:
    with patch.object(partners.adk_agent, "adk_available", return_value=True), \
         patch.object(partners.adk_agent, "adk_version", return_value="2.7.1"), \
         patch.object(partners.parallel_search, "sdk_available", return_value=True), \
         patch.object(partners.parallel_search, "sdk_version", return_value="1.3.2"):
        for label, port, hosted in (("hosted-private-workspace", 8766, True),
                                    ("local-desk", 8767, False)):
            httpd = serve(port, hosted=hosted)
            threading.Thread(target=httpd.serve_forever, daemon=True).start()
            time.sleep(0.25)
            print(f"==== {label} ====")
            code, health = get(port, "/health")
            print("health", code, json.dumps(health, indent=2))
            assert health["engine_default"] == "adk"
            assert health["parallel"] is True
            assert health["gemini_path"].startswith("vertex:")
            if hosted:
                assert health["mode"] == "private-workspaces"
                pcode, partners_body = get(port, "/partners")
                print("partners", pcode, "checklist", partners_body["track_checklist"])
                assert partners_body["track_checklist"]["partner_health_public"] is True
            else:
                assert health.get("mode") == "local-desk"
            httpd.shutdown()
            httpd.server_close()
    print("LOCAL_PARTNER_HTTP_OK")


if __name__ == "__main__":
    main()
