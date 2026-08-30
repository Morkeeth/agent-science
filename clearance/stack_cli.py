#!/usr/bin/env python3
"""CLI for stack-wide Agent Science websearch.

  python3 -m clearance.stack_cli search "Directive 2012/28/EU"
  python3 -m clearance.stack_cli browse
  python3 -m clearance.stack_cli stats
  python3 -m clearance.stack_cli ingest --claim "..." --url "https://..."
  python3 -m clearance.stack_cli serve          # desk + registry on :8080
  python3 -m clearance.stack_cli mcp              # stdio MCP (for Cursor)
"""
from __future__ import annotations

import argparse
import json
import sys

from clearance import ingest, stack_search


def _print_result(res: dict) -> None:
    label = res.get("label", "?")
    print(f"[{label}] {res.get('query', '')}")
    if label == "SOURCED":
        print(f"  source: {res.get('citation_url', '')}")
        print(f'  span: "{(res.get("quoted_terms") or "")[:240]}"')
        if res.get("reused"):
            print(f"  reused {res['reused']}x from registry")
    elif res.get("why") or res.get("cause"):
        print(f"  {res.get('why') or res.get('cause')}")
    src = res.get("source")
    api = res.get("parallel_api_calls", 0)
    if src:
        print(f"  via {src}" + (f" · {api} Parallel API" if api else " · 0 Parallel API"))


def cmd_search(args: argparse.Namespace) -> int:
    res = stack_search.search(args.query, live=not args.offline, subject=args.subject)
    if args.json:
        print(json.dumps(res, indent=2))
    else:
        _print_result(res)
    return 0 if res.get("label") != "NOT_CLEARED" or args.offline else 1


def cmd_browse(args: argparse.Namespace) -> int:
    import ask_registry
    rows = ask_registry.browse(limit=args.limit)
    if args.json:
        print(json.dumps(rows, indent=2))
        return 0
    for r in rows:
        print(f"  [{r['result_label']:12}] {r['query_text'][:55]:55}  {r['asked_at'][:19]}")
    return 0


def cmd_stats(_args: argparse.Namespace) -> int:
    print(json.dumps(stack_search.stats(), indent=2))
    return 0


def cmd_ingest(args: argparse.Namespace) -> int:
    if args.claim and args.url:
        res = ingest.ingest_claim(args.claim, args.url, production=args.production)
    elif args.text:
        res = ingest.ingest_text(args.text, production=args.production)
    else:
        res = ingest.ingest_text(sys.stdin.read(), production=args.production)
    print(json.dumps(res, indent=2))
    return 0


def cmd_serve(args: argparse.Namespace) -> int:
    import os
    os.environ.setdefault("PORT", str(args.port))
    from cloud import service
    service.main()
    return 0


def cmd_mcp(_args: argparse.Namespace) -> int:
    from clearance import mcp_server
    mcp_server.main()
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Agent Science — stack websearch")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("search", help="verified websearch (registry → live)")
    s.add_argument("query", nargs="+", help="search query")
    s.add_argument("--subject", default="stack")
    s.add_argument("--offline", action="store_true", help="registry only, no Parallel")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_search)

    b = sub.add_parser("browse", help="recent registry queries")
    b.add_argument("--limit", type=int, default=20)
    b.add_argument("--json", action="store_true")
    b.set_defaults(func=cmd_browse)

    sub.add_parser("stats", help="registry stats").set_defaults(func=cmd_stats)

    ig = sub.add_parser("ingest", help="ingest claim into registry")
    ig.add_argument("--claim")
    ig.add_argument("--url")
    ig.add_argument("--text")
    ig.add_argument("--production", default="ingest")
    ig.set_defaults(func=cmd_ingest)

    sv = sub.add_parser("serve", help="HTTP desk + registry")
    sv.add_argument("--port", type=int, default=8080)
    sv.set_defaults(func=cmd_serve)

    sub.add_parser("mcp", help="stdio MCP for Cursor").set_defaults(func=cmd_mcp)

    args = p.parse_args(argv)
    if args.cmd == "search":
        args.query = " ".join(args.query)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
