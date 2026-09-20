#!/usr/bin/env bash
# Prove private-workspaces /health + /partners expose partner fields locally.
# No keys, no network. Done-when: engine_default=adk and gemini/parallel present.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
python3 - <<'PY'
import hashlib, http.client, json, os, tempfile, threading, time
from http.server import HTTPServer
from unittest.mock import patch

TOKEN = "a" * 48
CONFIG = {
    "session_key": "s" * 48,
    "users": {"alice": hashlib.sha256(TOKEN.encode()).hexdigest()},
}
ORIGIN = "http://127.0.0.1"
tmpdir = tempfile.mkdtemp()
env = {
    "AGENT_SCIENCE_HOSTED": "1",
    "AGENT_SCIENCE_ALLOW_HTTP": "1",
    "AGENT_SCIENCE_PUBLIC_ORIGIN": ORIGIN,
    "AGENT_SCIENCE_ACCESS_CONFIG": json.dumps(CONFIG),
    "AGENT_SCIENCE_WORKSPACE_DIR": tmpdir,
    "AGENT_BUILDER": "1",
    "GCP_PROJECT": "hack-fleet",
    "PARALLEL_API_KEY": "pk-local-prove-not-live",
    "K_REVISION": "local-prove",
}
with patch.dict(os.environ, env, clear=False):
    with patch("cloud.agent.adk_available", return_value=True):
        with patch("cloud.agent.adk_version", return_value="2.7.1"):
            # Callable Gemini requires token — not GCP_PROJECT alone (2026-09-20).
            with patch("clearance.gemini.vertex_project", return_value="hack-fleet"):
                with patch("clearance.gemini.vertex_token", return_value="ya29.local-prove"):
                    from cloud.service import Handler
                    server = HTTPServer(("127.0.0.1", 0), Handler)
                    port = server.server_address[1]
                    threading.Thread(target=server.serve_forever, daemon=True).start()
                    time.sleep(0.15)

                    def get(path):
                        c = http.client.HTTPConnection("127.0.0.1", port, timeout=10)
                        c.request("GET", path)
                        r = c.getresponse()
                        code, body = r.status, json.loads(r.read().decode())
                        c.close()
                        return code, body

                    hc, health = get("/health")
                    pc, partners = get("/partners")
                    # /clear stays auth-gated
                    c = http.client.HTTPConnection("127.0.0.1", port, timeout=10)
                    c.request("POST", "/clear", b"{}", {"Content-Type": "application/json"})
                    clear_code = c.getresponse().status
                    c.close()
                    server.shutdown()
                    server.server_close()

print(json.dumps({"health": health, "partners_checklist": partners.get("track_checklist"),
                  "clear_anonymous_status": clear_code}, indent=2))
assert hc == 200
assert health["engine_default"] == "adk"
assert health["gemini"] is True and health["parallel"] is True
assert health.get("gemini_path", "").startswith("vertex:")
assert health.get("gemini_configured") is True
assert health["mode"] == "private-workspaces"
assert pc == 200 and partners["track_checklist"]["adk_agent_builder"] is True
assert clear_code == 401
print("PROVE_PARTNER_HEALTH_LOCAL OK")
PY
