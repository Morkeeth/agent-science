#!/usr/bin/env bash
# Prove private-workspaces serves public judge/film surfaces locally.
# No keys, no network. Done-when: /truths/ui + /visibility/ui 200 HTML;
# /registry and /clear stay shut for anonymous.
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
    "K_REVISION": "local-prove-film",
}
with patch.dict(os.environ, env, clear=False):
    with patch("cloud.agent.adk_available", return_value=True):
        with patch("cloud.agent.adk_version", return_value="2.7.1"):
            from cloud.service import Handler
            server = HTTPServer(("127.0.0.1", 0), Handler)
            port = server.server_address[1]
            threading.Thread(target=server.serve_forever, daemon=True).start()
            time.sleep(0.15)

            def get(path):
                c = http.client.HTTPConnection("127.0.0.1", port, timeout=30)
                c.request("GET", path)
                r = c.getresponse()
                code, ctype, body = r.status, r.getheader("content-type"), r.read().decode()
                c.close()
                return code, ctype or "", body

            truths = get("/truths/ui")
            vis_ui = get("/visibility/ui?q=ralph+loop+agentic")
            vis = get("/visibility?q=ralph+loop+agentic")
            pop = get("/popular/ui")
            reg = get("/registry")
            c = http.client.HTTPConnection("127.0.0.1", port, timeout=10)
            c.request("POST", "/clear", b"{}", {"Content-Type": "application/json"})
            clear_code = c.getresponse().status
            c.close()
            server.shutdown()
            server.server_close()

out = {
    "truths_ui": {"code": truths[0], "has_dashboard": "Truths dashboard" in truths[2]},
    "visibility_ui": {"code": vis_ui[0], "has_transparency": "Transparency" in vis_ui[2]},
    "visibility_json_keys": sorted(json.loads(vis[2]).keys())[:8] if vis[0] == 200 else [],
    "popular_ui_code": pop[0],
    "registry_anon": reg[0],
    "clear_anon": clear_code,
}
print(json.dumps(out, indent=2))
assert truths[0] == 200 and "Truths dashboard" in truths[2]
assert vis_ui[0] == 200 and "Transparency" in vis_ui[2]
assert vis[0] == 200 and "transparency" in json.loads(vis[2])
assert pop[0] == 200
assert reg[0] == 303
assert clear_code == 401
print("PROVE_JUDGE_SURFACES_LOCAL OK")
PY
