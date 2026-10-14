"""The MCP handshake reports the package version, read from one place."""
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))   # so `python3 tests/test_mcp_version.py` works too

import clearance  # noqa: E402


def test_initialize_reports_package_version():
    message = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
    p = subprocess.run([sys.executable, '-m', 'clearance.mcp_server'], input=json.dumps(message) + '\n',
                       capture_output=True, text=True, cwd=ROOT, timeout=30)
    assert p.returncode == 0, p.stderr
    info = json.loads(p.stdout.splitlines()[0])["result"]["serverInfo"]
    assert info["name"] == "agent-science"
    assert info["version"] == clearance.__version__, (info["version"], clearance.__version__)


if __name__ == "__main__":
    test_initialize_reports_package_version()
    print("PASS  mcp handshake version == clearance.__version__ ==", clearance.__version__)
