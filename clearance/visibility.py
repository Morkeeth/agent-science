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
    return {t for t in re.findall(r"[a-z0-9]{3,}", q.lower()) if t}


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
        if toks & set(re.findall(r"[a-z0-9]{3,}", blob)) or not toks:
            gh.append(row)
    for row in data.get("blogs_and_docs") or []:
        blob = f"{row.get('title', '')} {row.get('kind', '')}".lower()
        if toks & set(re.findall(r"[a-z0-9]{3,}", blob)) or not toks:
            blogs.append(row)
    if not gh:
        gh = sorted(
            data.get("github") or [],
            key=lambda r: r.get("stars") or 0,
            reverse=True,
        )
    else:
        gh = sorted(gh, key=lambda r: r.get("stars") or 0, reverse=True)
    if not blogs:
        blogs = list(data.get("blogs_and_docs") or [])
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
        for line in _PRACTICES.read_text(encoding="utf-8").splitlines():
            if not line.startswith("|") or "Practitioner" in line or line.startswith("|---"):
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
    if full and not hits:
        hits = all_rows
    return hits[: (20 if full else 6)]


def _peer_queries(query: str, *, limit: int = 8) -> list[dict]:
    toks = _tokens(query)
    peers = []
    for row in query_analytics.popular_queries(limit=50):
        ex = (row.get("example") or row.get("qnorm") or "")
        if toks & _tokens(ex) or not toks:
            peers.append(row)
    if not peers:
        peers = query_analytics.popular_queries(limit=limit)
    return peers[:limit]


def panel(
    query: str,
    *,
    live: bool = False,
    subject: str = "stack",
    full: bool = False,
    personal: bool = True,
) -> dict[str, Any]:
    """Visibility panel — full=True for complete agentic-truth rundown.

    When personal=True (default), indexes the ask into ~/.agent-science/truth.db.
    """
    from clearance import personal_truth

    local = personal_truth.lookup_local(query) if personal else None
    primary = stack_search.lookup(query, live=live, subject=subject)
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
    if full:
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
