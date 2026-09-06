"""Hosted partner public surface — health fields + /partners without auth."""
from __future__ import annotations

import hashlib
import http.client
import json
import os
import tempfile
import threading
import unittest
from http.server import HTTPServer
from unittest.mock import patch

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from cloud.service import Handler

TOKEN = "a" * 48
CONFIG = {
    "session_key": "s" * 48,
    "users": {"alice": hashlib.sha256(TOKEN.encode()).hexdigest()},
}
ORIGIN = "http://127.0.0.1:8771"


class HostedPartnerSurface(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.env = patch.dict(
            os.environ,
            {
                "AGENT_SCIENCE_HOSTED": "1",
                "AGENT_SCIENCE_ALLOW_HTTP": "1",
                "AGENT_SCIENCE_PUBLIC_ORIGIN": ORIGIN,
                "AGENT_SCIENCE_ACCESS_CONFIG": json.dumps(CONFIG),
                "AGENT_SCIENCE_WORKSPACE_DIR": self.temp.name,
                "PARALLEL_API_KEY": "pk-test-not-live",
                "GCP_PROJECT": "hack-fleet",
                "AGENT_BUILDER": "1",
            },
            clear=False,
        )
        self.env.start()
        self.server = HTTPServer(("127.0.0.1", 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
        self.env.stop()
        self.temp.cleanup()

    def request(self, method, path, data=None, *, token=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=10)
        h = {"Content-Type": "application/json"}
        if token:
            h["Authorization"] = "Bearer " + token
        body = json.dumps(data).encode() if data is not None else None
        conn.request(method, path, body, h)
        response = conn.getresponse()
        code = response.status
        fields = dict(response.getheaders())
        text = response.read().decode()
        conn.close()
        payload = (
            json.loads(text)
            if "application/json" in fields.get("Content-Type", "")
            else text
        )
        return code, fields, payload

    def test_health_exposes_partner_fields_without_auth(self):
        code, _, health = self.request("GET", "/health")
        self.assertEqual(code, 200)
        self.assertTrue(health["ok"])
        self.assertEqual(health["mode"], "private-workspaces")
        for key in (
            "gemini",
            "gemini_path",
            "parallel",
            "parallel_sdk",
            "agent_builder",
            "engine_default",
        ):
            self.assertIn(key, health, f"missing {key} — liveness-only health is a false green")
        self.assertTrue(health["parallel"])
        self.assertEqual(health["clearance_desk"], "local-only")
        self.assertIn("find_sources", health["hosted_parallel_path"])

    def test_partners_public_without_auth(self):
        code, _, body = self.request("GET", "/partners")
        self.assertEqual(code, 200)
        self.assertIn("partners", body)
        self.assertTrue(body["track_checklist"]["public_partner_health"])
        self.assertTrue(body["track_checklist"]["unauthenticated_clear_local_only"])

    def test_clear_still_requires_workspace_access(self):
        code, _, _ = self.request("POST", "/clear", {"script": "x", "subject": "y"})
        self.assertEqual(code, 401)


if __name__ == "__main__":
    unittest.main()
