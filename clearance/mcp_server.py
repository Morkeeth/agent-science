#!/usr/bin/env python3
"""Agent Science MCP — stack-wide verified websearch for Cursor/agents.

Run: python3 -m clearance.mcp_server
"""
from __future__ import annotations

import json
import sys
import sqlite3

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
]


TOOLS.append({
    "name": "science_case",
    "description": "Find saved research by topic with find; research a question, import an existing report, investigate gaps with Parallel/Perplexity, assess claims against exact source passages, inspect a brief, save decisions and review changed evidence. Stored locally. Quote occurrence is verified; support is not inferred. Repo context never enters web queries. Experiments execute only through the explicit local CLI.",
    "inputSchema": {"type": "object", "properties": {
        "action": {"type": "string", "enum": ["create", "show", "refresh", "decide", "list", "source", "review", "import", "investigate", "assess", "brief", "report", "find"]},
        "db": {"type": "string", "description": "Optional local case database, matching CLI --db"},
        "version": {"type": "integer", "description": "Required for decide, investigate and assess: inspected case version; optional historical version for show/source/brief/report"}, "evidence_id": {"type": "string"},
        "offset": {"type": "integer", "default": 0}, "limit": {"type": "integer", "description": "Source/report chunk characters (default 12000); investigate results per provider (1–10, default 5); find page size (1–100, default 5); list/review page size alias"},
        "query": {"type": "string", "description": "Local relevance query for find; local filter for list/review; explicit public search query for investigate"},
        "page_info": {"type": "boolean", "default": False, "description": "Include has_more/next_offset in list result; default retains legacy array"},
        "experiment_ids": {"type": "array", "items": {"type": "string"}, "description": "Valid local experiment IDs cited by this decision; may replace source evidence IDs"},
        "page_size": {"type": "integer", "minimum": 1, "maximum": 100, "description": "Page size alias: default 5 for find, 20 for list/review. For find, do not pass a conflicting limit."},
        "supersedes": {"type": "string", "description": "Active decision or assessment ID to replace; requires inspected version"},
        "report_text": {"type":"string","description":"Report contents, Markdown/plain text or Sonar JSON. Stored locally; never sent to discovery."},
        "providers": {"type":"array","items":{"type":"string","enum":["parallel","perplexity"]}},
        "max_documents": {"type":"integer","minimum":1,"maximum":40,"default":12},
        "claim_id": {"type":"string"},
        "quote": {"type":"string","description":"Exact source snapshot passage for an authored assessment"},
        "relation": {"type":"string","enum":["supports","contradicts","context","unresolved"]},
        "question": {"type": "string"}, "case_id": {"type": "string"},
        "root": {"type": "string", "description": "Local user repo for context"},
        "live": {"type": "boolean", "default": False},
        "sources": {"type": "array", "items": {"type": "string"}},
        "official_domains": {"type": "array", "items": {"type": "string"}},
        "statement": {"type": "string"}, "rationale": {"type": "string"},
        "evidence_ids": {"type": "array", "items": {"type": "string"}}
    }, "required": ["action"]}
})

for tool in TOOLS:
    if tool["name"] in ("science_lookup", "science_search", "science_visibility"):
        tool["inputSchema"]["properties"]["refresh"] = {"type": "boolean", "default": False, "description": "Bypass cached verdicts; live=true fetches current sources"}
    if tool["name"] == "science_visibility":
        tool["inputSchema"]["properties"]["root"] = {"type": "string", "description": "Your local repo, never the hosted server repo"}


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
    if name == "science_case":
        from clearance import cases, case_review, research, research_search
        action = arguments.get("action")
        db=arguments.get("db")
        try:
            for key in ("live","page_info"):
                if key in arguments and type(arguments[key]) is not bool:
                    raise ValueError(f"{key} must be a boolean")
            for key in ("sources","official_domains","evidence_ids","experiment_ids","providers"):
                if key in arguments and (not isinstance(arguments[key],list) or any(not isinstance(v,str) for v in arguments[key])):
                    raise ValueError(f"{key} must be an array of strings")
            for key in ("question","case_id","statement","rationale","query","supersedes","root","db","evidence_id","report_text","claim_id","quote","relation"):
                if key in arguments and not isinstance(arguments[key],str):
                    raise ValueError(f"{key} must be text")
            if "version" in arguments and (type(arguments["version"]) is not int or arguments["version"]<1):
                raise ValueError("version must be a positive integer")
            if action == "find":
                for key in ("limit", "page_size"):
                    if key in arguments and (type(arguments[key]) is not int or not 1 <= arguments[key] <= 100):
                        raise ValueError(f"find {key} must be an integer from 1 to 100")
                if "limit" in arguments and "page_size" in arguments and arguments["limit"] != arguments["page_size"]:
                    raise ValueError("find limit and page_size must agree when both are supplied")
                return json.dumps(research_search.find(arguments.get("query",""),db=db,root=arguments.get("root"),limit=arguments.get("page_size",arguments.get("limit",5)),offset=arguments.get("offset",0)),indent=2)
            elif action == "import":
                data=research.import_report(arguments.get("question",""),arguments.get("report_text",""),root=arguments.get("root"),live=arguments.get("live",False),max_documents=arguments.get("max_documents",12),db=db)
            elif action == "investigate":
                data=research.investigate(arguments.get("case_id",""),arguments.get("version"),query=arguments.get("query",""),sources=arguments.get("sources",[]),providers=arguments.get("providers",["parallel"]),live=arguments.get("live",False),limit=arguments.get("limit",5),db=db)
            elif action == "assess":
                data=research.assess(arguments.get("case_id",""),arguments.get("version"),statement=arguments.get("statement"),relation=arguments.get("relation"),rationale=arguments.get("rationale"),evidence_id=arguments.get("evidence_id"),quote=arguments.get("quote"),claim_id=arguments.get("claim_id"),supersedes=arguments.get("supersedes"),db=db)
            elif action == "brief":
                return json.dumps(research.brief(cases.get(arguments.get("case_id",""),version=arguments.get("version"),db=db)),indent=2)
            elif action == "report":
                return json.dumps(research.report_source(arguments.get("case_id",""),version=arguments.get("version"),db=db,offset=arguments.get("offset",0),limit=arguments.get("limit",12000)),indent=2)
            elif action == "create":
                data = cases.create(arguments.get("question", ""), root=arguments.get("root"),
                    live=arguments.get("live", False), sources=arguments.get("sources", []),
                    official_domains=arguments.get("official_domains", []),db=db)
            elif action == "show": data = cases.get(arguments.get("case_id", ""), version=arguments.get("version"),db=db)
            elif action == "source": return json.dumps(cases.source(arguments.get("case_id", ""), arguments.get("evidence_id", ""), version=arguments.get("version"), offset=arguments.get("offset",0), limit=arguments.get("limit",12000),db=db), indent=2)
            elif action == "refresh": data = cases.refresh(arguments.get("case_id", ""), live=arguments.get("live", False),db=db)
            elif action == "decide":
                if type(arguments.get("version")) is not int:
                    raise ValueError("decide requires the evidence version you inspected")
                data = cases.decide(arguments.get("case_id", ""), arguments.get("statement", ""), arguments.get("rationale", ""), arguments.get("evidence_ids", []),db=db,supersedes=arguments.get("supersedes"),expected_version=arguments["version"],experiment_ids=arguments.get("experiment_ids",[]))
            elif action in ("list", "review"):
                result=case_review.index(db=db,root=arguments.get("root"),query=arguments.get("query",""),review_only=action=="review",limit=arguments.get("page_size",arguments.get("limit",20)),offset=arguments.get("offset",0),include_cases=action=="list")
                if action=="list":
                    full_cases=result.pop("case_data")
                    result={**result,"cases":full_cases}
                return json.dumps(result if action=="review" or arguments.get("page_info") else result["cases"],indent=2)
            else: raise ValueError("unknown case action")
            return json.dumps(cases.public_view(data), indent=2)
        except (ValueError, OSError, sqlite3.Error) as exc:
            return json.dumps({"error": str(exc)})
    if name in ("science_lookup", "science_search"):
        live = arguments.get("live", name == "science_search")
        return json.dumps(stack_search.lookup(
            arguments["query"],
            subject=arguments.get("subject", "stack"),
            live=live,
            refresh=bool(arguments.get("refresh", False)),
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
            root=arguments.get("root"),
            refresh=bool(arguments.get("refresh", False)),
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
                    "serverInfo": {"name": "agent-science", "version": "0.4.0"},
                },
            })
        elif method == "notifications/initialized":
            pass
        elif method == "tools/list":
            _send_message({"jsonrpc": "2.0", "id": msg_id, "result": {"tools": TOOLS}})
        elif method == "tools/call":
            params = msg.get("params", {})
            try:
                if not isinstance(params,dict) or not isinstance(params.get("arguments",{}),dict):
                    raise ValueError("tool arguments must be an object")
                text = handle_tool(params.get("name", ""), params.get("arguments", {}))
                try:
                    payload=json.loads(text)
                except json.JSONDecodeError:
                    payload=None  # Some tools intentionally return Markdown.
                failed=isinstance(payload,dict) and "error" in payload
            except (ValueError,TypeError,KeyError,OSError,sqlite3.Error) as exc:
                text=json.dumps({"error":str(exc)})
                failed=True
            _send_message({
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {"content": [{"type": "text", "text": text}], "isError": failed},
            })
        elif msg_id is not None:
            _send_message({
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"},
            })


if __name__ == "__main__":
    main()
