#!/usr/bin/env bash
# Prove private-workspaces /health + /partners expose partner fields locally.
# No network. Real google-adk + parallel-web required — no mocks.
#
# Watched RED 2026-09-19: the previous version patched adk_available/adk_version
# to True/"2.7.1", so PROVE_PARTNER_HEALTH_LOCAL OK could print while
# `import google.adk` failed. That is a false-green class defect.
#
# Done-when: engine_default=adk, parallel_sdk=true, gemini+parallel fields present.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
python3 - <<'PY'
import hashlib, http.client, json, os, tempfile, threading, time
from http.server import HTTPServer

from cloud import agent as adk_agent
from clearance import search as parallel_search

# RED first — packages at object, not patched.
assert adk_agent.adk_available(), (
    "google-adk not importable; pip install -r requirements.txt "
    f"(adk_version={adk_agent.adk_version()!r})"
)
assert adk_agent.adk_version() == "2.7.1", adk_agent.adk_version()
assert parallel_search.sdk_available(), (
    "parallel-web not importable; pip install -r requirements.txt "
    f"(sdk_version={parallel_search.sdk_version()!r})"
)
assert parallel_search.sdk_version() == "1.3.2", parallel_search.sdk_version()

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
old = {k: os.environ.get(k) for k in env}
os.environ.update(env)
try:
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
    c = http.client.HTTPConnection("127.0.0.1", port, timeout=10)
    c.request("POST", "/clear", b"{}", {"Content-Type": "application/json"})
    clear_code = c.getresponse().status
    c.close()
    server.shutdown()
    server.server_close()
finally:
    for k, v in old.items():
        if v is None:
            os.environ.pop(k, None)
        else:
            os.environ[k] = v

print(json.dumps({"health": health, "partners_checklist": partners.get("track_checklist"),
                  "clear_anonymous_status": clear_code}, indent=2))
assert hc == 200
assert health["engine_default"] == "adk", health
assert health["agent_builder"] is True
assert health["adk_version"] == "2.7.1"
assert health["gemini"] is True and health["parallel"] is True
assert health["parallel_sdk"] is True, health
assert health["parallel_transport"] == "parallel-web", health
assert health["mode"] == "private-workspaces"
assert pc == 200 and partners["track_checklist"]["adk_agent_builder"] is True
assert partners["track_checklist"]["parallel_search_at_runtime"] is True
assert partners["track_checklist"]["parallel_web_sdk"] is True
assert clear_code == 401
print("PROVE_PARTNER_HEALTH_LOCAL OK · real google-adk + parallel-web")
PY
