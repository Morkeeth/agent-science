"""Hosted dual surface — partner proof must survive AGENT_SCIENCE_HOSTED=1.

Control history: revision agent-science-00026-zel served a stripped /health
(ok/service/mode/revision only). verify_partners_hosted.sh went red at the object.
These tests fail if that regression returns.
"""
from __future__ import annotations

import hashlib
import http.client
import json
import os
import sys
import tempfile
import threading
import unittest
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
ORIGIN = "http://127.0.0.1:8771"


class HostedPartnerSurfaces(unittest.TestCase):
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
                "AGENT_BUILDER": "1",
                "GCP_PROJECT": "hack-fleet",
                "PARALLEL_API_KEY": "pk-test-not-a-real-key",
                "K_REVISION": "test-dual-surface",
            },
            clear=False,
        )
        self.env.start()
        from cloud.service import Handler

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
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = "Bearer " + token
        body = json.dumps(data).encode() if data is not None else None
        conn.request(method, path, body, headers)
        response = conn.getresponse()
        code = response.status
        ctype = response.getheader("Content-Type") or ""
        text = response.read().decode()
        conn.close()
        payload = json.loads(text) if "application/json" in ctype else text
        return code, payload

    def test_anonymous_health_reports_all_four_partners(self):
        from cloud import agent as adk_agent

        with patch.object(adk_agent, "adk_available", return_value=True):
            with patch.object(adk_agent, "adk_version", return_value="2.7.1"):
                code, health = self.request("GET", "/health")
        self.assertEqual(code, 200, health)
        for field in (
            "gemini",
            "gemini_path",
            "parallel",
            "parallel_sdk",
            "agent_builder",
            "engine_default",
        ):
            self.assertIn(field, health, f"{field} missing from hosted /health — partner strip regression")
        self.assertTrue(health["gemini"])
        self.assertTrue(str(health["gemini_path"]).startswith("vertex:"))
        self.assertTrue(health["parallel"])
        self.assertEqual(health["engine_default"], "adk")
        self.assertEqual(health["mode"], "private-workspaces+public-desk")
        self.assertTrue(health.get("public_desk"))

    def test_anonymous_partners_manifest(self):
        from cloud import agent as adk_agent

        with patch.object(adk_agent, "adk_available", return_value=True):
            code, body = self.request("GET", "/partners")
        self.assertEqual(code, 200, body)
        self.assertIsInstance(body, dict)
        tc = body.get("track_checklist") or {}
        self.assertTrue(tc.get("hosted_url_required"))
        self.assertIn("partners", body)
        self.assertIn("parallel", body["partners"])
        self.assertIn("agent_builder_adk", body["partners"])

    def test_anonymous_clear_reaches_desk_not_workspace_auth(self):
        """Public /clear must not 401 behind workspace login on hosted."""
        from cloud import service as svc

        fake = {
            "ok": True,
            "engine": "adk",
            "claims_extracted": 1,
            "parallel_calls": 1,
            "corpus_hits": 0,
            "sourced": 0,
            "unsourced": 1,
        }
        with patch.object(svc, "_run_clearance", return_value=fake):
            code, body = self.request(
                "POST",
                "/clear",
                {"script": "Directive 2012/28/EU covers orphan works.", "subject": "dual-surface"},
            )
        self.assertEqual(code, 200, body)
        self.assertEqual(body.get("engine"), "adk")

    def test_api_cases_still_requires_workspace_token(self):
        code, body = self.request("GET", "/api/cases")
        self.assertEqual(code, 401, body)

    def test_stripped_health_shape_is_rejected_by_control(self):
        """The exact 00026 payload must fail the partner field contract."""
        stripped = {
            "ok": True,
            "service": "agent-science",
            "mode": "private-workspaces",
            "revision": "agent-science-00026-zel",
        }
        for field in ("gemini", "parallel", "agent_builder", "engine_default"):
            self.assertNotIn(field, stripped)
        # Contract used by verify_partners_hosted.sh
        req = {
            "ok": True,
            "gemini": True,
            "parallel": True,
            "parallel_sdk": True,
            "agent_builder": True,
            "engine_default": "adk",
        }
        failed = [k for k, v in req.items() if stripped.get(k) != v]
        self.assertEqual(
            failed,
            ["gemini", "parallel", "parallel_sdk", "agent_builder", "engine_default"],
            "control must go red on the live 00026 shape",
        )


if __name__ == "__main__":
    unittest.main()
