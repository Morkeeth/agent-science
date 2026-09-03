#!/usr/bin/env python3
"""Agent Science HTTP API — the Compounding Desk.

  GET  /health           liveness (not /healthz — GCP reserves *z paths)
  GET  /                 clearance desk UI
  GET  /search?q=         stack websearch (registry → live)
  POST /search            {"query","live?","subject?"}
  POST /ingest            claim markdown or {claim,url}
  GET  /front            the front surface — the wedge, the curve, the negative space
  GET  /refusal?term=    one refusal opened: every span considered, and why each failed
  GET  /registry         browsable verified-truths registry
  GET  /registry/api?q=  JSON registry query (read-only)
  GET  /stats              dictionary economics + recent queries
  GET  /popular            top dev queries + optimization targets (JSON)
  GET  /popular/ui         HTML report for devs
  GET  /truths/ui          truths dashboard — ranked queries + field ★
  GET  /visibility?q=      full truth-layer panel (JSON)
  GET  /visibility/ui?q=     HTML visibility — transparency WOW for judges

Stdlib in the serving path, except the ADK agent that /clear runs through: Agent
Builder is a submission requirement and a requirement is not met by a module nobody
imports. Every gap report names the engine that produced it (`adk` or `direct`), so
"the agent ran" is a field a judge can read rather than a claim in a README.
"""
from __future__ import annotations

import html
import json
import os
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from http.server import BaseHTTPRequestHandler, HTTPServer  # noqa: E402

import agent_science  # noqa: E402
import ask_registry  # noqa: E402
from clearance import ingest as stack_ingest, query_analytics, stack_search  # noqa: E402
from clearance import corpus  # noqa: E402
from clearance import refusal_log  # noqa: E402
from cloud import agent as adk_agent  # noqa: E402
from cloud import partners as partner_manifest  # noqa: E402

# ADK is the default path. Setting this to "0" serves the direct pipeline instead and
# is for controls only — a run with the agent switched off is a different product and
# every report says which one answered.
ADK_DEFAULT = os.environ.get("AGENT_BUILDER", "1").strip().lower() not in (
    "0", "false", "off", "no",
)

# Direction: cool archival paper + ink + stamp red for action only.
# Signature device: the COMPOUND strip (Parallel A-vs-memory numbers).
# Kill: system-ui default, purple, cream/terracotta, status-light theater.
_PAGE = """<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Agent Science — truth companion</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Newsreader:opsz,wght@6..72,400;6..72,600&display=swap" rel="stylesheet">
<style>
:root{
  --paper:#e9ecef;
  --ink:#14161c;
  --mute:#5c6370;
  --line:#c5cad3;
  --stamp:#b42318;
  --band:#dfe3e8;
}
*{box-sizing:border-box}
html,body{margin:0;background:var(--paper);color:var(--ink);
  font-family:"Newsreader",Georgia,serif;font-size:18px;line-height:1.45}
.wrap{max-width:52rem;margin:0 auto;padding:2.5rem 1.25rem 4rem}
.brand{font-size:clamp(2.4rem,6vw,3.6rem);font-weight:600;letter-spacing:-.02em;
  line-height:1.05;margin:0 0 .4rem}
.thesis{color:var(--mute);font-size:1.05rem;max-width:36rem;margin:0 0 2rem}
.desk{border-top:1px solid var(--ink);padding-top:1.25rem}
label{display:block;font-family:"IBM Plex Mono",monospace;font-size:.72rem;
  letter-spacing:.06em;text-transform:uppercase;color:var(--mute);margin:0 0 .35rem}
input[type=text],textarea{
  width:100%;background:#f7f8fa;border:1px solid var(--line);color:var(--ink);
  font:inherit;padding:.7rem .8rem;border-radius:0}
textarea{min-height:14rem;resize:vertical;font-size:1rem}
.row{display:grid;grid-template-columns:1fr auto;gap:1rem;align-items:end;margin-bottom:1rem}
button{
  font-family:"IBM Plex Mono",monospace;font-size:.8rem;letter-spacing:.04em;
  text-transform:uppercase;background:var(--ink);color:var(--paper);
  border:0;padding:.85rem 1.4rem;cursor:pointer}
button:hover{background:#000}
.hint{font-size:.9rem;color:var(--mute);margin:1rem 0 0;max-width:34rem}
.hint code{font-family:"IBM Plex Mono",monospace;font-size:.78rem}
.nav{font-family:"IBM Plex Mono",monospace;font-size:.78rem;margin:0 0 1.5rem}
.nav a{color:var(--ink)}
</style></head><body>
<div class="wrap">
  <h1 class="brand">Agent Science</h1>
  <p class="thesis">Paste a documentary script. Every checkable claim comes back
  <strong>sourced verbatim</strong> with its URL — or <strong>refused with a named cause</strong>
  a lawyer can read. The shelf remembers: second ask is free. Clearance and E&amp;O are
  one vertical on the same truth layer.</p>
<p class="nav"><a href="/front">What this desk refuses, and why that is the product</a> · <a href="/visibility/ui?q=ralph+loop+agentic">Websearch visibility</a> (the websearch companion) · <a href="/registry">Browse the registry</a> · <a href="/truths/ui">Truths dashboard</a> · <a href="/popular/ui">Popular queries</a> — {registry_stats} verified truths on disk.</p>
  <form class="desk" method="post" action="/clear">
    <div class="row">
      <div>
        <label for="subject">Subject shelf</label>
        <input id="subject" name="subject" type="text" value="orphan-works"
          placeholder="e.g. orphan-works" required>
      </div>
      <button type="submit">Clear script</button>
    </div>
    <label for="script">Documentary narration</label>
    <textarea id="script" name="script" required
      placeholder="Paste production narration. Every factual claim comes back SOURCED or UNSOURCED — with the reason."></textarea>
    <p class="hint">Same subject tag on a second script → claims already cleared resolve from
    corpus (no Parallel call). That fraction is the product.
    Try fixtures <code>documentary-orphan-works.txt</code> then
    <code>documentary-orphan-works-B.txt</code>.</p>
  </form>
</div>
</body></html>"""


def _esc(s) -> str:
    return html.escape("" if s is None else str(s), quote=True)


def _log_db() -> Path:
    return agent_science._log_db()


def _registry_stats_line() -> str:
    try:
        st = ask_registry.stats(db=_log_db())
        return f"{st['n']} claims · {st['cleared']} sourced"
    except Exception:
        return "registry loading…"


def _desk_page(subject: str = "orphan-works") -> str:
    page = _PAGE.replace("{registry_stats}", _esc(_registry_stats_line()))
    if subject:
        page = page.replace(
            'value="orphan-works"',
            f'value="{html.escape(subject, quote=True)}"',
            1,
        )
    return page


def _buyer_week_strip() -> str:
    """Recurring number a producer/insurer reports upward: cleared vs caught."""
    try:
        con = refusal_log.connect(_log_db())
        w = refusal_log.week_tally(con)
        return (
            f"<section class='buyer'>"
            f"<p class='compound-label'>Buyer week · last {w['days']} days</p>"
            f"<div class='nums'>"
            f"<div><span class='n'>{_esc(w['cleared'])}</span>"
            f"<span class='k'>Cleared</span></div>"
            f"<div><span class='n hit'>{_esc(w['caught'])}</span>"
            f"<span class='k'>Caught</span></div>"
            f"<div><span class='n'>{_esc(w['n'])}</span>"
            f"<span class='k'>Logged</span></div>"
            f"</div>"
            f"<p class='compound-note'>Claims cleared vs caught — the number they report "
            f"upward. Not model confidence.</p>"
            f"</section>"
        )
    except Exception:
        return ""


def _report_html(out: dict) -> str:
    """Clearance memo: compound strip → action items → sourced evidence."""
    n = out.get("claims_extracted") or 0
    sourced = out.get("sourced") or 0
    unsourced = out.get("unsourced") or 0
    parallel = out.get("parallel_api_calls")
    if parallel is None:
        parallel = out.get("parallel_calls") or 0
    hits = out.get("corpus_hits") or 0
    prior = out.get("prior_run") or {}
    prior_parallel = prior.get("parallel_api_calls")
    remembered = out.get("corpus_remembered") or 0
    subject = _esc(out.get("subject"))
    rows = out.get("rows") or []
    buyer = _buyer_week_strip()

    compound = ""
    delta_note = ""
    if prior_parallel is not None and hits and prior_parallel > parallel:
        delta_note = (
            f"<p class='compound-note'><strong>Compound:</strong> Parallel API "
            f"{_esc(prior_parallel)} → {_esc(parallel)} "
            f"(−{_esc(prior_parallel - parallel)} vs last run on this shelf).</p>"
        )
    if hits:
        compound = f"""
<section class="compound">
  <p class="compound-label">Compounding — this run</p>
  <div class="nums">
    <div><span class="n">{_esc(parallel)}</span><span class="k">Parallel API</span></div>
    <div><span class="n hit">{_esc(hits)}</span><span class="k">Corpus hits</span></div>
    <div><span class="n">{_esc(remembered)}</span><span class="k">On this shelf</span></div>
  </div>
  {delta_note}
  <p class="compound-note">{_esc(hits)} claim(s) resolved from memory — search not re-spent.
  Paste another script with subject <strong>{subject}</strong> to compound further.</p>
</section>"""
    else:
        compound = f"""
<section class="compound cold">
  <p class="compound-label">First pass on this shelf</p>
  <div class="nums">
    <div><span class="n">{_esc(parallel)}</span><span class="k">Parallel API</span></div>
    <div><span class="n">{_esc(remembered)}</span><span class="k">Now remembered</span></div>
  </div>
  <p class="compound-note">Nothing reused yet. Clear a <em>second</em> script with the same
  subject tag to see the fraction drop.</p>
</section>"""

    action = [r for r in rows if r.get("label") != "SOURCED"]
    action_html = ""
    if action:
        items = []
        for r in action:
            items.append(
                f"<li><strong>{_esc(r.get('claim_id'))}</strong> "
                f"<span class='stamp'>{_esc(r.get('label'))}</span>"
                f"<p class='claim'>{_esc(r.get('text'))}</p>"
                f"<p class='why'>{_esc(r.get('why'))}</p></li>"
            )
        action_html = (
            "<section class='action'><h2>Claims requiring action</h2>"
            f"<ul>{''.join(items)}</ul></section>"
        )
    else:
        action_html = (
            "<section class='action'><h2>Claims requiring action</h2>"
            "<p class='why'>None on this pass. Unusual for real narration — "
            "confirm the input was not a plumbing fixture.</p></section>"
        )

    sourced_rows = [r for r in rows if r.get("label") == "SOURCED"]
    sourced_html_parts = []
    for r in sourced_rows:
        hit = ""
        if r.get("corpus_hit"):
            hit = "<p class='reuse'>Resolved from corpus — no Parallel call.</p>"
            if r.get("reused_from"):
                hit += (
                    f"<p class='warn'>Reused evidence was gathered for different wording: "
                    f"“{_esc(r.get('reused_from')[:160])}”. Same distinctive term — "
                    f"a human should confirm it is the same assertion.</p>"
                )
        quote = _esc((r.get("quoted_terms") or "")[:280])
        note = r.get("source_note")
        note_h = f"<p class='why'>{_esc(note)}</p>" if note else ""
        sourced_html_parts.append(
            f"<article><h3>{_esc(r.get('claim_id'))} — SOURCED</h3>"
            f"<p class='claim'>{_esc(r.get('text'))}</p>{hit}"
            f"<p class='cite'><a href='{_esc(r.get('citation_url'))}'>"
            f"{_esc(r.get('citation_url'))}</a></p>"
            f"<blockquote>“{quote}”</blockquote>{note_h}</article>"
        )
    sourced_block = (
        "<section class='sourced'><h2>Sourced</h2>"
        + ("".join(sourced_html_parts) or "<p class='why'>None.</p>")
        + "</section>"
    )

    return f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Gap report — {subject}</title>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Newsreader:opsz,wght@6..72,400;6..72,600&display=swap" rel="stylesheet">
<style>
:root{{--paper:#e9ecef;--ink:#14161c;--mute:#5c6370;--line:#c5cad3;--stamp:#b42318;--band:#dfe3e8}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--paper);color:var(--ink);
  font-family:"Newsreader",Georgia,serif;font-size:18px;line-height:1.45}}
.wrap{{max-width:52rem;margin:0 auto;padding:2rem 1.25rem 4rem}}
a{{color:var(--ink)}}
.back{{font-family:"IBM Plex Mono",monospace;font-size:.72rem;letter-spacing:.06em;
  text-transform:uppercase;color:var(--mute);text-decoration:none}}
h1{{font-size:clamp(1.8rem,4vw,2.6rem);margin:.8rem 0 .3rem;letter-spacing:-.02em}}
.meta{{font-family:"IBM Plex Mono",monospace;font-size:.78rem;color:var(--mute);margin:0 0 1.5rem}}
.tally{{display:grid;grid-template-columns:repeat(4,1fr);gap:1px;background:var(--line);
  border:1px solid var(--line);margin:0 0 1.5rem}}
.tally div{{background:var(--paper);padding:.85rem .7rem}}
.tally .n{{display:block;font-family:"IBM Plex Mono",monospace;font-size:1.6rem;font-weight:600}}
.tally .k{{font-family:"IBM Plex Mono",monospace;font-size:.65rem;letter-spacing:.06em;
  text-transform:uppercase;color:var(--mute)}}
.compound{{background:var(--band);padding:1.1rem 1rem;margin:0 0 1.75rem;border-left:4px solid var(--ink)}}
.compound.cold{{border-left-color:var(--line)}}
.compound-label{{font-family:"IBM Plex Mono",monospace;font-size:.68rem;letter-spacing:.08em;
  text-transform:uppercase;margin:0 0 .6rem;color:var(--mute)}}
.nums{{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem}}
.nums .n{{display:block;font-family:"IBM Plex Mono",monospace;font-size:2.2rem;font-weight:600;line-height:1}}
.nums .n.hit{{color:var(--ink)}}
.nums .k{{font-family:"IBM Plex Mono",monospace;font-size:.65rem;letter-spacing:.06em;
  text-transform:uppercase;color:var(--mute)}}
.compound-note{{margin:.85rem 0 0;color:var(--mute);font-size:.95rem}}
.buyer{{background:#f4f1ea;padding:1.1rem 1rem;margin:0 0 1.75rem;border-left:4px solid var(--stamp)}}
h2{{font-size:1.15rem;margin:2rem 0 .8rem;border-bottom:1px solid var(--ink);padding-bottom:.3rem}}
ul{{list-style:none;padding:0;margin:0}}
li{{padding:1rem 0;border-bottom:1px solid var(--line)}}
.stamp{{font-family:"IBM Plex Mono",monospace;font-size:.7rem;letter-spacing:.05em;
  color:var(--stamp);margin-left:.4rem}}
.claim{{margin:.35rem 0;font-size:1.05rem}}
.why{{color:var(--mute);font-size:.95rem;margin:.25rem 0 0}}
.reuse{{font-family:"IBM Plex Mono",monospace;font-size:.75rem;margin:.4rem 0}}
.warn{{color:var(--stamp);font-size:.9rem}}
.cite{{font-family:"IBM Plex Mono",monospace;font-size:.72rem;word-break:break-all}}
blockquote{{margin:.5rem 0;padding-left:.8rem;border-left:2px solid var(--line);color:var(--mute);
  font-size:.95rem}}
article{{padding:1rem 0;border-bottom:1px solid var(--line)}}
.next{{margin:2.5rem 0 0;padding-top:1rem;border-top:1px solid var(--ink)}}
.next a.button{{display:inline-block;font-family:"IBM Plex Mono",monospace;font-size:.75rem;
  letter-spacing:.04em;text-transform:uppercase;background:var(--ink);color:var(--paper);
  text-decoration:none;padding:.75rem 1.2rem;margin-top:.5rem}}
@media(max-width:640px){{.tally,.nums{{grid-template-columns:1fr 1fr}}}}
</style></head><body>
<div class="wrap">
  <a class="back" href="/?subject={subject}">← desk</a>
  <h1>Gap report</h1>
  <p class="meta">subject {subject} · clearance memo</p>
  <div class="tally">
    <div><span class="n">{_esc(n)}</span><span class="k">Claims</span></div>
    <div><span class="n">{_esc(sourced)}</span><span class="k">Sourced</span></div>
    <div><span class="n">{_esc(unsourced)}</span><span class="k">Unsourced</span></div>
    <div><span class="n">{_esc(parallel)}</span><span class="k">Parallel</span></div>
  </div>
  {buyer}
  {compound}
  {action_html}
  {sourced_block}
  <section class="next">
    <p class="compound-note">Second production on the same shelf is the product.
    Paste the next narration with subject <strong>{subject}</strong>.</p>
    <a class="button" href="/?subject={subject}">Clear another script on {subject}</a>
  </section>
</div>
</body></html>"""


def _popular_page(limit: int = 15) -> str:
    data = query_analytics.report(db=_log_db(), limit=limit)
    notes = data.get("traffic_notes") or {}
    note_html = "".join(f"<li>{_esc(n)}</li>" for n in (notes.get("notes") or []))
    by_t = notes.get("by_traffic") or {}
    traffic_meta = (
        f"asks={notes.get('total_asks', 0)} · "
        f"human={by_t.get('human', 0)} gate={by_t.get('gate', 0)} "
        f"demo={by_t.get('demo', 0)} fleet={by_t.get('fleet', 0)} "
        f"unknown={by_t.get('unknown', 0)}"
        + (" · <strong>POLLUTED</strong>" if notes.get("polluted") else "")
    )
    human_rows = []
    for r in (data.get("popular_human") or [])[:limit]:
        human_rows.append(
            f"<tr><td>{_esc(r['asks'])}</td>"
            f"<td>{_esc(r.get('example', '')[:80])}</td>"
            f"<td>{_esc(r.get('sourced', 0))}</td>"
            f"<td>{_esc(r.get('not_cleared', 0))}</td>"
            f"<td>{_esc(r.get('live_asks') or 0)}</td></tr>"
        )
    rows = []
    for r in data.get("popular_queries", [])[:limit]:
        rows.append(
            f"<tr><td>{_esc(r['asks'])}</td>"
            f"<td>{_esc(r.get('example', '')[:80])}</td>"
            f"<td>{_esc(r.get('sourced', 0))}</td>"
            f"<td>{_esc(r.get('not_cleared', 0))}</td>"
            f"<td>{_esc(r.get('live_asks') or 0)}</td></tr>"
        )
    targets = []
    for r in data.get("optimization_targets", [])[:8]:
        targets.append(
            f"<li><strong>{_esc(r.get('example', '')[:70])}</strong> "
            f"({ _esc(r.get('asks'))} asks) — {_esc(r.get('action', ''))}</li>"
        )
    aliases = []
    for r in data.get("alias_candidates", [])[:6]:
        aliases.append(
            f"<li><code>{_esc(r['alias'])}</code> → "
            f"<code>{_esc(r['canonical'][:60])}</code></li>"
        )
    return f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Popular queries · Agent Science</title>
<style>
body{{font-family:Georgia,serif;background:#e8e6e1;color:#16181d;margin:0;padding:2rem}}
.wrap{{max-width:52rem;margin:0 auto}}
h1{{font-size:1.6rem;margin:0 0 .5rem}}
p.meta{{color:#61656e;font-size:.95rem}}
a{{color:inherit}}
table{{width:100%;border-collapse:collapse;margin:1.5rem 0;font-size:.9rem}}
th,td{{text-align:left;padding:.5rem;border-bottom:1px solid #c9c5bd}}
th{{font-family:monospace;font-size:.7rem;text-transform:uppercase;letter-spacing:.08em}}
h2{{font-size:1rem;margin:2rem 0 .5rem}}
ul{{padding-left:1.2rem}}
code{{font-size:.85rem}}
.notes{{background:#f3f1ec;padding:.75rem 1rem;border-left:3px solid #B42318}}
</style></head><body><div class="wrap">
<p><a href="/">← desk</a> · <a href="/registry">registry</a></p>
<h1>Popular queries</h1>
<p class="meta">Truth dictionary analytics — human vs gate/demo split.
JSON: <a href="/popular">/popular</a> · {traffic_meta}</p>
<div class="notes"><strong>Traffic notes</strong><ul>{note_html or '<li>No pollution notes.</li>'}</ul></div>
<h2>Human view (gate/demo excluded)</h2>
<table>
<tr><th>Asks</th><th>Query</th><th>Sourced</th><th>Miss</th><th>Live</th></tr>
{''.join(human_rows) or '<tr><td colspan="5">No human/unknown asks yet.</td></tr>'}
</table>
<h2>All asks (includes gate + film demo)</h2>
<table>
<tr><th>Asks</th><th>Query</th><th>Sourced</th><th>Miss</th><th>Live</th></tr>
{''.join(rows) or '<tr><td colspan="5">No queries logged yet — use science_lookup.</td></tr>'}
</table>
<h2>Optimize next (human view)</h2>
<ul>{''.join(targets) or '<li>Nothing flagged yet.</li>'}</ul>
<h2>Alias candidates</h2>
<ul>{''.join(aliases) or '<li>Add phrasings to truth-dictionary/aliases.json</li>'}</ul>
</div></body></html>"""


def _truths_page(limit: int = 15) -> str:
    """Popular truths dashboard — ranked queries + field signals strip."""
    data = query_analytics.report(db=_log_db(), limit=limit)
    st = stack_search.stats(db=_log_db())
    signals_path = Path(__file__).resolve().parents[1] / "truth-dictionary" / "field-signals.json"
    field_rows = []
    hn_note = ""
    if signals_path.exists():
        try:
            sig = json.loads(signals_path.read_text(encoding="utf-8"))
            for g in (sig.get("github") or [])[:6]:
                field_rows.append(
                    f"<tr><td>★ {g.get('stars', 0)}</td>"
                    f"<td>{_esc(g.get('repo', ''))}</td>"
                    f"<td>{_esc(g.get('why', ''))}</td></tr>"
                )
            hn = sig.get("hacker_news") or {}
            hn_note = f"HN source: {_esc(hn.get('source', 'unknown'))} · read {_esc(hn.get('read_at', '—'))}"
        except json.JSONDecodeError:
            pass
    pop_rows = []
    for r in data.get("popular_queries", [])[:limit]:
        pop_rows.append(
            f"<tr><td>{_esc(r['asks'])}</td>"
            f"<td>{_esc(r.get('example', '')[:80])}</td>"
            f"<td>{_esc(r.get('sourced', 0))}</td>"
            f"<td>{_esc(r.get('not_cleared', 0))}</td></tr>"
        )
    hit = st.get("dictionary_hit_rate", 0)
    return f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Truths · Agent Science</title>
<style>
body{{font-family:Georgia,serif;background:#e8e6e1;color:#16181d;margin:0;padding:2rem}}
.wrap{{max-width:56rem;margin:0 auto}}
h1{{font-size:1.6rem;margin:0 0 .5rem}}
p.meta{{color:#61656e;font-size:.95rem}}
a{{color:inherit}}
table{{width:100%;border-collapse:collapse;margin:1.5rem 0;font-size:.9rem}}
th,td{{text-align:left;padding:.5rem;border-bottom:1px solid #c9c5bd}}
th{{font-family:monospace;font-size:.7rem;text-transform:uppercase;letter-spacing:.08em}}
.strip{{background:#fff;padding:1rem;border:1px solid #c9c5bd;margin:1rem 0}}
</style></head><body><div class="wrap">
<p><a href="/">← desk</a> · <a href="/popular/ui">popular</a> · <a href="/registry">registry</a></p>
<h1>Truths dashboard</h1>
<p class="meta">Most websearched claims · field adoption strip · hit rate at object</p>
<div class="strip">
  <strong>Shelf:</strong> {st.get('n', 0)} claims · hit rate {hit} · {st.get('queries_logged', 0)} queries logged
</div>
<h2>Top queries (ranked by asks)</h2>
<table>
<tr><th>Asks</th><th>Query</th><th>Sourced</th><th>Miss</th></tr>
{''.join(pop_rows) or '<tr><td colspan="4">No queries yet.</td></tr>'}
</table>
<h2>Field signals (GitHub ★)</h2>
<table>
<tr><th>★</th><th>Repo</th><th>Why</th></tr>
{''.join(field_rows) or '<tr><td colspan="3">Run refresh_field_signals.py</td></tr>'}
</table>
<p class="meta">{hn_note}</p>
</div></body></html>"""


def _visibility_panel(query: str, *, live: bool = False, full: bool = True) -> dict:
    from clearance import visibility
    return visibility.panel(query, live=live, full=full, personal=False)


def _visibility_page(query: str, *, live: bool = False, full: bool = True) -> str:
    """Full websearch visibility — truth layer HTML for judges."""
    from clearance import visibility
    q = query.strip() or "ralph loop agentic"
    data = _visibility_panel(q, live=live, full=full)
    return visibility.render_html(data, query=q)


def _run_clearance(script: str, subject: str, model: str) -> dict:
    """Clear through the ADK agent, and say so in the report.

    A fallback that quietly serves the direct pipeline would let the submission
    claim Agent Builder on a path that had stopped using it. So the fallback keeps
    running (a judge still gets a clearance) but stamps `engine: "direct"` and
    carries the ADK failure in `adk_error`. The claim and the evidence move together.
    """
    if ADK_DEFAULT and adk_agent.adk_available():
        try:
            return adk_agent.run_clearance(script, subject=subject)
        except Exception as e:
            out = agent_science.clear_script(script, subject=subject, model=model)
            out["engine"] = "direct"
            out["adk_error"] = f"{type(e).__name__}: {e}"
            return out
    out = agent_science.clear_script(script, subject=subject, model=model)
    out["engine"] = "direct"
    if ADK_DEFAULT:
        out["adk_error"] = "google-adk not importable in this image"
    return out


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _send(self, code: int, body: bytes, content_type: str):
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _json(self, code: int, payload):
        self._send(code, json.dumps(payload, indent=1).encode(), "application/json")

    def _read_json(self):
        n = int(self.headers.get("Content-Length") or 0)
        if not n:
            return {}
        try:
            return json.loads(self.rfile.read(n))
        except json.JSONDecodeError:
            return None

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        qs = parse_qs(parsed.query)

        if path in ("/", "/index.html"):
            subj = (qs.get("subject") or [""])[0].strip() or "orphan-works"
            return self._send(200, _desk_page(subj).encode(), "text/html; charset=utf-8")

        # THE FRONT SURFACE. Served at /front rather than replacing "/": the desk at
        # "/" is the live clearance runner and is what the hosted demo and the partner
        # runtime already point at. Silently swapping what a shipped URL returns is the
        # substitution defect wearing a routing table. The desk links here instead.
        if path in ("/front", "/front/"):
            page = ask_registry.render_front(db=_log_db(), registry_href="/registry")
            return self._send(200, page.encode(), "text/html; charset=utf-8")

        if path in ("/refusal", "/refusal/"):
            term = (qs.get("term") or [""])[0]
            page = ask_registry.render_refusal(term=term, db=_log_db(), home="/front")
            return self._send(200, page.encode(), "text/html; charset=utf-8")

        if path in ("/registry", "/registry/"):
            q = (qs.get("q") or [""])[0]
            page = ask_registry.render_page(q=q.strip(), db=_log_db())
            return self._send(200, page.encode(), "text/html; charset=utf-8")

        if path == "/registry/api":
            q = (qs.get("q") or [""])[0]
            return self._json(200, ask_registry.ask(q, db=_log_db()))

        if path == "/search":
            q = (qs.get("q") or [""])[0]
            live = (qs.get("live") or ["true"])[0].lower() not in ("0", "false", "no")
            subj = (qs.get("subject") or ["stack"])[0]
            traffic = (qs.get("traffic") or [None])[0]
            return self._json(200, stack_search.search(
                q, live=live, subject=subj, db=_log_db(), traffic=traffic
            ))

        if path == "/stats":
            return self._json(200, stack_search.stats(db=_log_db()))

        if path == "/popular":
            limit = int((qs.get("limit") or ["15"])[0])
            return self._json(200, query_analytics.report(db=_log_db(), limit=limit))

        if path in ("/popular/ui", "/popular/ui/"):
            limit = int((qs.get("limit") or ["15"])[0])
            return self._send(200, _popular_page(limit).encode(), "text/html; charset=utf-8")

        if path in ("/truths/ui", "/truths/ui/"):
            limit = int((qs.get("limit") or ["15"])[0])
            return self._send(200, _truths_page(limit).encode(), "text/html; charset=utf-8")

        if path == "/visibility":
            q = (qs.get("q") or ["ralph loop agentic"])[0]
            live = (qs.get("live") or ["false"])[0].lower() in ("1", "true", "yes")
            full = (qs.get("full") or ["true"])[0].lower() not in ("0", "false", "no")
            return self._json(200, _visibility_panel(q, live=live, full=full))

        if path in ("/visibility/ui", "/visibility/ui/"):
            q = (qs.get("q") or ["ralph loop agentic"])[0]
            live = (qs.get("live") or ["false"])[0].lower() in ("1", "true", "yes")
            full = (qs.get("full") or ["true"])[0].lower() not in ("0", "false", "no")
            return self._send(200, _visibility_page(q, live=live, full=full).encode(),
                              "text/html; charset=utf-8")

        if path == "/health":
            gemini_path = "none"
            if os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"):
                gemini_path = "api-key"
            else:
                proj = (
                    os.environ.get("GCP_PROJECT")
                    or os.environ.get("GOOGLE_CLOUD_PROJECT")
                    or (os.environ.get("K_SERVICE") and "adc")
                )
                if proj:
                    gemini_path = f"vertex:{proj}"
                else:
                    try:
                        from clearance import gemini as _g
                        p = _g.vertex_project()
                        if p and _g.vertex_token():
                            gemini_path = f"vertex:{p}"
                    except Exception:
                        pass
            adk_ok = adk_agent.adk_available()
            adk_default = ADK_DEFAULT and adk_ok
            from clearance import search as _parallel
            return self._json(200, {
                "ok": True,
                "service": "agent-science",
                "gemini": gemini_path != "none",
                "gemini_path": gemini_path,
                "parallel": bool(os.environ.get("PARALLEL_API_KEY")),
                "parallel_sdk": _parallel.sdk_available(),
                "parallel_sdk_version": _parallel.sdk_version(),
                "parallel_transport": _parallel.integration_info()["transport"],
                "last_parallel_search_id": _parallel.last_search_id(),
                "agent_builder": adk_ok,
                "adk_version": adk_agent.adk_version(),
                "engine_default": "adk" if adk_default else "direct",
            })

        if path == "/partners":
            gemini_path = "none"
            if os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"):
                gemini_path = "api-key"
            else:
                proj = os.environ.get("GCP_PROJECT") or os.environ.get("GOOGLE_CLOUD_PROJECT")
                if proj:
                    gemini_path = f"vertex:{proj}"
            adk_ok = adk_agent.adk_available()
            return self._json(200, partner_manifest.manifest(
                gemini_path=gemini_path,
                adk_default=ADK_DEFAULT and adk_ok,
            ))

        if path == "/corpus":
            subject = (qs.get("subject") or ["default"])[0].strip() or "default"
            use = agent_science._use(subject)
            con = corpus.connect()
            return self._json(200, {
                "subject": subject,
                "use": use,
                "remembered": corpus.size_for_use(con, use),
                "total": corpus.size(con),
            })

        self._json(404, {"error": f"no route {path}"})

    def do_POST(self):
        if self.path == "/search":
            body = self._read_json()
            if body is None:
                return self._json(400, {"error": "body is not valid JSON"})
            q = (body.get("query") or "").strip()
            if not q:
                return self._json(400, {"error": "field 'query' is required"})
            live = body.get("live", True)
            subject = (body.get("subject") or "stack").strip()
            traffic = body.get("traffic")
            return self._json(200, stack_search.search(
                q, live=live, subject=subject, db=_log_db(), traffic=traffic
            ))

        if self.path == "/ingest":
            body = self._read_json()
            if body is None:
                return self._json(400, {"error": "body is not valid JSON"})
            prod = (body.get("production") or "ingest").strip()
            try:
                if body.get("claim") and body.get("url"):
                    res = stack_ingest.ingest_claim(body["claim"], body["url"], production=prod)
                elif body.get("text"):
                    res = stack_ingest.ingest_text(body["text"], production=prod)
                else:
                    return self._json(400, {"error": "pass text or claim+url"})
            except ValueError as e:
                return self._json(400, {"error": str(e)})
            return self._json(200, res)

        if self.path == "/clear":
            ct = self.headers.get("Content-Type", "")
            if "application/json" in ct:
                body = self._read_json()
                if body is None:
                    return self._json(400, {"error": "body is not valid JSON"})
                script = (body.get("script") or "").strip()
                subject = (body.get("subject") or "default").strip()
            else:
                n = int(self.headers.get("Content-Length") or 0)
                raw = self.rfile.read(n).decode("utf-8", errors="replace")
                parts = {}
                for pair in raw.split("&"):
                    if "=" in pair:
                        k, v = pair.split("=", 1)
                        from urllib.parse import unquote_plus
                        parts[k] = unquote_plus(v.replace("+", " "))
                script = (parts.get("script") or "").strip()
                subject = (parts.get("subject") or "default").strip()
            if not script:
                return self._json(400, {"error": "field 'script' is required"})
            model = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash-lite")
            try:
                out = _run_clearance(script, subject, model)
            except RuntimeError as e:
                return self._json(503, {"error": str(e)})
            code = 200 if out.get("ok") else 422
            if "application/json" not in ct and out.get("ok"):
                return self._send(200, _report_html(out).encode(), "text/html; charset=utf-8")
            return self._json(code, out)
        self._json(404, {"error": f"no route {self.path}"})

    def log_message(self, fmt, *a):
        sys.stderr.write("%s %s\n" % (self.address_string(), fmt % a))


def main():
    port = int(os.environ.get("PORT", 8080))
    sys.stderr.write(f"agent-science compounding desk on :{port}\n")
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()


if __name__ == "__main__":
    main()
