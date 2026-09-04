"""Websearch visibility — full agentic-truth panel, not one answer.

Agent Science websearch is the truth layer for believe+use. Full rundown:
docs/WEBSEARCH-FULL-RUNDOWN.md
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from clearance import query_analytics, stack_search

_ROOT = Path(__file__).resolve().parent.parent
_SIGNALS = _ROOT / "truth-dictionary" / "field-signals.json"
_ALIASES = _ROOT / "truth-dictionary" / "aliases.json"
_PRACTICES = _ROOT / "docs" / "inspiration" / "PRACTICES-CORPUS.md"


def _tokens(q: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9]{3,}", q.lower()) if t} - {"the", "and", "for", "with", "best", "practice", "practices", "what", "how", "does", "should"}


def _alias_hits(query: str) -> list[dict]:
    if not _ALIASES.exists():
        return []
    try:
        aliases = json.loads(_ALIASES.read_text())
    except json.JSONDecodeError:
        return []
    q = query.strip().lower()
    toks = _tokens(query)
    out = []
    for alias, canonical in aliases.items():
        a = alias.lower()
        if a == q or a in q or q in a or (toks & _tokens(alias)):
            out.append({"alias": alias, "canonical": canonical})
    return out[:8]


def _field_hits(query: str, *, full: bool = False) -> dict:
    if not _SIGNALS.exists():
        return {"github": [], "blogs_and_docs": [], "read_at": None}
    try:
        data = json.loads(_SIGNALS.read_text())
    except json.JSONDecodeError:
        return {"github": [], "blogs_and_docs": [], "read_at": None}
    toks = _tokens(query)
    gh, blogs = [], []
    for row in data.get("github") or []:
        blob = f"{row.get('repo', '')} {row.get('why', '')}".lower()
        if toks & set(re.findall(r"[a-z0-9]{3,}", blob)):
            gh.append(row)
    for row in data.get("blogs_and_docs") or []:
        blob = f"{row.get('title', '')} {row.get('kind', '')}".lower()
        if toks & set(re.findall(r"[a-z0-9]{3,}", blob)):
            blogs.append(row)
    gh = sorted(gh, key=lambda r: r.get("stars") or 0, reverse=True)
    n = 99 if full else 5
    return {
        "github": gh[:n],
        "blogs_and_docs": blogs[:n],
        "read_at": data.get("read_at"),
        "note": "stars = adoption signal, not a verdict",
    }


def _practices_hits(query: str, *, full: bool = False) -> list[dict]:
    if not _PRACTICES.exists():
        return []
    toks = _tokens(query)
    hits: list[dict] = []

    def _rows() -> list[dict]:
        out = []
        in_practitioner_table = False
        for line in _PRACTICES.read_text(encoding="utf-8").splitlines():
            if line.startswith("|") and "Practitioner" in line and "Source" in line:
                in_practitioner_table = True
                continue
            if line.startswith("#"):
                in_practitioner_table = False
            if not in_practitioner_table or not line.startswith("|") or line.startswith("|---"):
                continue
            parts = [p.strip() for p in line.strip("|").split("|")]
            if len(parts) >= 3:
                out.append({"who": parts[0], "practice": parts[1], "source": parts[2]})
        return out

    all_rows = _rows()
    for row in all_rows:
        blob = f"{row['who']} {row['practice']} {row['source']}".lower()
        if toks & set(re.findall(r"[a-z0-9]{3,}", blob)):
            hits.append(row)
    return hits[: (20 if full else 6)]


def _peer_queries(query: str, *, limit: int = 8) -> list[dict]:
    toks = _tokens(query)
    peers = []
    for row in query_analytics.popular_queries(limit=50):
        ex = (row.get("example") or row.get("qnorm") or "")
        if toks & _tokens(ex):
            peers.append(row)
    return peers[:limit]


def _lookup_angles(query: str, primary: dict, aliases: list[dict], *, live: bool) -> list[dict]:
    """Query variants and tier routes attempted for this visibility ask."""
    return [
        {**event, "variant": event.get("query", query), "tier": event.get("tier", "—"),
         "hit": event.get("outcome", "unknown")}
        for event in primary.get("trace", [])
    ]


def _compute_transparency(
    query: str,
    primary: dict,
    aliases: list[dict],
    field: dict,
    practices: list[dict],
    peer_queries: list[dict],
    *,
    live: bool,
) -> dict[str, Any]:
    """Transparency panes: angles searched, shallow route, imbalance."""
    gh = field.get("github") or []
    blogs = field.get("blogs_and_docs") or []
    has_field = bool(gh or blogs)
    has_practices = bool(practices)
    has_peers = bool(peer_queries)
    tier = primary.get("cost_tier") or "?"

    # Unverified links and peer queries cannot prove research depth.
    shallow = True  # Single-answer lookup does not establish multi-source breadth.


    buckets = {
        "github": len(gh),
        "blogs_docs": len(blogs),
        "practices": len(practices),
        "peers": len(peer_queries),
        "primary": 1 if primary.get("label") else 0,
    }
    nonzero = {k: v for k, v in buckets.items() if v > 0}
    total = sum(nonzero.values())
    imbalance: dict | None = None
    if total >= 3:
        dominant = max(nonzero, key=nonzero.get)
        share = nonzero[dominant] / total
        if share >= 0.65:
            notes = {
                "github": "only adoption signals — no verify path or practitioner depth",
                "blogs_docs": "only blogs/docs — no GitHub use signals or peer asks",
                "practices": "only practitioner corpus — no field ★ or peer depth",
                "peers": "only fleet peer asks — thin field belief/use context",
                "primary": "only dictionary primary — no field or peer panes matched",
            }
            imbalance = {
                "dominant": dominant,
                "share": round(share, 2),
                "counts": nonzero,
                "note": notes.get(dominant, "one source type dominates"),
            }
    if has_field and not has_practices and tier == "free":
        if imbalance is None:
            imbalance = {
                "dominant": "github",
                "share": round(len(gh) / max(total, 1), 2),
                "counts": nonzero,
                "note": "dictionary hit with stars only — no practitioner verify path",
            }

    return {
        "angles_searched": _lookup_angles(query, primary, aliases, live=live),
        "shallow_route": shallow,
        "imbalance": imbalance,
    }


def panel(
    query: str,
    *,
    live: bool = False,
    subject: str = "stack",
    full: bool = False,
    personal: bool = True,
    root: Path | str | None = None,
    refresh: bool = False,
) -> dict[str, Any]:
    """Visibility panel — full=True for complete agentic-truth rundown.

    When personal=True (default), indexes the ask into ~/.agent-science/truth.db.
    """
    from clearance import personal_truth

    local = personal_truth.lookup_local(query) if personal else None
    primary = stack_search.lookup(query, live=live, subject=subject, refresh=refresh)
    out: dict[str, Any] = {
        "query": query,
        "mode": "full" if full else "standard",
        "primary": primary,
        "personal_prior": (
            {
                "label": local.get("result_label"),
                "asked_at": local.get("asked_at"),
                "citation_url": local.get("citation_url"),
                "cause": local.get("cause"),
            }
            if local
            else None
        ),
        "aliases": _alias_hits(query),
        "field": _field_hits(query, full=full),
        "agentic_practices": _practices_hits(query, full=full),
        "peer_queries": _peer_queries(query, limit=15 if full else 8),
        "optimization": [
            r
            for r in query_analytics.optimization_targets(limit=20)
            if _tokens(query) & _tokens(r.get("example") or "")
        ][: (10 if full else 5)],
        "parallel_probes": [
            r
            for r in query_analytics.parallel_probes(limit=30)
            if _tokens(query) & _tokens(r.get("probe") or "")
        ][: (10 if full else 5)],
        "discipline": (
            "Agent Science websearch = truth layer for believe+use. "
            "Primary is one pane; ★/blogs/practices/peers are visibility. "
            "Personal DB indexes your asks. Stars never author SOURCED. "
            "Full rundown: docs/WEBSEARCH-FULL-RUNDOWN.md"
        ),
    }
    out["transparency"] = _compute_transparency(
        query,
        primary,
        out["aliases"],
        out["field"],
        out["agentic_practices"],
        out["peer_queries"],
        live=live,
    )
    if full:
        from clearance import stack_fit
        out["stack_fit"] = stack_fit.score(query, root=root) if root else {"fit": "unassessed", "improvement": "Attach your repo locally to capture context and run an experiment.", "stack": {}}
        out["shelf_stats"] = stack_search.stats()
        out["popular_bundle"] = {
            "top_reused": query_analytics.top_terms(limit=8),
            "alias_candidates": query_analytics.alias_candidates(limit=8),
        }
        if personal:
            out["personal_stats"] = personal_truth.stats()
    if personal:
        slim = {
            "mode": out.get("mode"),
            "aliases": out.get("aliases"),
            "field_github": [g.get("repo") for g in (out.get("field") or {}).get("github") or []],
            "practices": [h.get("who") for h in out.get("agentic_practices") or []],
        }
        ask_id = personal_truth.record_ask(
            query, primary, panel=slim, source="visibility"
        )
        out["personal_ask_id"] = ask_id
    return out


def format_panel(data: dict) -> str:
    p = data.get("primary") or {}
    mode = data.get("mode") or "standard"
    lines = [
        f"# Agent Science websearch · {mode} visibility",
        f"# Query · {data.get('query')}",
        "",
        "## 0 · Personal prior (your truth DB)",
    ]
    prior = data.get("personal_prior")
    if prior:
        lines.append(
            f"  earlier={prior.get('label')}  at={prior.get('asked_at')}  "
            f"url={prior.get('citation_url') or prior.get('cause') or '—'}"
        )
    else:
        lines.append("  (first ask on this machine — will index into ~/.agent-science/truth.db)")
    if data.get("personal_ask_id"):
        lines.append(f"  indexed_ask_id={data['personal_ask_id']}")

    lines += [
        "",
        "## 1 · Primary (dictionary — verify or refuse)",
        f"  label={p.get('label') or p.get('result_label')}  "
        f"tier={p.get('cost_tier')}  "
        f"parallel={p.get('parallel_api_calls', 0)}",
    ]
    if p.get("citation_url"):
        lines.append(f"  url={p['citation_url']}")
    if p.get("quoted_terms"):
        qt = str(p["quoted_terms"]).replace("\n", " ")[:220]
        lines.append(f"  span={qt}")
    if p.get("cause"):
        lines.append(f"  cause={p['cause']}")
    if p.get("resolves_with"):
        lines.append(f"  resolves_with={p['resolves_with']}")

    trans = data.get("transparency") or {}
    lines += ["", "## 1b · Transparency (what was searched)"]
    if trans.get("shallow_route"):
        lines.append("  SHALLOW_ROUTE=yes — dictionary/cheap only; no field or peer depth")
    else:
        lines.append("  SHALLOW_ROUTE=no — field, practices, or peers present")
    for a in trans.get("angles_searched") or []:
        bits = [f"variant={a.get('variant', '')[:60]}", f"route={a.get('route')}", f"tier={a.get('tier')}"]
        if a.get("hit"):
            bits.append(f"hit={a['hit']}")
        if a.get("reason"):
            bits.append(f"reason={a['reason']}")
        lines.append("  " + "  ".join(bits))
    imb = trans.get("imbalance")
    if imb:
        lines.append(
            f"  IMBALANCE: {imb.get('dominant')} dominates ({imb.get('share')}) — {imb.get('note')}"
        )
    else:
        lines.append("  IMBALANCE: none — source mix balanced")

    if data.get("stack_fit"):
        sf = data["stack_fit"]
        lines += [
            "",
            "## 1c · Stack-fit (magnet eval)",
            f"  fit={sf.get('fit')}  stack={','.join((sf.get('stack') or {}).get('stack') or [])}",
            f"  improvement: {sf.get('improvement')}",
        ]
        for r in sf.get("reasons") or []:
            lines.append(f"  reason: {r}")

    lines += ["", "## 2 · Aliases (other phrasings → canonical)"]
    for a in data.get("aliases") or []:
        lines.append(f"  {a['alias']} → {str(a['canonical'])[:90]}")
    if not data.get("aliases"):
        lines.append("  (none)")

    field = data.get("field") or {}
    lines += [
        "",
        f"## 3 · Field use — GitHub ★ (adoption · read {field.get('read_at')})",
    ]
    lines.append(f"  note: {field.get('note')}")
    for g in field.get("github") or []:
        lines.append(f"  {g.get('stars'):>7} ★  {g.get('repo')}  — {g.get('why')}")
        lines.append(f"           {g.get('url')}")

    lines += ["", "## 4 · Field belief — blogs / official docs"]
    for b in field.get("blogs_and_docs") or []:
        lines.append(f"  [{b.get('kind')}] {b.get('title')}")
        lines.append(f"           {b.get('url')}")

    lines += [
        "",
        "## 5 · Agentic practices (Grinder corpus — named engineer truths)",
    ]
    for h in data.get("agentic_practices") or []:
        lines.append(f"  {h.get('who')}: {h.get('practice')[:120]}")
        lines.append(f"           source: {h.get('source')}")
    if not data.get("agentic_practices"):
        lines.append(
            "  (no corpus line matched — see docs/inspiration/PRACTICES-CORPUS.md)"
        )

    lines += ["", "## 6 · Peer queries (fleet already asked)"]
    for r in data.get("peer_queries") or []:
        lines.append(
            f"  ×{r.get('asks')}  {r.get('example') or r.get('qnorm')}  "
            f"(sourced={r.get('sourced')} refused={r.get('refused')} "
            f"live={r.get('live_asks')})"
        )
    if not data.get("peer_queries"):
        lines.append("  (none yet)")

    if data.get("parallel_probes"):
        lines += ["", "## 7 · Parallel probes (related discovery)"]
        for r in data["parallel_probes"]:
            lines.append(f"  ×{r.get('asks')}  {r.get('probe')}")

    if data.get("optimization"):
        lines += ["", "## 8 · Optimize next (misses / live spend)"]
        for r in data["optimization"]:
            lines.append(
                f"  ×{r.get('asks')}  {r.get('example')}  → {r.get('action')}"
            )

    if data.get("shelf_stats"):
        s = data["shelf_stats"]
        lines += [
            "",
            "## 9 · Fleet shelf stats",
            f"  claims={s.get('n')} cleared={s.get('cleared')} "
            f"refused={s.get('refused')} queries={s.get('queries_logged')} "
            f"hit_rate={s.get('dictionary_hit_rate')}",
        ]
    if data.get("personal_stats"):
        ps = data["personal_stats"]
        lines += [
            "",
            "## 9b · Personal truth DB",
            f"  db={ps.get('db')}  asks={ps.get('asks')}  "
            f"truths={ps.get('truths')}  skills={ps.get('skills')}  "
            f"fetches={ps.get('fetches')}",
        ]

    if data.get("popular_bundle"):
        lines += ["", "## 10 · Shelf shape (reuse + alias candidates)"]
        for r in (data["popular_bundle"].get("top_reused") or [])[:5]:
            lines.append(
                f"  reused×{r.get('reused')}  {r.get('term')}  [{r.get('verdict')}]"
            )
        for r in (data["popular_bundle"].get("alias_candidates") or [])[:5]:
            lines.append(f"  alias?  {r.get('alias')} → {r.get('canonical')}")

    lines += [
        "",
        "## Discipline",
        f"  {data.get('discipline')}",
        "  Full rundown: docs/WEBSEARCH-FULL-RUNDOWN.md",
    ]
    return "\n".join(lines) + "\n"


def _esc(s: object) -> str:
    import html
    return html.escape("" if s is None else str(s))


def _badge(label: str) -> str:
    lab = (label or "UNKNOWN").upper()
    cls = "badge"
    if "CONTRARY" in lab:
        cls += " contrary"
    elif lab in ("SOURCED", "CLEARED", "GREEN"):
        cls += " sourced"
    elif lab in ("UNSOURCED", "REFUSED", "RED"):
        cls += " refused"
    return f'<span class="{cls}">{_esc(lab)}</span>'


def render_html(data: dict, *, query: str = "") -> str:
    """Judge-facing HTML visibility panel — structured, not monospace dump."""
    q = query or data.get("query") or ""
    p = data.get("primary") or {}
    trans = data.get("transparency") or {}
    label = p.get("label") or p.get("result_label") or "UNKNOWN"
    shallow = trans.get("shallow_route")
    imb = trans.get("imbalance")

    angle_rows = ""
    for a in trans.get("angles_searched") or []:
        hit = f' <span class="hit">{_esc(a.get("hit"))}</span>' if a.get("hit") else ""
        angle_rows += (
            f'<tr><td>{_esc(a.get("variant", "")[:50])}</td>'
            f'<td>{_esc(a.get("route"))}</td><td>{_esc(a.get("tier"))}</td>'
            f'<td>{hit}</td></tr>'
        )

    gh_rows = ""
    for g in (data.get("field") or {}).get("github") or []:
        gh_rows += (
            f'<tr><td>{g.get("stars", 0):,}★</td>'
            f'<td><a href="{_esc(g.get("url"))}">{_esc(g.get("repo"))}</a></td>'
            f'<td>{_esc(g.get("why", ""))}</td></tr>'
        )

    span = (p.get("quoted_terms") or p.get("span") or "")
    if span:
        span = str(span).replace("\n", " ")[:280]

    imb_html = ""
    if imb:
        imb_html = (
            f'<p class="warn">IMBALANCE: <strong>{_esc(imb.get("dominant"))}</strong> '
            f'({imb.get("share")}) — {_esc(imb.get("note"))}</p>'
        )


    shallow_html = (
        '<p class="warn">Limited evidence — a single-answer lookup does not establish multi-source breadth.</p>'
        if shallow
        else '<p class="ok">Live discovery returned a citation. Source breadth still requires review.</p>'
    )

    context_rows = "".join(
        f'<li><a href="{_esc(row.get("url"))}">{_esc(row.get("title"))}</a></li>'
        for row in (data.get("field") or {}).get("blogs_and_docs", [])
    )
    practice_rows = "".join(f'<li>{_esc(row.get("who"))}: {_esc(row.get("practice"))} · {_esc(row.get("source"))}</li>' for row in data.get("agentic_practices", []))
    candidate_rows = "".join(f'<li>{_esc(row.get("established"))}<br><a href="{_esc(row.get("citation_url"))}">{_esc(row.get("citation_url"))}</a></li>' for row in p.get("candidates", [])[:8])
    candidate_html = f'<div class="panel"><h2>Related claims</h2><p>These are different assertions. Their saved verdicts do not answer this question.</p><ul>{candidate_rows}</ul></div>' if candidate_rows else ""
    context_html = f'<div class="panel"><h2>Related sources · context, not verified support</h2><ul>{context_rows or "<li>No related blogs or docs found in the local catalog.</li>"}</ul><ul>{practice_rows or "<li>No related practitioner entries found.</li>"}</ul><p class="meta">Catalog read: {_esc((data.get("field") or {}).get("read_at") or "unknown")}</p></div>'

    return f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Visibility · Agent Science</title>
<style>
:root{{--bg:#e8e6e1;--ink:#16181d;--muted:#61656e;--rule:#c9c5bd;--accent:#B42318;
  --sourced:#1a6b3c;--refused:#8b1a1a;--contrary:#9a3412}}
*{{box-sizing:border-box}}
body{{font-family:Georgia,"Times New Roman",serif;background:var(--bg);color:var(--ink);
  margin:0;padding:1.25rem 1.5rem;line-height:1.5;font-size:1rem}}
.wrap{{max-width:56rem;margin:0 auto}}
nav{{font-family:ui-monospace,monospace;font-size:.8rem;margin-bottom:1rem}}
nav a{{color:inherit;margin-right:.75rem}}
.lead{{font-size:1.05rem;color:var(--muted);margin:.5rem 0 1.25rem;max-width:42rem}}
form{{display:flex;gap:.5rem;margin:1rem 0 1.5rem;flex-wrap:wrap}}
input[type=text]{{flex:1;min-width:14rem;padding:.55rem .65rem;border:1px solid var(--rule);font:inherit}}
button{{font:inherit;padding:.55rem 1rem;background:var(--ink);color:var(--bg);border:0;cursor:pointer}}
.panel{{background:#fff;border:1px solid var(--rule);padding:1rem 1.15rem;margin:0 0 1rem}}
.panel h2{{font-size:1rem;margin:0 0 .65rem;text-transform:uppercase;letter-spacing:.06em;font-weight:600}}
.badge{{display:inline-block;font-family:ui-monospace,monospace;font-size:.75rem;font-weight:600;
  padding:.2rem .55rem;border:1px solid var(--rule);margin-bottom:.5rem}}
.badge.sourced{{border-color:var(--sourced);color:var(--sourced)}}
.badge.refused{{border-color:var(--refused);color:var(--refused)}}
.badge.contrary{{border-color:var(--contrary);color:var(--contrary)}}
.meta{{font-family:ui-monospace,monospace;font-size:.78rem;color:var(--muted)}}
.span{{border-left:3px solid var(--accent);padding-left:.75rem;margin:.75rem 0;font-style:italic}}
table{{width:100%;border-collapse:collapse;font-size:.85rem;font-family:ui-monospace,monospace}}
th,td{{border-bottom:1px solid var(--rule);padding:.35rem .4rem;text-align:left;vertical-align:top}}
th{{color:var(--muted);font-weight:500}}
.hit{{color:var(--contrary);font-weight:600}}
.warn{{color:var(--contrary);font-size:.9rem}}
.ok{{color:var(--sourced);font-size:.9rem}}
.track{{background:var(--ink);color:var(--bg);padding:.85rem 1rem;margin:0 0 1.25rem;font-size:.95rem}}
.track strong{{font-weight:600}}
</style></head><body><div class="wrap">
<nav><a href="/">desk</a><a href="/front">clearance</a><a href="/truths/ui">truths</a><a href="/registry">registry</a></nav>

<div class="track"><strong>What should you believe or use?</strong> Inspect the evidence, see the actual search attempts, and take the question into a repo experiment.</div>

<h1>Websearch visibility</h1>
<p class="lead">Truth layer for what agentic builders believe and use. Not one answer — every angle searched, field signals, and a primary verdict.</p>

<form method="get" action="/visibility/ui">
  <input type="text" name="q" value="{_esc(q)}" placeholder="e.g. ralph loop agentic" required>
  <label><input type="checkbox" name="live" value="true"> Search the web</label>
  <button type="submit">Inspect evidence</button>
</form>

<div class="panel">
  <h2>Primary verdict</h2>
  {_badge(label)}
  <p class="meta">tier={_esc(p.get('cost_tier'))} · parallel={p.get('parallel_api_calls', 0)}</p>
  {f'<p class="meta"><a href="{_esc(p.get("citation_url"))}">{_esc(p.get("citation_url"))}</a></p>' if p.get('citation_url') else ''}
  {f'<div class="span">{_esc(span)}</div>' if span else ''}
  {f'<p class="meta">cause: {_esc(p.get("cause"))}</p>' if p.get('cause') else ''}
</div>

<div class="panel">
  <h2>Transparency · what was searched</h2>
  {shallow_html}
  {imb_html}
  <table><tr><th>variant</th><th>route</th><th>tier</th><th>hit</th></tr>{angle_rows}</table>
</div>

<div class="panel">
  <h2>Field adoption · GitHub ★</h2>
  <p class="meta">stars = adoption signal, not a verdict</p>
  <table><tr><th>★</th><th>repo</th><th>why</th></tr>{gh_rows or '<tr><td colspan="3">no match</td></tr>'}</table>
</div>

{candidate_html}
{context_html}
<p class="meta">JSON: <a href="/visibility?q={_esc(q)}">/visibility</a> · <a href="/partners">partners</a></p>
</div></body></html>"""
