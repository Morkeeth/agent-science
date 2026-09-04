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

from clearance import ingest, query_analytics, stack_search


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
    tier = res.get("cost_tier", "?")
    if src or tier:
        bits = [f"tier={tier}"]
        if src:
            bits.append(f"via {src}")
        if api:
            bits.append(f"{api} Parallel API")
        else:
            bits.append("0 Parallel API")
        print(f"  {' · '.join(bits)}")
    if res.get("next_step"):
        print(f"  → {res['next_step']}")


def cmd_lookup(args: argparse.Namespace) -> int:
    res = stack_search.lookup(args.query, live=args.live, subject=args.subject, refresh=args.refresh)
    if args.json:
        print(json.dumps(res, indent=2))
    else:
        _print_result(res)
    return 0 if res.get("label") not in ("NOT_CLEARED",) or args.live else 1


def cmd_search(args: argparse.Namespace) -> int:
    res = stack_search.lookup(args.query, live=not args.offline, subject=args.subject, refresh=args.refresh)
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


def cmd_popular(args: argparse.Namespace) -> int:
    data = query_analytics.report(limit=args.limit)
    if args.json:
        print(json.dumps(data, indent=2))
        return 0
    print("=== Popular queries (by asks) ===")
    for r in data["popular_queries"][: args.limit]:
        print(f"  {r['asks']:3d}x  [{r.get('sourced', 0)} sourced / "
              f"{r.get('not_cleared', 0)} miss / {r.get('live_asks', 0)} live]  "
              f"{r['example'][:70]}")
    print("\n=== Optimize next (live spend or misses) ===")
    for r in data["optimization_targets"][: args.limit]:
        print(f"  {r['asks']:3d}x  live={r.get('live_asks', 0)} miss={r.get('not_cleared', 0)}  "
              f"→ {r['action']}")
        print(f"         {r['example'][:75]}")
    if data["alias_candidates"]:
        print("\n=== Alias candidates (add to truth-dictionary/aliases.json) ===")
        for r in data["alias_candidates"][:8]:
            print(f'  "{r["alias"]}" → "{r["canonical"]}"')
    if data["parallel_probes"]:
        print("\n=== Parallel probes (from receipts) ===")
        for r in data["parallel_probes"][:8]:
            print(f"  {r['asks']:3d}x  {r['probe'][:70]}")
    return 0


def cmd_stats(_args: argparse.Namespace) -> int:
    print(json.dumps(stack_search.stats(), indent=2))
    return 0


def cmd_visibility(args: argparse.Namespace) -> int:
    from clearance import visibility
    data = visibility.panel(
        args.query,
        live=args.live,
        subject=args.subject,
        full=args.full,
        personal=not args.no_personal,
        root=args.root,
        refresh=args.refresh,
    )
    if args.json:
        print(json.dumps(data, indent=2, default=str))
    else:
        print(visibility.format_panel(data), end="")
    return 0


def cmd_truth(args: argparse.Namespace) -> int:
    from clearance import personal_truth
    if args.action == "stats":
        print(json.dumps(personal_truth.stats(), indent=2))
        return 0
    if args.action == "recent":
        print(json.dumps(personal_truth.recent_asks(limit=args.limit), indent=2, default=str))
        return 0
    if args.action == "truths":
        print(json.dumps(
            personal_truth.recent_truths(kind=args.kind, limit=args.limit),
            indent=2, default=str,
        ))
        return 0
    if args.action == "fetch-field":
        print(json.dumps(personal_truth.ingest_field_signals(), indent=2))
        return 0
    if args.action == "skill":
        if getattr(args, "fit", None):
            from clearance import stack_fit
            data = stack_fit.score(args.fit)
            if args.json:
                print(json.dumps(data, indent=2))
            else:
                print(stack_fit.format_result(data), end="")
            return 0
        tid = personal_truth.record_skill_truth(
            args.skill, args.verdict, probe=args.probe, note=args.note,
        )
        print(json.dumps({"id": tid, **personal_truth.stats()}, indent=2))
        return 0
    print("unknown truth action", file=sys.stderr)
    return 1


def cmd_stack_fit(args: argparse.Namespace) -> int:
    from clearance import stack_fit
    data = stack_fit.score(args.query, root=args.root)
    if args.json:
        print(json.dumps(data, indent=2))
    else:
        print(stack_fit.format_result(data), end="")
    return 0


def cmd_notes(args: argparse.Namespace) -> int:
    from clearance import community_notes as CN
    if args.action == "list":
        rows = CN.list_notes(status=args.status, path=args.path)
        if args.json:
            print(json.dumps(rows, indent=2))
        else:
            for r in rows:
                print(f"[{r.get('status')}] {r.get('id')}  {r.get('claim', '')[:70]}")
                if r.get("dispute"):
                    print(f"  dispute: {r['dispute'].get('text', '')[:80]}")
        return 0
    if args.action == "upload":
        row = CN.upload(args.claim, submitter=args.submitter, url=args.url, path=args.path)
        print(json.dumps(row, indent=2))
        return 0
    if args.action == "dispute":
        row = CN.dispute(args.note_id, args.text, submitter=args.submitter, path=args.path)
        if not row:
            print(json.dumps({"error": "note not found"}), file=sys.stderr)
            return 1
        print(json.dumps(row, indent=2))
        return 0
    print("unknown notes action", file=sys.stderr)
    return 1


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

    s = sub.add_parser("lookup", help="truth dictionary (free/cheap; live optional)")
    s.add_argument("query", nargs="+", help="lookup query")
    s.add_argument("--subject", default="stack")
    s.add_argument("--live", action="store_true", help="paid Parallel on miss")
    s.add_argument("--refresh", action="store_true", help="bypass old verdicts and source caches")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_lookup)

    s = sub.add_parser("search", help="verified websearch (live unless --offline)")
    s.add_argument("query", nargs="+", help="search query")
    s.add_argument("--subject", default="stack")
    s.add_argument("--offline", action="store_true", help="registry only, no Parallel")
    s.add_argument("--refresh", action="store_true", help="bypass old verdicts and source caches")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_search)

    b = sub.add_parser("browse", help="recent registry queries")
    b.add_argument("--limit", type=int, default=20)
    b.add_argument("--json", action="store_true")
    b.set_defaults(func=cmd_browse)

    sub.add_parser("stats", help="registry stats").set_defaults(func=cmd_stats)

    pop = sub.add_parser("popular", help="top queries + optimization targets for devs")
    pop.add_argument("--limit", type=int, default=15)
    pop.add_argument("--json", action="store_true")
    pop.set_defaults(func=cmd_popular)

    vis = sub.add_parser(
        "visibility",
        help="truth-layer websearch panel — more than one answer",
    )
    vis.add_argument("query", nargs="+", help="query")
    vis.add_argument("--subject", default="stack")
    vis.add_argument("--live", action="store_true")
    vis.add_argument("--refresh", action="store_true")
    vis.add_argument("--root", default=".", help="your repo context (kept local)")
    vis.add_argument("--full", action="store_true",
                     help="full agentic-truth rundown (all panes)")
    vis.add_argument("--no-personal", action="store_true",
                     help="do not write ~/.agent-science/truth.db")
    vis.add_argument("--json", action="store_true")
    vis.set_defaults(func=cmd_visibility)

    tr = sub.add_parser("truth", help="personal truth DB (~/.agent-science/truth.db)")
    tr_sub = tr.add_subparsers(dest="action", required=True)
    tr_sub.add_parser("stats", help="personal shelf counts").set_defaults(func=cmd_truth)
    tr_r = tr_sub.add_parser("recent", help="recent personal asks")
    tr_r.add_argument("--limit", type=int, default=20)
    tr_r.set_defaults(func=cmd_truth)
    tr_t = tr_sub.add_parser("truths", help="recent personal truths")
    tr_t.add_argument("--kind", choices=["claim", "skill", "field_fetch"])
    tr_t.add_argument("--limit", type=int, default=20)
    tr_t.set_defaults(func=cmd_truth)
    tr_sub.add_parser(
        "fetch-field", help="pull field-signals URLs into personal fetches"
    ).set_defaults(func=cmd_truth)
    tr_s = tr_sub.add_parser("skill", help="record Magnet skill verdict as truth")
    tr_s.add_argument("skill", nargs="?")
    tr_s.add_argument("verdict", nargs="?", choices=["helped", "hurt", "baseline"])
    tr_s.add_argument("--fit", help="stack-fit score for query instead of recording skill")
    tr_s.add_argument("--probe")
    tr_s.add_argument("--note")
    tr_s.add_argument("--json", action="store_true")
    tr_s.set_defaults(func=cmd_truth)

    sf = sub.add_parser("stack-fit", help="magnet eval — how well a truth fits your stack")
    sf.add_argument("query", nargs="+", help="query or truth to score")
    sf.add_argument("--root", default=".", help="repo root to detect stack from")
    sf.add_argument("--json", action="store_true")
    sf.set_defaults(func=cmd_stack_fit)

    nt = sub.add_parser("notes", help="community notes — upload / dispute claims")
    nt_sub = nt.add_subparsers(dest="action", required=True)
    nt_l = nt_sub.add_parser("list", help="list community notes")
    nt_l.add_argument("--status", choices=["pending", "disputed"])
    nt_l.add_argument("--path", help="override notes JSONL path")
    nt_l.add_argument("--json", action="store_true")
    nt_l.set_defaults(func=cmd_notes)
    nt_u = nt_sub.add_parser("upload", help="upload a claim for community review")
    nt_u.add_argument("claim")
    nt_u.add_argument("--submitter", default="anonymous")
    nt_u.add_argument("--url")
    nt_u.add_argument("--path")
    nt_u.set_defaults(func=cmd_notes)
    nt_d = nt_sub.add_parser("dispute", help="dispute an existing note")
    nt_d.add_argument("note_id")
    nt_d.add_argument("text")
    nt_d.add_argument("--submitter", default="anonymous")
    nt_d.add_argument("--path")
    nt_d.set_defaults(func=cmd_notes)

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

    from clearance.case_cli import add_parser
    add_parser(sub)

    args = p.parse_args(argv)
    if args.cmd in ("search", "lookup", "visibility", "stack-fit"):
        args.query = " ".join(args.query)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
