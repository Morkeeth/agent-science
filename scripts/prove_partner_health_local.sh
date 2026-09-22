#!/usr/bin/env bash
# Prove private-workspaces /health + /partners expose partner fields locally.
# No network. Done-when: engine_default=adk and gemini/parallel present.
#
# ADK honesty (2026-09-22): earlier versions always patched adk_available=True,
# so PROVE_PARTNER_HEALTH_LOCAL OK never proved google-adk was importable.
# Default now uses the real import. Cold-clone without pip may set
# PROVE_ALLOW_ADK_PATCH=1 — that path prints FINDING and stamps prove_mode.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PROVE_ALLOW_ADK_PATCH="${PROVE_ALLOW_ADK_PATCH:-0}"
python3 - <<'PY'
import hashlib, http.client, json, os, tempfile, threading, time
from contextlib import ExitStack
from http.server import HTTPServer
from unittest.mock import patch

from cloud import agent as adk_agent

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

real_adk = adk_agent.adk_available()
real_ver = adk_agent.adk_version()
allow_patch = os.environ.get("PROVE_ALLOW_ADK_PATCH", "0").strip().lower() in (
    "1", "true", "yes", "on",
)
prove_mode = "unpatched"

if real_adk:
    print(f"ADK import REAL · version={real_ver}")
elif allow_patch:
    prove_mode = "adk-patched"
    print(
        "FINDING: ADK not importable — proving HTTP shape with patch "
        "(PROVE_ALLOW_ADK_PATCH=1). Not a real engine_default prove."
    )
else:
    print("BLOCKED: google-adk not importable.")
    print("  pip install 'google-adk==2.7.1'   # then re-run")
    print("  OR: PROVE_ALLOW_ADK_PATCH=1 bash scripts/prove_partner_health_local.sh")
    raise SystemExit(3)

with patch.dict(os.environ, env, clear=False), ExitStack() as stack:
    if prove_mode == "adk-patched":
        stack.enter_context(patch("cloud.agent.adk_available", return_value=True))
        stack.enter_context(patch("cloud.agent.adk_version", return_value="2.7.1"))
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

out = {
    "prove_mode": prove_mode,
    "adk_import_real": real_adk,
    "adk_version_real": real_ver,
    "health": health,
    "partners_checklist": partners.get("track_checklist"),
    "clear_anonymous_status": clear_code,
}
print(json.dumps(out, indent=2))
assert hc == 200
assert health["engine_default"] == "adk"
assert health["gemini"] is True and health["parallel"] is True
assert health["mode"] == "private-workspaces"
assert pc == 200 and partners["track_checklist"]["adk_agent_builder"] is True
assert clear_code == 401
if prove_mode == "unpatched":
    print("PROVE_PARTNER_HEALTH_LOCAL OK · unpatched ADK")
else:
    print("PROVE_PARTNER_HEALTH_LOCAL OK · HTTP shape only (ADK patched)")
PY
