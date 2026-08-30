#!/usr/bin/env bash
# Install Agent Science MCP into ~/.cursor/mcp.json
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MCP="$HOME/.cursor/mcp.json"
PY="${PYTHON:-python3}"

mkdir -p "$(dirname "$MCP")"
if [[ ! -f "$MCP" ]]; then
  echo '{"mcpServers":{}}' > "$MCP"
fi

"$PY" - "$ROOT" "$MCP" <<'PY'
import json, sys
root, mcp_path = sys.argv[1], sys.argv[2]
with open(mcp_path) as f:
    cfg = json.load(f)
servers = cfg.setdefault("mcpServers", {})
servers["agent-science"] = {
    "command": sys.executable,
    "args": ["-m", "clearance.mcp_server"],
    "cwd": root,
}
with open(mcp_path, "w") as f:
    json.dump(cfg, f, indent=2)
    f.write("\n")
print(f"installed agent-science MCP → {mcp_path}")
print("Restart Cursor. Use science_search instead of raw web search.")
PY
