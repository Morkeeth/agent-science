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
import re
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Optional
from urllib.parse import parse_qs, quote, urlencode, urlparse

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
/* inline-block, not inline: at 390px the two-word chip "thin evidence" broke across
   two lines, which made its box span 21px->390px and run its underline flush into the
   viewport edge. bodyScrollWidth stayed 390 the whole time, so the measurement said the
   page was clean and only looking at it said otherwise. */
.filters a{margin-right:.7rem;text-decoration:none;border-bottom:1px solid var(--rule);
  padding-bottom:1px;display:inline-block}
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
.exhibit{background:var(--card);border:1px solid var(--rule);
  padding:1.1rem 1.2rem;overflow-x:auto}
/* A wide table scrolls inside its own box. Measured at a REAL 390px
   viewport (document.documentElement.clientWidth === 390, not a cropped
   screenshot): the causes table pushed the page to 411px and the whole
   body scrolled sideways. */
.exhibit table{min-width:26rem}
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

/* ============================================================ THE FRONT SURFACE
   ONE signature device, taken from this subject and from nothing else: THE NEAR-MISS
   STACK. Two spans, the same anchor, one numeral apart. The anchor is underlined in
   both so you can see it is identical; the provision citation is BOXED so you can see
   it is not. Everything a keyword grounder checks is drawn as matching; the one thing
   it does not check is drawn as the difference. The layout is the argument — delete the
   marks and the page has to make the point in a sentence instead, and loses it. */
.hero{border:1px solid var(--rule);background:var(--card);margin:0 0 2rem}
.hero-head{padding:1.05rem 1.2rem .9rem;border-bottom:1px solid var(--rule)}
.hero-kicker{font-family:'IBM Plex Mono',ui-monospace,Menlo,monospace;font-size:.6rem;
  letter-spacing:.18em;text-transform:uppercase;color:var(--refused);font-weight:600;
  margin:0 0 .5rem}
.hero-claim{margin:0;font-size:1.12rem;line-height:1.35}
.hero-body{padding:1.05rem 1.2rem 1.2rem}

/* the two candidate readings, stacked */
.nearmiss{display:grid;grid-template-columns:8.5rem 1fr;gap:0 1.1rem;
  border-top:1px solid var(--rule);padding:.95rem 0 .1rem}
.nearmiss:first-of-type{border-top:0}
.nm-side{font-family:'IBM Plex Mono',ui-monospace,Menlo,monospace;font-size:.63rem;
  letter-spacing:.08em;line-height:1.55;color:var(--mute)}
.nm-verdict{display:block;font-weight:600;letter-spacing:.1em;margin:0 0 .35rem}
.nm-verdict.pass{color:var(--sourced)} .nm-verdict.fail{color:var(--refused)}
.nm-span{margin:0;font-size:.92rem;line-height:1.6;color:#2c3038}
.nm-span .anchor{border-bottom:2px solid var(--sourced);padding-bottom:1px}
.nm-cite{font-family:'IBM Plex Mono',ui-monospace,Menlo,monospace;font-size:.84em;
  border:1.5px solid var(--refused);color:var(--refused);padding:0 .28em;
  border-radius:2px;white-space:nowrap;font-weight:600}
.nm-cite.ok{border-color:var(--sourced);color:var(--sourced)}
.nm-why{margin:.5rem 0 0;font-size:.82rem;color:#4a4438;line-height:1.5}
.nm-why code{font-family:'IBM Plex Mono',ui-monospace,Menlo,monospace;font-size:.92em}
.checks{list-style:none;margin:.1rem 0 0;padding:0;
  font-family:'IBM Plex Mono',ui-monospace,Menlo,monospace;font-size:.68rem;
  color:var(--mute);line-height:1.85}
.checks li:before{content:"✓ ";color:var(--sourced);font-weight:600}
.checks li.no:before{content:"✕ ";color:var(--refused)}
.hero-foot{border-top:1px solid var(--rule);padding:.8rem 1.2rem;
  font-family:'IBM Plex Mono',ui-monospace,Menlo,monospace;font-size:.66rem;
  color:var(--mute);line-height:1.6}
.hero-foot a{color:var(--mute)}

/* the curve — two panels, ONE measure each, never two scales on one axis */
.panels{display:grid;grid-template-columns:1fr 1fr;gap:1.2rem}
@media(max-width:640px){.panels{grid-template-columns:1fr}}
.panel{border:1px solid var(--rule);background:var(--card);padding:.95rem 1rem 1rem}
.panel h3{margin:0 0 .1rem;font-size:.92rem;font-weight:600;letter-spacing:-.01em}
.panel p.sub{margin:0 0 .8rem;font-size:.72rem;color:var(--mute);line-height:1.5;
  font-family:'IBM Plex Mono',ui-monospace,Menlo,monospace}
.panel svg{display:block;width:100%;height:auto;overflow:visible}
.axis{stroke:var(--rule);stroke-width:1}
.gridline{stroke:var(--rule);stroke-width:1;opacity:.55}
.tick{font-family:'IBM Plex Mono',ui-monospace,Menlo,monospace;font-size:8.5px;
  fill:var(--mute)}
.vlabel{font-family:'IBM Plex Mono',ui-monospace,Menlo,monospace;font-size:9.5px;
  font-weight:600}
.bar-reuse{fill:var(--sourced)} .bar-cost{fill:var(--mute);opacity:.55}
.hero-num{font-family:'IBM Plex Mono',ui-monospace,Menlo,monospace;font-weight:600;
  font-size:2rem;line-height:1;letter-spacing:-.02em}

/* the audit page */
.cand{border-top:1px solid var(--rule);padding:.9rem 0}
.cand:last-of-type{border-bottom:1px solid var(--rule)}
.cand-head{font-family:'IBM Plex Mono',ui-monospace,Menlo,monospace;font-size:.64rem;
  letter-spacing:.08em;margin:0 0 .4rem;color:var(--mute)}
.cand-head b.no{color:var(--refused)} .cand-head b.yes{color:var(--sourced)}
.cand-span{margin:0;padding-left:.85rem;font-size:.9rem;line-height:1.6;color:#2c3038;
  border-left:3px solid var(--rule)}
.cand-span.no{border-left-color:var(--refused)}
.cand-span.yes{border-left-color:var(--sourced)}
.cand-why{margin:.45rem 0 0;padding-left:.85rem;font-size:.78rem;color:#4a4438;
  font-family:'IBM Plex Mono',ui-monospace,Menlo,monospace;line-height:1.55}
.empty{border-left:3px solid var(--unknown);padding-left:.8rem;font-size:.84rem;
  color:#4a4438;max-width:46rem}
.rowlink{font-family:'IBM Plex Mono',ui-monospace,Menlo,monospace;font-size:.64rem;
  text-decoration:none;border-bottom:1px solid var(--rule)}

/* PHONE. Measured at a real 390px viewport, not a cropped 500px screenshot: the
   near-miss grid held its 8.5rem label column, leaving the span about fourteen
   characters wide and the label a tall thin ribbon beside it. The device only works
   when the two readings sit one above the other, which is also how they should be read. */
@media(max-width:640px){
  .nearmiss{grid-template-columns:1fr;gap:.45rem 0;padding:1rem 0 .3rem}
  .nm-side{display:flex;flex-wrap:wrap;align-items:baseline;gap:0 .6rem;font-size:.6rem}
  .nm-verdict{margin:0}
  .hero-head,.hero-body,.hero-foot{padding-left:.9rem;padding-right:.9rem}
  .nm-span{font-size:.88rem;line-height:1.55}
  .hero-claim{font-size:1rem}
  /* THE SHELF WAS NEVER PHONE-CHECKED, ONLY THE FRONT PAGE WAS. Measured with real
     device emulation 2026-08-31: /registry read clientWidth 390 and bodyScrollWidth
     486 — a 96px horizontal scroll on the one page the front surface sends a stranger
     to. Long unbreakable source URLs in .meta and unhyphenated claim text pushed the
     body; the row text is prose, not a table, so it wraps rather than scrolls. */
  .claim,.refusal,.meta,.settles,.row{overflow-wrap:anywhere;word-break:break-word}
}

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
                f' · <a href="/front">the front surface</a>'
                f" · /registry/api?q= for JSON</p>")
    return _SHELL.replace("__CSS__", _CSS).replace("__BODY__", "".join(body))



# ============================================================== THE NEAR-MISS STACK
#
# The signature device. It marks TWO things inside a span the engine produced, and it
# marks them by searching that span — never by re-typing it:
#
#   the ANCHOR          the distinctive phrase the claim demanded, underlined. Identical
#                       in both readings, which is the point: every test a keyword
#                       grounder runs is a test on this substring.
#   the CITATION        the provision the clause is actually about, boxed. This is the
#                       only difference between a €15,000,000 answer and a €35,000,000
#                       one, and it is one numeral wide.
#
# If either mark cannot be found in the span, the span renders PLAIN. It is never
# rewritten to make a mark fit: the text on this page has to be the text the engine
# judged, character for character, or the page is doing what the product refuses.

def _mark_span(span: str, *, must_contain: str, claim: str,
               rivals: frozenset = frozenset()) -> str:
    """Escape, then mark the anchor and ONLY the citations the engine spoke about.

    Escaping AFTER inserting tags would escape the tags, so both needles are matched
    against the already-escaped string.

    THE MARK MUST NOT ASSERT MORE THAN THE ENGINE DID. The first version boxed EVERY
    provision it could find and coloured it by whether the claim mentioned it — which
    put a refusal-red box around "Articles 5" inside the span that CLEARS the true
    claim, because that sentence names Article 5 in order to exclude it. Two correct
    facts adjacent, asserting a relation neither supports: the row was right, the mark
    said it was wrong, and nothing on the page checked the mark against the verdict.
    So: green marks the provision the CLAIM is about; red marks only a provision the
    engine's own finding named as the rival. Everything else stays plain text.
    """
    from clearance import semantic as _sem

    text = html.escape(span or "")
    marks = []                                   # (start, end, css class)
    # CASE-INSENSITIVE, because the registry stores the anchor normalised (lowercased)
    # while the span is the document's own casing. Matching exactly meant the audit page
    # underlined nothing at all and the reader could not see that both readings turn on
    # the same substring — the one fact the whole device exists to show.
    anchor = html.escape(must_contain or "")
    if anchor:
        at = text.lower().find(anchor.lower())
        if at >= 0:
            marks.append((at, at + len(anchor), "anchor"))

    wanted = {n for _h, n in _sem.provisions(claim or "")}
    for m in _sem._PROVISION.finditer(text):
        num = m.group(2)
        if num in wanted:
            marks.append((m.start(), m.end(), "nm-cite ok"))
        elif num in rivals:
            marks.append((m.start(), m.end(), "nm-cite"))

    # Overlaps would produce crossed tags. Keep the first of any overlapping pair:
    # deterministic, and it degrades to an unmarked span, never to broken markup.
    marks.sort()
    kept, last = [], -1
    for a, b, cls in marks:
        if a >= last:
            kept.append((a, b, cls))
            last = b
    out, pos = [], 0
    for a, b, cls in kept:
        out += [text[pos:a], f'<span class="{cls}">', text[a:b], "</span>"]
        pos = b
    out.append(text[pos:])
    return "".join(out)


def _rivals_named_by(detail: str, claim: str = "") -> frozenset:
    """The provision numbers the engine's own finding names AS THE RIVAL.

    Reading them back out of the finding keeps the mark downstream of the engine: the
    page cannot box a citation the refusal did not mention.

    It reads the `cites …` clause specifically, not everything after the semicolon. The
    finding's sentence ends "…cites Article 5 and never Article 50", so a looser parse
    pulled BOTH numbers out and the page then boxed the claim's own provision in
    refusal-red wherever it appeared. `claim` is subtracted as well, so the two
    independent ways of getting this wrong both have to fail at once.
    """
    from clearance import semantic as _sem
    if not detail:
        return frozenset()
    m = re.search(r"\bcites\s+(.*?)\s+and never\b", detail)
    text = m.group(1) if m else (detail.split(";", 1)[1] if ";" in detail else detail)
    # "cites Article 5, 7" — the head noun is written once and the rest are bare numbers.
    head = next((h for h, _n in _sem.provisions(text)), "")
    nums = {n for _h, n in _sem.provisions(text)}
    if head:
        nums |= {t for t in re.findall(r"\b\d+\b", text)}
    return frozenset(nums - {n for _h, n in _sem.provisions(claim or "")})


def _nearmiss_html(*, side: str, verdict: str, passed: bool, span: str,
                   must_contain: str, claim: str, why: str = "",
                   rivals: frozenset = frozenset()) -> str:
    cls = "pass" if passed else "fail"
    # No placeholder for an absent span. "— no span" read as "the desk found nothing",
    # which is the opposite of what this row says: it read the SAME span as the row
    # above it and refused it.
    body = (f'<p class="nm-span">{_mark_span(span, must_contain=must_contain, claim=claim, rivals=rivals)}</p>'
            if span else "")
    return (f'<div class="nearmiss"><div class="nm-side">'
            f'<span class="nm-verdict {cls}">{html.escape(verdict)}</span>'
            f'{html.escape(side)}</div><div>{body}'
            + (f'<p class="nm-why">{why}</p>' if why else "") + "</div></div>")


EVAL_PATH = Path(__file__).resolve().parent / "docs/EVAL-citation-conflict-2026-08-31.json"
EVAL_COMMAND = "python3 scripts/eval_citation_conflict.py"


def _measurement_html() -> str:
    """What this mechanism has and has not been shown to cost. Read from the eval file.

    THE SENTENCE THIS EXISTS TO PREVENT. "Measured on 312 claims, zero false refusals"
    is true and it is the wrong object: zero of the 27 claims it clears on research-corpus/
    cite a provision at all, so the population contains no case the check could have got
    wrong.

    AND THAT DENOMINATOR USED TO MOVE ON ITS OWN. It read 314 until 2026-08-31 because
    `clearance.ingest` wrote claim files INTO `research-corpus/` — the directory the eval
    replays — so using the product changed its own published population, and a clean
    checkout read 312. The corpus is now frozen and hashed (`research-corpus/MANIFEST.json`),
    ingest writes to `research-inbox/`, and the number here is read from the eval receipt,
    which names the population and the day it was frozen.

    AND THE WORD "SHELF" WAS DOING A SECOND JOB IT WAS NOT ENTITLED TO. This paragraph
    counted research-corpus/ (312 claims, 27 cleared) and called it "this shelf"; a
    thousand pixels below, "the negative space, counted" prints the registry database
    (179 claims, 29 cleared) and calls that the shelf too. Two correct numbers, one
    screen apart, under one noun — the adjacency defect `clearance/curve.py` has a
    whole docstring about, committed one paragraph away from the disclaimer that
    prevented it for the curve. Corrected 2026-08-31: the population is named. A number produced by a population that cannot exercise the mechanism is not
    evidence the mechanism is safe — it is evidence nobody has looked yet, and it reads
    identically. So the count that matters is printed FIRST, and it is a count of
    eligible rows, not of verdicts unchanged.

    AND THE STRIP ITSELF CARRIED THE NIGHT'S OWN DEFECT. Until 2026-08-31 05:5x it said
    "its only evidence is the two cases above" — on a page that, one block higher, now
    prints the 11-claim held-out probe (SHIPS 9/11, BASE 7/11) beside the recall
    boundary. Two correct blocks, one screen apart, one denying the other's existence.
    Pinned by `t_the_measurement_strip_does_not_deny_the_heldout_probe`.
    """
    import json
    if not EVAL_PATH.exists():
        return ""
    try:
        e = json.loads(EVAL_PATH.read_text())
    except (ValueError, OSError):
        return ""
    g, a, r = e["gold"], e["attribution"], e["registry"]
    arms = [k for k in ("BASE", "CONFLICT", "ABSENCE") if f"correct_{k}" in g]
    gold_line = "; ".join(f"{k.lower()} {g['correct_' + k]}/{g['n']}" for k in arms)
    changed = len(r["flips"].get("CONFLICT", []))
    pop = r.get("population") or {}
    return (
        '<p class="warn"><b>What this check has been shown to cost, and what it '
        "has not.</b> On the labelled held-out set it costs nothing: "
        f"{html.escape(gold_line)}, unchanged. Replayed over <code>research-corpus/</code>"
        f" — {r['total']} claims across {pop.get('files', '?')} files, FROZEN "
        f"{html.escape(str(pop.get('frozen_at', 'unknown')))} and hashed in "
        "<code>research-corpus/MANIFEST.json</code> so this denominator cannot move when "
        "the product is used; a DIFFERENT population from the registry counted lower "
        f"down this page — it changes {changed} verdicts, and that number is not "
        f"evidence of safety, because <b>{a['cite_a_provision']} of the {a['greens']} "
        "claims it clears there cite a provision at all</b>. That corpus cannot "
        "exercise the mechanism. Its evidence is the two cases above, one of which is "
        "the case it was built for, plus the 11-claim held-out probe stated with the "
        "boundary higher up this page. The looser arm — refusing when the span "
        "never names the provision — is built and measured and does NOT ship, for the "
        f"same reason. Reproduce: <code>{html.escape(EVAL_COMMAND)}</code>.</p>")


def _wedge_html() -> str:
    """The first ten seconds. Rendered from the engine's receipt, or not at all.

    There is no written-down fallback and there must never be one: a page that can
    print a verdict the engine did not produce is the product's own founding defect,
    committed by the surface built to sell against it.
    """
    from clearance import wedge as W

    r = W.receipt()
    if not r:
        return ('<div class="hero"><div class="hero-body"><p class="empty">The wedge '
                "has no receipt on this machine. It is produced by <code>"
                f"{html.escape(W.COMMAND)}</code>, which fetches the cited instrument "
                "and runs the shipping engine. Nothing is rendered from memory.</p>"
                "</div></div>")

    by_id = {c["id"]: c for c in r["cases"]}
    one, two = by_id.get("WEDGE-1"), by_id.get("WEDGE-2")
    if not one:
        return ""

    base_span = one["base"].get("quoted_terms") or ""
    detail = (one["ships"].get("trail") or [{}])[0].get("detail") or ""
    # The detail is `code: sentence`. The code is already printed beside it.
    detail = detail.split(":", 1)[1].strip() if ":" in detail else detail

    rivals = _rivals_named_by((one["ships"].get("trail") or [{}])[0].get("detail") or "",
                               one["claim"])
    cov = one.get("coverage")
    # The third test is printed with its MEASURED value, not as an adjective beside it.
    # Both lines said the same thing and one of them had a number, which made the other
    # decoration.
    passes = list(W.KEYWORD_GROUNDER_PASSES)
    if cov is not None:
        passes[-1] = f"carries {cov:.0%} of the claim's content terms"
    checks = "".join(f"<li>{html.escape(c)}</li>" for c in passes)
    out = [
        '<div class="hero">',
        '<div class="hero-head">',
        '<p class="hero-kicker">the near miss — one numeral, twenty million euro</p>',
        f'<p class="hero-claim">{html.escape(one["claim"])}</p>',
        "</div><div class=\"hero-body\">",
        _nearmiss_html(
            # Dated from the receipt, never "today": the label would be a sentence the
            # receipt's own produced_at contradicts within twenty-four hours.
            side=(f"this engine on {r['produced_at'][:10]} with the check off, and what "
                  "any keyword-grounded answer returns: a citation, a verbatim quote, "
                  "a green tick"),
            verdict=one["base"]["label"], passed=one["base"]["verdict"] == "GREEN",
            span=base_span, must_contain=one["must_contain"], claim=one["claim"],
            rivals=rivals,
            why='<ul class="checks">' + checks + "</ul>"),
        _nearmiss_html(
            side="what this desk returns",
            verdict=one["ships"]["label"], passed=one["ships"]["verdict"] == "GREEN",
            span="", must_contain="", claim="",
            why=(f'<code>{html.escape(one["ships"].get("refusal_code") or "")}</code> — '
                 + html.escape(detail))),
    ]
    if two:
        out.append(_nearmiss_html(
            side="the same desk, the same article, the true claim",
            verdict=two["ships"]["label"], passed=two["ships"]["verdict"] == "GREEN",
            span=two["ships"].get("quoted_terms") or "",
            must_contain=two["must_contain"], claim=two["claim"],
            why=html.escape(two["note"])
                + " The span stops before point (g); the desk cleared it because "
                  "nothing in the clause it quotes claims a different article, and "
                  "absence alone is not a refusal here."))
    out.append("</div>")
    out.append('<p class="hero-foot"><b>What this refuses, and what it does not.</b> '
               + html.escape(W.RECALL_BOUNDARY) + "</p>")
    out.append('<p class="hero-foot">'
               + html.escape(W.PROVENANCE)
               + f' Document: <a href="{html.escape(W.URL, quote=True)}">'
               + html.escape(W.INSTRUMENT) + "</a>, "
               + f'{r["document_chars"]:,} characters fetched {html.escape(r["produced_at"][:10])}. '
               + '<a class="rowlink" href="/refusal?term='
               + html.escape(quote(one["must_contain"]), quote=True)
               + '">open this refusal and read every span considered →</a>'
               + "</p></div>")
    return "".join(out)


# ================================================================== THE CURVE, DRAWN
#
# TWO PANELS, ONE MEASURE EACH. Reuse is a percentage and cost is a fraction of a cent;
# putting both on one plot needs two y-scales, and a dual-axis chart lets whoever drew it
# choose the crossing point and therefore the conclusion. Side by side on their own
# scales, the reader draws it: one climbs, the other does not. Both baselines are ZERO —
# a cost axis cropped to its own range would render a flat line as a mountain range, and
# "cost stays flat" is the half of this exhibit that is easy to fake and hard to notice.

def _panel(*, title: str, sub: str, values, labels, fmt, bar_class: str,
           ymax: float) -> str:
    W, H = 300.0, 120.0
    left, bottom, top = 26.0, 22.0, 16.0
    plot_w, plot_h = W - left - 6, H - bottom - top
    n = len(values)
    slot = plot_w / n
    bw = slot * 0.46
    bars, ticks = [], []
    for i, (v, lab) in enumerate(zip(values, labels)):
        h = plot_h * (v / ymax) if ymax else 0
        x = left + slot * i + (slot - bw) / 2
        y = top + plot_h - h
        # 4px rounded data-end anchored to the baseline: the corners that touch the
        # axis stay square, so the bar reads as growing FROM the axis.
        bars.append(f'<path class="{bar_class}" d="M{x:.1f},{top + plot_h:.1f} '
                    f'V{y + 3:.1f} q0,-3 3,-3 h{bw - 6:.1f} q3,0 3,3 '
                    f'V{top + plot_h:.1f} Z"/>')
        bars.append(f'<text class="vlabel" x="{x + bw / 2:.1f}" y="{y - 4:.1f}" '
                    f'text-anchor="middle" fill="currentColor">{fmt(v)}</text>')
        ticks.append(f'<text class="tick" x="{x + bw / 2:.1f}" '
                     f'y="{top + plot_h + 11:.1f}" text-anchor="middle">{lab}</text>')
    grid = "".join(
        f'<line class="gridline" x1="{left}" x2="{W - 6}" '
        f'y1="{top + plot_h * (1 - f):.1f}" y2="{top + plot_h * (1 - f):.1f}"/>'
        f'<text class="tick" x="{left - 4}" y="{top + plot_h * (1 - f) + 3:.1f}" '
        f'text-anchor="end">{fmt(ymax * f)}</text>'
        for f in (0.0, 0.5, 1.0))
    return (f'<div class="panel"><h3>{html.escape(title)}</h3>'
            f'<p class="sub">{html.escape(sub)}</p>'
            f'<svg viewBox="0 0 {W:.0f} {H:.0f}" role="img" '
            f'aria-label="{html.escape(title)}">{grid}'
            f'<line class="axis" x1="{left}" x2="{W - 6}" y1="{top + plot_h}" '
            f'y2="{top + plot_h}"/>' + "".join(bars) + "".join(ticks) + "</svg></div>")


def _curve_panels_html() -> str:
    legs = curve.LEGS
    labels = [f"leg {l.n}" for l in legs]
    reuse = [l.reuse for l in legs]
    cost = [l.cost_per_claim for l in legs]
    return (
        '<div class="panels">'
        + _panel(title="Reuse climbs",
                 sub="claims answered from the corpus, no search",
                 values=reuse, labels=labels, fmt=lambda v: f"{v:.0%}",
                 bar_class="bar-reuse", ymax=0.5)
        + _panel(title="Cost per claim does not fall",
                 # "Flat" is the word that would be doing the work here, and it is not
                 # quite true: the four legs are not identical. What IS true is that
                 # there is no downward trend while reuse climbs 46 points. So the
                 # subtitle prints the RANGE, from the same numbers the bars are drawn
                 # from, and lets the reader hold the engine to it.
                 sub=(f"US dollars per claim, axis from zero. "
                      f"Range ${min(cost):.4f}-${max(cost):.4f}; "
                      f"last leg {abs(cost[-1] / cost[0] - 1):.0%} "
                      f"{'below' if cost[-1] < cost[0] else 'above'} the first, "
                      f"and not monotonic."),
                 values=cost, labels=labels, fmt=lambda v: f"${v:.4f}",
                 bar_class="bar-cost", ymax=0.005)
        + "</div>")


# ================================================================= THE AUDIT PAGE
#
# A refusal you must trust is a chatbot. A refusal you can open is the product.

def _trail_html(trail: list, *, claim: str, must_contain: str) -> str:
    if not trail:
        return ""
    out = []
    for i, t in enumerate(trail, 1):
        ok = bool(t.get("admissible"))
        cls = "yes" if ok else "no"
        cov = t.get("coverage")
        head = (f'candidate {i} of {len(trail)} · '
                f'<b class="{cls}">{"ADMISSIBLE" if ok else "REFUSED"}</b>'
                + (f' · carries {cov:.0%} of the claim' if cov is not None else ""))
        out.append(f'<div class="cand"><p class="cand-head">{head}</p>'
                   f'<p class="cand-span {cls}">'
                   + _mark_span(t.get("span") or "", must_contain=must_contain,
                                claim=claim,
                                rivals=_rivals_named_by(t.get("detail") or "", claim))
                   + "</p>")
        if t.get("detail"):
            d = t["detail"]
            code, _, rest = d.partition(":")
            out.append(f'<p class="cand-why"><b>{html.escape(code)}</b> —'
                       f'{html.escape(rest)}</p>')
        out.append("</div>")
    return "".join(out)


def _receipt_row(term: str) -> Optional[dict]:
    """A shelf-shaped row rebuilt from the committed wedge receipt, or None.

    Not a fixture standing in for a verdict: every field here was produced by
    `scripts/wedge_receipt.py` running the engine against the fetched instrument. The
    row is marked with the production it came from so the page never implies the local
    shelf holds it.
    """
    from clearance import wedge as W
    r = W.receipt()
    if not r:
        return None
    want = refusal_log.norm_term(term)
    for c in r["cases"]:
        if refusal_log.norm_term(c["must_contain"]) != want:
            continue
        sh = c["ships"]
        return {"term": c["must_contain"], "established": c["claim"],
                "verdict": sh["verdict"], "cause": sh["cause"],
                "refusal_code": sh["refusal_code"], "citation_url": sh["citation_url"],
                "quoted_terms": sh["quoted_terms"], "basis": None, "reused": 0,
                "first_seen_in": f"{W.COMMAND} · {r['produced_at'][:10]}",
                "trail": json.dumps(sh["trail"])}
    return None


def render_refusal(*, term: str, db: Path | str | None = None,
                   home: str = "/") -> str:
    """One row, opened: the claim, every span weighed, and why each was not evidence."""
    con = refusal_log.connect(_db(db))
    row = con.execute("SELECT * FROM claims WHERE term = ? LIMIT 1",
                      (refusal_log.norm_term(term),)).fetchone()
    if row is None:
        # COLD CLONE. `cache/refusal_log.db` is gitignored, so a fresh clone has the
        # committed receipt and an empty shelf — and the front page's one call to action
        # would dead-end on "Not on the shelf" for exactly the reader it was written for.
        # The fallback reads the RECEIPT, which is engine output, so the law holds: this
        # page still cannot print a verdict the engine did not produce.
        row = _receipt_row(term)
    if row is None:
        return _SHELL.replace("__CSS__", _CSS).replace(
            "__BODY__", "<h1>Not on the shelf</h1><p class=\"lead\">No claim in this "
            "registry is keyed by that term. That is an honest miss, not an answer.</p>"
            f'<p class="meta"><a href="{html.escape(home, quote=True)}">← the desk</a></p>')
    r = dict(row)
    label = refusal_log.surface_label(verdict=r["verdict"], cause=r.get("cause"))
    meaning, settles = refusal_log.explain(r.get("cause"))
    trail = refusal_log.trail_of(r)
    has_trail = r.get("trail") is not None

    body = [
        f'<p class="hero-kicker">{html.escape(label)}</p>',
        f'<h1 style="font-size:1.35rem">{html.escape(r["established"][:400])}</h1>',
        '<p class="meta">' + " · ".join(filter(None, [
            html.escape(r.get("cause") or ""),
            f'<code>{html.escape(r["refusal_code"])}</code>' if r.get("refusal_code") else "",
            html.escape(r.get("first_seen_in") or ""),
            f'reused {r["reused"]}x' if r.get("reused") else "",
        ])) + "</p>",
    ]
    if r.get("citation_url"):
        u = html.escape(r["citation_url"], quote=True)
        body.append(f'<p class="meta"><a href="{u}">{html.escape(r["citation_url"][:100])}</a></p>')
    if meaning:
        body.append(f'<p class="lead">{html.escape(meaning)}'
                    + (f' <span class="settles">Settled by: {html.escape(settles)}.</span>'
                       if settles else "") + "</p>")

    body.append(f"<h2>The spans considered — {len(trail)}</h2>")
    if trail:
        # The anchor is the row's TERM — the distinctive phrase the claim demanded.
        # `quoted_terms` on a refusal row is the engine's note about the document, not
        # the claim's anchor, and passing it underlined nothing.
        body.append(_trail_html(trail, claim=r["established"], must_contain=r["term"]))
    elif has_trail:
        body.append('<p class="empty">The locator offered nothing. The document was '
                    "opened and no passage in it carried the claim's anchor at all — "
                    "which is a different fact from a passage that carried it and did "
                    "not support the claim.</p>")
    else:
        body.append('<p class="empty"><b>No trail was recorded for this row.</b> It was '
                    "written to the registry before the audit trail existed "
                    "(2026-08-31). Re-clearing the claim records one. The row is not "
                    "shown with an empty trail, because “nothing was considered” and "
                    "“nobody wrote it down” are different facts and only one of them is "
                    "true here.</p>")
    body.append(f'<p class="meta" style="margin-top:2.2rem">'
                f'<a href="{html.escape(home, quote=True)}">← the desk</a> · '
                f'<a href="/registry">the shelf</a></p>')
    return _SHELL.replace("__CSS__", _CSS).replace("__BODY__", "".join(body))


# ================================================================== THE FRONT PAGE

_NUMBER_WORDS = ("zero", "one", "two", "three", "four", "five", "six", "seven",
                 "eight", "nine", "ten", "eleven", "twelve")


def _spell(n: int) -> str:
    """Small integers as English, so a count and its word can never disagree."""
    return _NUMBER_WORDS[n] if 0 <= n < len(_NUMBER_WORDS) else str(n)


def render_front(*, db: Path | str | None = None, registry_href: str = "/registry") -> str:
    """What a stranger meets. The refusal first, the economics second, the desk third."""
    con = refusal_log.connect(_db(db))
    st = refusal_log.stats(con)
    thin, sourced_n = refusal_log.thin_evidence_count(con)
    causes = refusal_log.by_cause(con)
    refusal_rows = [c for c in causes if c["label"] != "SOURCED"]

    body = [
        "<h1>Agent Science</h1>",
        '<p class="lead">A clearance desk for documentary claims. Every answer is a '
        "verbatim span from a document we fetched, or a refusal with a named cause you "
        "can open and audit. There is no third option, and nothing here paraphrases.</p>",
        _wedge_html(),
        _measurement_html(),

        "<h2>Why it compounds</h2>",
        '<p class="lead">A cleared claim is established once and free to every '
        "production afterwards. The interesting half is that the bill does not fall "
        "with it.</p>",
        _curve_panels_html(),
        f'<p class="note"><b>{html.escape(curve.WHAT_IS_TRUE)}</b></p>',
        f'<p class="note">{html.escape(curve.WHAT_IS_NOT_TRUE)} {html.escape(curve.WHY)}</p>',
        f'<p class="prov">{html.escape(curve.PROVENANCE)}</p>',

        "<h2>The negative space, counted</h2>",
        '<p class="lead">A refusal costs a search, several documents fetched and read, '
        "and an independence assessment. It is the expensive half a marketplace has no "
        "reason to build, so nobody else accumulates it. This desk keeps every one, "
        "with what would settle it.</p>",
        '<div class="counts">'
        f'<div><b>{st["n"]}</b><span>claims</span></div>'
        f'<div><b>{st["cleared"]}</b><span>sourced</span></div>'
        f'<div><b>{st["refused"]}</b><span>refused</span></div>'
        f'<div><b>{thin}</b><span>thin evidence</span></div>'
        f'<div><b>{st["productions"]}</b><span>productions</span></div></div>',
        '<div class="exhibit"><table><tr><th>cause</th><th>n</th>'
        "<th>what it means</th><th>settled by</th></tr>"
        + "".join(f"<tr><td>{html.escape(c['cause'] or '—')}</td><td>{c['n']}</td>"
                  f"<td>{html.escape(c['meaning'] or '—')}</td>"
                  f"<td>{html.escape(c['settles_it'] or '—')}</td></tr>"
                  for c in refusal_rows)
        + "</table></div>",
        # "the other NINE" was a literal beside a count read from CAUSE_ENGLISH. Add a
        # tenth cause and the sentence reads "the other nine ... a closed set of 11":
        # one paragraph contradicting itself, in the warn box that exists to stop the
        # reader inferring a number the data does not support. Derived 2026-08-31.
        ('<p class="warn">Every refusal on this desk currently carries the same cause. '
         "That is a property of how the shelf was filled — a corpus backfill seeds only "
         "the one refusal that carries the document it read — and not a claim that the "
         f"other {_spell(len(refusal_log.CAUSE_ENGLISH) - len(refusal_rows))} causes are "
         "rare. The engine's refusal vocabulary is a closed set of "
         f"{len(refusal_log.CAUSE_ENGLISH)}; this shelf has exercised "
         f"{len(refusal_rows)} of them.</p>") if len(refusal_rows) < 2 else "",
        f'<p class="meta" style="margin-top:2.4rem">'
        f'<a class="rowlink" href="{html.escape(registry_href, quote=True)}">'
        "browse every claim on the shelf →</a></p>",
    ]
    return _SHELL.replace("__CSS__", _CSS).replace("__BODY__", "".join(body))


class _Handler(BaseHTTPRequestHandler):
    """Local surface: the desk, the shelf, and one refusal opened.

    `serve()` referenced this class for a week and it did not exist — `--serve` raised
    NameError on every invocation. Found while rendering the front surface, which is the
    only reason anyone ran it.
    """

    def log_message(self, *a):        # keep the terminal readable
        pass

    def do_GET(self):
        u = urlparse(self.path)
        qs = parse_qs(u.query)
        # `/front` is named in the lane brief, in NIGHTRUN and in the footer of the
        # shelf — and it 404'd, because the handler only ever answered "/". The same
        # defect as `serve()` referencing a `_Handler` that did not exist, one level
        # down: a route nobody requested is a route nobody ran. Pinned by
        # `t_every_internal_link_resolves_to_a_served_route`.
        if u.path.rstrip("/") in ("", "/index.html", "/front"):
            page = render_front()
        elif u.path.rstrip("/") == "/refusal":
            page = render_refusal(term=(qs.get("term") or [""])[0])
        elif u.path.rstrip("/") in ("/registry", ""):
            page = render_page(q=(qs.get("q") or [""])[0].strip(),
                               label=(qs.get("label") or [""])[0].strip())
        else:
            self.send_error(404)
            return
        raw = page.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)


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
