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
from urllib.parse import parse_qs, urlencode, urlparse

from clearance import curve, refusal_log

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


_CSS = """
:root{
  --paper:#e8e6e1; --card:#f3f1ed; --ink:#16181d; --mute:#61656e; --rule:#c9c5bd;
  --sourced:#1c5637; --refused:#8f3a24; --unknown:#6b5a1f; --accent:#16181d;
}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);
  font:17px/1.5 Newsreader,Georgia,'Iowan Old Style',serif;
  -webkit-font-smoothing:antialiased}
.wrap{max-width:60rem;margin:0 auto;padding:2.2rem 1.3rem 5rem}
.mono{font-family:'IBM Plex Mono',ui-monospace,SFMono-Regular,Menlo,monospace}
h1{font-size:1.9rem;line-height:1.1;margin:0 0 .3rem;letter-spacing:-.015em}
h2{font-size:.72rem;letter-spacing:.16em;text-transform:uppercase;color:var(--mute);
  font-family:'IBM Plex Mono',ui-monospace,Menlo,monospace;font-weight:600;
  margin:2.6rem 0 .8rem;padding-bottom:.4rem;border-bottom:1px solid var(--rule)}
p.lead{color:var(--mute);margin:0 0 1.2rem;max-width:44rem}
a{color:inherit}

/* the counters: live, and labelled live */
.counts{display:flex;flex-wrap:wrap;gap:0;border:1px solid var(--rule);
  background:var(--card);margin-bottom:1.4rem}
.counts div{flex:1 1 7rem;padding:.7rem .85rem;border-right:1px solid var(--rule)}
.counts div:last-child{border-right:0}
.counts b{display:block;font-size:1.35rem;line-height:1.1;
  font-family:'IBM Plex Mono',ui-monospace,Menlo,monospace}
.counts span{font-size:.66rem;letter-spacing:.1em;text-transform:uppercase;
  color:var(--mute);font-family:'IBM Plex Mono',ui-monospace,Menlo,monospace}

form.ask{display:flex;gap:.5rem;margin:0 0 .6rem}
form.ask input{flex:1;padding:.62rem .75rem;border:1px solid var(--rule);
  background:#fff;font:inherit;font-size:.95rem}
form.ask button{padding:.62rem 1.1rem;background:var(--ink);color:var(--paper);
  border:0;cursor:pointer;font:inherit;font-size:.9rem}
.filters{font-size:.74rem;color:var(--mute);margin:0 0 1.6rem;
  font-family:'IBM Plex Mono',ui-monospace,Menlo,monospace}
.filters a{margin-right:.7rem;text-decoration:none;border-bottom:1px solid var(--rule);
  padding-bottom:1px}
.filters a.on{border-bottom:2px solid var(--ink);font-weight:600}

/* THE SHELF. One row per claim. The refusal sits in the SAME column as the evidence —
   that is the whole argument of the product, rendered as a layout rather than said. */
.row{border-top:1px solid var(--rule);padding:.85rem 0;display:grid;
  grid-template-columns:6.4rem 1fr;gap:0 1rem;align-items:start}
.row:last-child{border-bottom:1px solid var(--rule)}
.tag{font-family:'IBM Plex Mono',ui-monospace,Menlo,monospace;font-size:.6rem;
  letter-spacing:.09em;font-weight:600;padding-top:.3rem}
.tag.sourced{color:var(--sourced)} .tag.unsourced,.tag.refuted{color:var(--refused)}
.tag.unknown,.tag.not_cleared{color:var(--unknown)}
.claim{margin:0 0 .3rem;font-size:.98rem}
.evidence{margin:.25rem 0 0;padding-left:.85rem;border-left:3px solid var(--sourced);
  color:#2c3038;font-size:.9rem}
.refusal{margin:.25rem 0 0;padding-left:.85rem;border-left:3px solid var(--refused);
  color:#2c3038;font-size:.9rem}
.meta{font-family:'IBM Plex Mono',ui-monospace,Menlo,monospace;font-size:.66rem;
  color:var(--mute);margin:.35rem 0 0}
.meta a{color:var(--mute)}
.settles{font-style:italic;color:var(--mute)}
.evidence.thin{border-left-color:var(--unknown);color:#4a4438}
.thinflag{font-family:'IBM Plex Mono',ui-monospace,Menlo,monospace;font-size:.66rem;
  color:var(--unknown);margin:.3rem 0 0;padding-left:.85rem}

/* the curve exhibit — visually a different object from the live shelf */
.exhibit{background:var(--card);border:1px solid var(--rule);padding:1.1rem 1.2rem}
.exhibit table{width:100%;border-collapse:collapse;font-size:.8rem;
  font-family:'IBM Plex Mono',ui-monospace,Menlo,monospace}
.exhibit th{text-align:left;font-size:.6rem;letter-spacing:.09em;text-transform:uppercase;
  color:var(--mute);font-weight:600;padding:0 .5rem .4rem 0}
.exhibit td{padding:.3rem .5rem .3rem 0;border-top:1px solid var(--rule);
  vertical-align:middle}
.bar{display:block;height:.5rem;background:var(--sourced);min-width:1px}
.bar.flat{background:var(--mute);opacity:.45}
.prov{font-size:.7rem;color:var(--mute);margin:.9rem 0 0;line-height:1.45;
  font-family:'IBM Plex Mono',ui-monospace,Menlo,monospace}
.note{font-size:.82rem;color:var(--mute);margin:.7rem 0 0;max-width:46rem}
.warn{border-left:3px solid var(--unknown);padding-left:.8rem;font-size:.82rem;
  color:#4a4438;margin:1rem 0 0;max-width:46rem}
@media(max-width:620px){.row{grid-template-columns:1fr}.tag{padding-top:0}}
"""

_SHELL = """<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Agent Science — the registry</title>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Newsreader:opsz,wght@6..72,400;6..72,600&display=swap" rel="stylesheet">
<style>__CSS__</style></head><body><div class="wrap">__BODY__</div></body></html>"""


def _tag(label: str) -> str:
    cls = (label or "").lower().replace("-", "_")
    return f'<span class="tag {cls}">{html.escape(label or "")}</span>'


def _row_html(r: dict) -> str:
    """One claim. SOURCED shows the span; a refusal shows the cause in the same slot."""
    out = [f'<div class="row">{_tag(r["label"])}<div>']
    out.append(f'<p class="claim">{html.escape((r.get("established") or "")[:400])}</p>')
    if r["label"] == "SOURCED" and (r.get("quoted_terms") or "").strip():
        cls = "evidence thin" if r.get("thin") else "evidence"
        out.append(f'<p class="{cls}">“'
                   + html.escape((r["quoted_terms"] or "")[:420]) + '”</p>')
        if r.get("thin"):
            out.append('<p class="thinflag">Thin evidence — this span carries '
                       f'{r["coverage"]:.0%} of the claim\'s terms. It is verbatim and '
                       "it is in the cited document; read it before you rely on it.</p>")
    else:
        meaning = r.get("meaning") or (r.get("cause") or "not cleared")
        out.append(f'<p class="refusal">{html.escape(meaning)}')
        if r.get("settles_it"):
            out.append(f' <span class="settles">Settled by: '
                       f'{html.escape(r["settles_it"])}.</span>')
        out.append("</p>")
    meta = []
    if r.get("citation_url"):
        u = html.escape(r["citation_url"])
        meta.append(f'<a href="{u}">{html.escape(r["citation_url"][:78])}</a>')
    if r.get("cause"):
        meta.append(html.escape(r["cause"]))
    if r.get("basis"):
        meta.append(html.escape(r["basis"]))
    if r.get("reused"):
        meta.append(f'reused {r["reused"]}x — cleared once, free since')
    if r.get("first_seen_in"):
        meta.append(html.escape(r["first_seen_in"]))
    if meta:
        out.append('<p class="meta">' + " · ".join(meta) + "</p>")
    out.append("</div></div>")
    return "".join(out)


def _filters_html(active_label: str, q: str) -> str:
    def link(name, value):
        qs = {}
        if value:
            qs["label"] = value
        if q:
            qs["q"] = q
        href = "?" + urlencode(qs) if qs else "?"
        on = " on" if (active_label or "") == (value or "") else ""
        return f'<a class="f{on}" href="{html.escape(href, quote=True)}">{name}</a>'

    return ('<p class="filters">' + link("everything", "") + link("sourced", "SOURCED")
            + link("unsourced", "UNSOURCED") + link("unknown", "UNKNOWN")
            + link("refuted", "REFUTED") + link("thin evidence", "THIN") + "</p>")


def _curve_html() -> str:
    """The exhibit. Its provenance is not decoration — see clearance/curve.py."""
    peak = max(l.reuse for l in curve.LEGS) or 1.0
    rows = []
    for l in curve.LEGS:
        w = 100 * l.reuse / peak
        rows.append(
            f"<tr><td>{l.n}</td><td>{html.escape(l.script)}</td>"
            f"<td>{l.claims}</td><td>{l.from_memory}</td>"
            f'<td style="width:38%"><span class="bar" style="width:{w:.0f}%"></span></td>'
            f"<td>{l.reuse:.0%}</td><td>${l.cost_per_claim:.5f}</td></tr>")
    return (
        '<div class="exhibit">'
        "<table><tr><th>leg</th><th>script</th><th>claims</th><th>from memory</th>"
        "<th>reuse</th><th></th><th>cost/claim</th></tr>" + "".join(rows) + "</table>"
        f'<p class="note"><b>{html.escape(curve.WHAT_IS_TRUE)}</b></p>'
        f'<p class="note">{html.escape(curve.WHAT_IS_NOT_TRUE)} '
        f"{html.escape(curve.WHY)}</p>"
        f'<p class="prov">{html.escape(curve.PROVENANCE)}</p>'
        "</div>")


def _live_note(st: dict) -> str:
    """Separate the live counters from the cited curve. ALWAYS — never conditionally.

    Two correct numbers side by side assert a relationship nobody checks. The curve is a
    real measurement on 56 claims from four scripts; this registry is a different
    population. An earlier version of this function only spoke up when the live reuse
    counter read zero — which meant the moment anyone ran a query against the desk, the
    warning vanished and the page went back to implying the curve described the shelf
    above it. A guarantee that switches itself off on use is not a guarantee.
    """
    n = st.get("reuses") or 0
    if n:
        state = (f"This registry's own reuse counter reads <b>{n}</b>, from queries run "
                 "against this desk.")
    else:
        state = ("This registry's own reuse counter reads <b>0</b>. It was seeded by a "
                 "corpus backfill and no production has queried it since.")
    return ('<p class="warn">' + state + " The curve above is a SEPARATE measurement on "
            "a different population, made once, in August 2026. The two numbers are not "
            "comparable and neither is evidence for the other. Every query you run here "
            "is logged and moves the live one.</p>")


def render_page(*, q: str = "", db: Path | str | None = None,
                desk_href: str = "/", label: str = "") -> str:
    """The registry's face: what has been cleared, what was refused, and why.

    Three zones, deliberately not blended. THE SHELF is live and browsable. THE NEGATIVE
    SPACE counts the refusals, because a refusal is the expensive half nobody else
    accumulates. THE CURVE is a cited exhibit from a different population and says so.
    """
    dbp = _db(db)
    con = refusal_log.connect(dbp)
    st = refusal_log.stats(con)
    result = ask(q, db=dbp) if q.strip() else None
    thin, sourced_n = refusal_log.thin_evidence_count(con)
    shelf = refusal_log.browse_claims(con, label=label or None, q=q or None, limit=120)
    causes = refusal_log.by_cause(con)
    prods = refusal_log.productions(con)

    body = [
        "<h1>The registry</h1>",
        '<p class="lead">Every claim this desk has ever cleared or refused, and the '
        "reason for each. An answer is a verbatim span from a real source, or a refusal "
        "with a named cause. There is no third option and no paraphrase.</p>",
        '<div class="counts">'
        f'<div><b>{st["n"]}</b><span>claims</span></div>'
        f'<div><b>{st["cleared"]}</b><span>sourced</span></div>'
        f'<div><b>{st["refused"]}</b><span>refused</span></div>'
        f'<div><b>{thin}</b><span>thin evidence</span></div>'
        f'<div><b>{st["reuses"]}</b><span>reuses</span></div>'
        f'<div><b>{st["productions"]}</b><span>productions</span></div></div>',
        f'<form class="ask" method="get" action=""><input type="text" name="q" '
        f'value="{html.escape(q, quote=True)}" placeholder="Ask the registry…" autofocus>'
        f'<button type="submit">Query</button></form>',
        _filters_html(label, q),
    ]
    if thin:
        body.append(
            f'<p class="warn"><b>{thin} of {sourced_n} sourced rows rest on thin '
            "evidence</b> — the span is verbatim and it is in the cited document, but it "
            "carries little of what the claim says, usually because the page had no "
            "better sentence to offer. They are marked on the row and filterable above. "
            "A cleared claim quoting page furniture is worse than an honest refusal, so "
            "this desk prints the number rather than letting you find it one row at a "
            "time.</p>")

    if result:
        body.append("<h2>Answer</h2>")
        body.append(_row_html({
            "label": result["label"],
            "established": result.get("established") or result["query"],
            "quoted_terms": result.get("quoted_terms"),
            "citation_url": result.get("citation_url"),
            "cause": result.get("cause"),
            "meaning": (refusal_log.explain(result.get("cause"))[0]
                        or result.get("why") or ""),
            "settles_it": (result.get("resolves_with")
                           or refusal_log.explain(result.get("cause"))[1]),
            "reused": result.get("reused"),
            "first_seen_in": result.get("first_seen_in"),
        }))

    body.append(f"<h2>The shelf — {shelf['total']} claim"
                f"{'' if shelf['total'] == 1 else 's'}"
                f"{' matching' if (q or label) else ''}</h2>")
    if shelf["rows"]:
        body += [_row_html(r) for r in shelf["rows"]]
        if shelf["total"] > len(shelf["rows"]):
            body.append(f'<p class="meta">showing {len(shelf["rows"])} of '
                        f'{shelf["total"]} — narrow with a query</p>')
    else:
        body.append('<p class="lead">Nothing on the shelf matches. That is an honest '
                    "miss, not an answer.</p>")

    body.append("<h2>The negative space</h2>")
    body.append('<p class="lead">A refusal is expensive to produce — a search, several '
                "documents fetched and read, an independence assessment — and it is the "
                "half a marketplace has no reason to build. It is kept here, counted and "
                "actionable.</p>")
    body.append('<div class="exhibit"><table><tr><th>label</th><th>cause</th>'
                "<th>n</th><th>what it means</th><th>settled by</th></tr>"
                + "".join(
                    f"<tr><td>{html.escape(c['label'])}</td>"
                    f"<td>{html.escape(c['cause'] or '—')}</td><td>{c['n']}</td>"
                    f"<td>{html.escape(c['meaning'] or '—')}</td>"
                    f"<td>{html.escape(c['settles_it'] or '—')}</td></tr>"
                    for c in causes)
                + "</table></div>")

    body.append("<h2>Productions</h2>")
    body.append('<div class="exhibit"><table><tr><th>production</th><th>claims</th>'
                "<th>sourced</th></tr>"
                + "".join(f"<tr><td>{html.escape(p['p'])}</td><td>{p['n']}</td>"
                          f"<td>{p['cleared']}</td></tr>" for p in prods)
                + "</table></div>")

    body.append("<h2>Why it gets cheaper — the compounding curve</h2>")
    body.append(_curve_html())
    body.append(_live_note(st))

    body.append(f'<p class="meta" style="margin-top:2.4rem">'
                f'<a href="{html.escape(desk_href, quote=True)}">← the clearance desk</a>'
                f" · /registry/api?q= for JSON</p>")
    return _SHELL.replace("__CSS__", _CSS).replace("__BODY__", "".join(body))


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
