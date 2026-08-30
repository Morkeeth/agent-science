"""ask_registry — the registry has a face (slice 2).

Query in → SOURCED span, UNSOURCED, or UNKNOWN with named refusal.
Every query becomes a browsable registry row. The refusal is the product.

    python3 ask_registry.py "Directive 2012/28/EU"
    python3 ask_registry.py --browse
    python3 ask_registry.py --serve          # local UI on :8091

No model, no network on the read path — it searches the compounding log
(clearance/refusal_log.py) that every clearance run writes.
"""
from __future__ import annotations

import argparse
import html
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from clearance import refusal_log

DB = Path(os.environ.get("REFUSAL_LOG_DB", refusal_log.DB))


def _db(path: Path | str | None = None) -> Path:
    return Path(path) if path else DB


def ask(query: str, db: Path | str = DB) -> dict:
    """Search the registry; log this query as a browsable row."""
    con = refusal_log.connect(db)
    return refusal_log.search_registry(con, query)


def browse(*, db: Path | str = DB, limit: int = 50) -> list[dict]:
    con = refusal_log.connect(db)
    return refusal_log.browse_queries(con, limit=limit)


def stats(*, db: Path | str = DB) -> dict:
    con = refusal_log.connect(db)
    return refusal_log.stats(con)


def _fmt(res: dict) -> str:
    lines = [f"\n  registry ← {res['query']!r}"]
    label = res["label"]
    lines.append(f"    [{label}]")

    if label == "SOURCED":
        span = (res.get("quoted_terms") or "")[:240]
        lines.append(f"        span: \"{span}\"")
        if res.get("citation_url"):
            lines.append(f"        source: {res['citation_url'][:90]}")
        if res.get("reused"):
            lines.append(f"        reused {res['reused']}x — cleared once, free since")
    elif label in ("UNSOURCED", "UNKNOWN", "REFUTED"):
        cause = res.get("cause") or "unspecified"
        lines.append(f"        refusal: {cause}")
        if res.get("why"):
            lines.append(f"        why: {res['why']}")
        if res.get("resolves_with"):
            lines.append(f"        would resolve with: {res['resolves_with']}")
        if res.get("quoted_terms"):
            lines.append(f"        read: \"{(res['quoted_terms'] or '')[:120]}\"")
    else:
        lines.append(f"        {res.get('why', 'not cleared yet')}")

    if res.get("matches", 0) > 1:
        lines.append(f"        ({res['matches']} claim rows matched)")
    return "\n".join(lines) + "\n"


_PAGE = """<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Agent Science — registry</title>
<style>
:root{--paper:#e9ecef;--ink:#14161c;--mute:#5c6370;--line:#c5cad3;--sourced:#1a5c2e;--unsourced:#b42318}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);
  font-family:Georgia,serif;font-size:18px;line-height:1.45}
.wrap{max-width:46rem;margin:0 auto;padding:2rem 1.25rem 3rem}
h1{font-size:2rem;margin:0 0 .25rem}p.lead{color:var(--mute);margin:0 0 .5rem}
p.nav,p.stats{font-family:monospace;font-size:.78rem;margin:0 0 1rem}
p.nav a{color:var(--ink)}
p.stats{color:var(--mute)}
form{display:flex;gap:.5rem;margin-bottom:2rem}
input[type=text]{flex:1;padding:.65rem .8rem;border:1px solid var(--line);font:inherit}
button{padding:.65rem 1rem;background:var(--ink);color:var(--paper);border:0;cursor:pointer}
.result{border-top:1px solid var(--ink);padding-top:1rem;margin-bottom:2rem}
.label{font-family:monospace;font-size:.85rem;letter-spacing:.04em}
.label.sourced{color:var(--sourced)}.label.unsourced,.label.unknown{color:var(--unsourced)}
blockquote{margin:.5rem 0;padding-left:.8rem;border-left:2px solid var(--line);color:var(--mute)}
table{width:100%;border-collapse:collapse;font-size:.9rem}
th,td{text-align:left;padding:.45rem .3rem;border-bottom:1px solid var(--line)}
th{font-family:monospace;font-size:.7rem;text-transform:uppercase;color:var(--mute)}
</style></head><body>
<div class="wrap">
  <h1>Registry</h1>
  <p class="lead">The websearch companion — verified truths and honest refusals, browsable.</p>
  <p class="nav"><a href="/">← clearance desk</a></p>
  <p class="stats">{stats_line}</p>
  <form method="get" action="/">
    <input type="text" name="q" value="{q}" placeholder="Ask anything cleared…" autofocus>
    <button type="submit">Query</button>
  </form>
  {result}
  <h2>Recent queries</h2>
  {browse}
</div>
</body></html>"""


def _html_result(res: dict | None) -> str:
    if not res:
        return ""
    label = html.escape(res.get("label") or "")
    cls = label.lower().replace("_", "-")
    parts = [f'<div class="result"><p class="label {cls}">[{label}]</p>']
    if res.get("label") == "SOURCED":
        parts.append(f'<blockquote>{html.escape((res.get("quoted_terms") or "")[:400])}</blockquote>')
        if res.get("citation_url"):
            u = html.escape(res["citation_url"])
            parts.append(f'<p><a href="{u}">{u[:80]}</a></p>')
    elif res.get("why") or res.get("cause"):
        parts.append(f'<p>{html.escape(res.get("why") or res.get("cause") or "")}</p>')
        if res.get("resolves_with"):
            parts.append(f'<p>Would resolve with: {html.escape(res["resolves_with"])}</p>')
    else:
        parts.append(f'<p>{html.escape(res.get("why", "not cleared"))}</p>')
    parts.append("</div>")
    return "".join(parts)


def _html_browse(rows: list[dict]) -> str:
    if not rows:
        return "<p class='lead'>No queries yet.</p>"
    tr = []
    for r in rows[:30]:
        tr.append(
            f"<tr><td>{html.escape((r.get('query_text') or '')[:50])}</td>"
            f"<td>{html.escape(r.get('result_label') or '')}</td>"
            f"<td>{html.escape((r.get('cause') or '')[:40])}</td>"
            f"<td>{html.escape((r.get('asked_at') or '')[:19])}</td></tr>"
        )
    return ("<table><tr><th>Query</th><th>Label</th><th>Cause</th><th>When</th></tr>"
            + "".join(tr) + "</table>")


class _Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, body: bytes, ctype: str):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        qs = parse_qs(parsed.query)
        if parsed.path == "/api":
            q = (qs.get("q") or [""])[0]
            return self._send(200, json.dumps(ask(q), indent=1).encode(), "application/json")
        q = (qs.get("q") or [""])[0].strip()
        page = render_page(q=q)
        self._send(200, page.encode(), "text/html; charset=utf-8")

    def log_message(self, fmt, *a):
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % a))


def render_page(*, q: str = "", db: Path | str | None = None,
                desk_href: str = "/") -> str:
    """HTML registry surface for hosted /registry and local --serve."""
    dbp = _db(db)
    st = stats(db=dbp)
    stats_line = (f"{st['n']} claims in registry · {st['cleared']} sourced · "
                  f"{st['refused']} refused · {st['reuses']} reuses")
    res = ask(q, db=dbp) if q.strip() else None
    page = (_PAGE
            .replace("{q}", html.escape(q, quote=True))
            .replace("{stats_line}", html.escape(stats_line))
            .replace("{result}", _html_result(res))
            .replace("{browse}", _html_browse(browse(db=dbp))))
    return page.replace('href="/"', f'href="{html.escape(desk_href, quote=True)}"', 1)


def serve(port: int = 8091) -> None:
    sys.stderr.write(f"registry on http://127.0.0.1:{port}/\n")
    HTTPServer(("127.0.0.1", port), _Handler).serve_forever()


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("query", nargs="*", help="question to search the registry")
    p.add_argument("--browse", action="store_true", help="list recent queries")
    p.add_argument("--json", action="store_true", help="machine-readable output")
    p.add_argument("--serve", action="store_true", help="local registry UI")
    p.add_argument("--port", type=int, default=8091)
    args = p.parse_args(argv)

    if args.serve:
        serve(args.port)
        return 0

    if args.browse:
        rows = browse()
        if args.json:
            print(json.dumps(rows, indent=1))
            return 0
        print(f"\n  registry — {len(rows)} recent quer{'y' if len(rows)==1 else 'ies'}\n")
        for r in rows:
            print(f"    [{r['result_label']:12}] {r['query_text'][:55]:55}  {r['asked_at'][:19]}")
        print()
        return 0

    if not args.query:
        p.print_help()
        return 2

    res = ask(" ".join(args.query))
    if args.json:
        print(json.dumps(res, indent=1))
    else:
        print(_fmt(res))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
