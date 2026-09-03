#!/usr/bin/env python3
"""Agent Science MCP — stack-wide verified websearch for Cursor/agents.

Run: python3 -m clearance.mcp_server
"""
from __future__ import annotations

import json
import sys

from clearance import ingest, query_analytics, stack_search

TOOLS = [
    {
        "name": "science_lookup",
        "description": (
            "DEFAULT for daily factual lookups. Truth dictionary: exact replay → registry "
            "→ URL routing (CELEX, arXiv, rights vocab) → only then optional live search. "
            "Returns cost_tier (free/cheap/live). Set live=true only when you need fresh "
            "web discovery. USE THIS instead of raw web search."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "What to look up"},
                "live": {"type": "boolean", "description": "Paid Parallel+Gemini on miss", "default": False},
                "subject": {"type": "string", "description": "Production tag for compounding", "default": "stack"},
                "traffic": {
                    "type": "string",
                    "description": "human|gate|fleet|demo — analytics class (default human for MCP)",
                    "default": "human",
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "science_search",
        "description": (
            "Live verified websearch — same as science_lookup with live=true. Use when "
            "dictionary miss needs fresh Parallel discovery. Prefer science_lookup first."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "What to look up"},
                "live": {"type": "boolean", "description": "Live Parallel on registry miss", "default": True},
                "subject": {"type": "string", "description": "Production tag for compounding", "default": "stack"},
                "traffic": {"type": "string", "default": "human"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "science_popular",
        "description": (
            "Top queries devs ask, optimization targets (repeated live/miss), alias "
            "candidates, and Parallel probes. Use to grow the truth dictionary efficiently."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "default": 15},
            },
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
        "name": "science_visibility",
        "description": (
            "FULL Agent Science websearch — truth layer for believe+use. "
            "Not one answer: primary verify/refuse + aliases + GitHub ★ + blogs/docs + "
            "agentic practices corpus + peer queries + Parallel probes + shelf stats. "
            "Indexes into personal truth DB (~/.agent-science/truth.db) by default. "
            "Default full=true. Prefer over raw web search and over science_lookup alone."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "What to scout"},
                "live": {"type": "boolean", "default": False},
                "full": {
                    "type": "boolean",
                    "default": True,
                    "description": "Full agentic-truth rundown (all panes). Default true.",
                },
                "no_personal": {
                    "type": "boolean",
                    "default": False,
                    "description": "Skip writing personal truth DB",
                },
                "subject": {"type": "string", "default": "stack"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "science_truth",
        "description": (
            "Personal truth DB — your indexed websearch asks, Magnet skill verdicts "
            "(helped/hurt/baseline), and field fetches. Actions: stats, recent, "
            "fetch-field, skill."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["stats", "recent", "fetch-field", "skill"],
                    "default": "stats",
                },
                "limit": {"type": "integer", "default": 20},
                "skill": {"type": "string"},
                "verdict": {"type": "string", "enum": ["helped", "hurt", "baseline"]},
                "probe": {"type": "string"},
                "note": {"type": "string"},
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
    {
        "name": "science_use_bar",
        "description": (
            "USE-BAR interceptor: run truth layer BEFORE any raw websearch and write a "
            "session receipt (~/.agent-science/session-receipts.jsonl). Prefer this (or "
            "science_visibility) over browser search. Returns lookup/visibility result + "
            "receipt_id. Do not claim Oscar uses Agent Science every search without a "
            "filled session receipt."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "mode": {
                    "type": "string",
                    "enum": ["lookup", "visibility"],
                    "default": "lookup",
                },
                "live": {"type": "boolean", "default": False},
                "traffic": {"type": "string", "default": "human"},
                "subject": {"type": "string", "default": "stack"},
                "session_id": {"type": "string"},
            },
            "required": ["query"],
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
    if name in ("science_lookup", "science_search"):
        live = arguments.get("live", name == "science_search")
        return json.dumps(stack_search.lookup(
            arguments["query"],
            subject=arguments.get("subject", "stack"),
            live=live,
            traffic=arguments.get("traffic", "human"),
        ), indent=2)

    if name == "science_use_bar":
        from clearance import use_path
        return json.dumps(use_path.intercept(
            arguments["query"],
            mode=arguments.get("mode", "lookup"),
            live=bool(arguments.get("live", False)),
            traffic=arguments.get("traffic", "human"),
            subject=arguments.get("subject", "stack"),
            session_id=arguments.get("session_id"),
        ), indent=2)

    if name == "science_popular":
        return json.dumps(query_analytics.report(
            limit=int(arguments.get("limit", 15)),
        ), indent=2)

    if name == "science_browse":
        import ask_registry
        rows = ask_registry.browse(limit=int(arguments.get("limit", 20)))
        return json.dumps(rows, indent=2)

    if name == "science_stats":
        return json.dumps(stack_search.stats(), indent=2)

    if name == "science_visibility":
        from clearance import visibility
        full = arguments.get("full", True)
        if full is None:
            full = True
        data = visibility.panel(
            arguments["query"],
            live=bool(arguments.get("live", False)),
            subject=arguments.get("subject", "stack"),
            full=bool(full),
            personal=not bool(arguments.get("no_personal", False)),
        )
        return visibility.format_panel(data)

    if name == "science_truth":
        from clearance import personal_truth
        action = arguments.get("action", "stats")
        if action == "stats":
            return json.dumps(personal_truth.stats(), indent=2)
        if action == "recent":
            return json.dumps(
                personal_truth.recent_asks(limit=int(arguments.get("limit", 20))),
                indent=2, default=str,
            )
        if action == "fetch-field":
            return json.dumps(personal_truth.ingest_field_signals(), indent=2)
        if action == "skill":
            tid = personal_truth.record_skill_truth(
                arguments["skill"],
                arguments["verdict"],
                probe=arguments.get("probe"),
                note=arguments.get("note"),
            )
            return json.dumps({"id": tid, **personal_truth.stats()}, indent=2)
        return json.dumps({"error": f"unknown action {action}"})

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
