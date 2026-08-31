#!/usr/bin/env python3
"""Agent Science MCP — stack-wide verified websearch for Cursor/agents.

Run: python3 -m clearance.mcp_server
"""
from __future__ import annotations

import json
import sys

from clearance import ingest, stack_search

TOOLS = [
    {
        "name": "science_search",
        "description": (
            "Verified websearch for the fleet stack. Returns SOURCED (verbatim quote + "
            "URL), UNSOURCED/UNKNOWN (named refusal), or NOT_CLEARED. Checks the registry "
            "first (free); on miss runs Parallel + verify live. USE THIS instead of raw "
            "web search when you need a citable answer or an honest refusal."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "What to look up"},
                "live": {"type": "boolean", "description": "Live Parallel on registry miss", "default": True},
                "subject": {"type": "string", "description": "Production tag for compounding", "default": "stack"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "science_browse",
        "description": "Recent registry queries — what the stack already searched.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "default": 20},
            },
        },
    },
    {
        "name": "science_stats",
        "description": "Registry size, sourced/refused counts, recent queries.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "science_ingest",
        "description": (
            "Ingest a researched claim+URL into the registry (verify against source, "
            "append to research-inbox). Pass markdown with [CLAIM]/[URL] or claim+url. "
            "The audit trail is the inbox; the frozen measurement population is "
            "never written to."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "[CLAIM] markdown or claim\\nurl"},
                "claim": {"type": "string"},
                "url": {"type": "string"},
                "production": {"type": "string", "default": "ingest"},
            },
        },
    },
    {
        "name": "science_clear",
        "description": (
            "Clear a full documentary/production script — gap report with SOURCED/UNSOURCED rows."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "script": {"type": "string"},
                "subject": {"type": "string", "default": "production"},
            },
            "required": ["script"],
        },
    },
]


def _read_message():
    while True:
        line = sys.stdin.readline()
        if not line:
            return None
        line = line.strip()
        if not line:
            continue
        try:
            return json.loads(line)
        except json.JSONDecodeError:
            continue


def _send_message(msg):
    sys.stdout.write(json.dumps(msg) + "\n")
    sys.stdout.flush()


def handle_tool(name: str, arguments: dict) -> str:
    if name == "science_search":
        return json.dumps(stack_search.search(
            arguments["query"],
            subject=arguments.get("subject", "stack"),
            live=arguments.get("live", True),
        ), indent=2)

    if name == "science_browse":
        import ask_registry
        rows = ask_registry.browse(limit=int(arguments.get("limit", 20)))
        return json.dumps(rows, indent=2)

    if name == "science_stats":
        return json.dumps(stack_search.stats(), indent=2)

    if name == "science_ingest":
        prod = arguments.get("production", "ingest")
        if arguments.get("claim") and arguments.get("url"):
            res = ingest.ingest_claim(arguments["claim"], arguments["url"], production=prod)
        elif arguments.get("text"):
            res = ingest.ingest_text(arguments["text"], production=prod)
        else:
            return json.dumps({"error": "pass text or claim+url"})
        return json.dumps(res, indent=2)

    if name == "science_clear":
        import agent_science
        out = agent_science.clear_script(
            arguments["script"],
            subject=arguments.get("subject", "production"),
        )
        return json.dumps(out, indent=2)

    return json.dumps({"error": f"unknown tool: {name}"})


def main():
    while True:
        msg = _read_message()
        if msg is None:
            break
        method = msg.get("method", "")
        msg_id = msg.get("id")

        if method == "initialize":
            _send_message({
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {"listChanged": False}},
                    "serverInfo": {"name": "agent-science", "version": "0.2.0"},
                },
            })
        elif method == "notifications/initialized":
            pass
        elif method == "tools/list":
            _send_message({"jsonrpc": "2.0", "id": msg_id, "result": {"tools": TOOLS}})
        elif method == "tools/call":
            params = msg.get("params", {})
            text = handle_tool(params.get("name", ""), params.get("arguments", {}))
            _send_message({
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {"content": [{"type": "text", "text": text}], "isError": False},
            })
        elif msg_id is not None:
            _send_message({
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"},
            })


if __name__ == "__main__":
    main()
