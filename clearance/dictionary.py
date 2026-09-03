"""Truth dictionary — daily lookups with explicit cost tiers.

The dictionary is the compounding shelf: every verified answer (or honest refusal)
you pay for once becomes free for the fleet. Agents should call `lookup()` before
any live web search.

Cost tiers (cheapest first):
  free  — exact query replay or registry fuzzy hit (0 API calls)
  cheap — URL routing + cached fetch + string verify (0 Parallel, 0 Gemini)
  live  — Parallel discovery + Gemini locate (paid)
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Optional

from clearance import refusal_log, routing, search as _search
from clearance.facts import Claim, judge_claim
from clearance.gemini import GeminiLocator
from clearance.locate import DEFAULT
from clearance.verdict import CONTRARY_TO_RESEARCH, GREEN

_ROOT = Path(__file__).resolve().parent.parent
_ALIASES = _ROOT / "truth-dictionary" / "aliases.json"

COST_FREE = "free"
COST_CHEAP = "cheap"
COST_LIVE = "live"

_COST_NOTE = {
    COST_FREE: "dictionary hit — 0 API calls",
    COST_CHEAP: "routed primary + fetch — 0 Parallel, 0 Gemini",
    COST_LIVE: "live web discovery — Parallel (+ Gemini locate)",
}


def _db() -> Path:
    return Path(os.environ.get("REFUSAL_LOG_DB", refusal_log.DB))


def _aliases() -> dict[str, str]:
    if not _ALIASES.exists():
        return {}
    try:
        raw = json.loads(_ALIASES.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return {k.strip().lower(): v.strip() for k, v in raw.items() if k and v}


def canonical_query(query: str) -> str:
    """Map casual phrasing to a canonical dictionary key when listed."""
    q = query.strip()
    return _aliases().get(q.lower(), q)


def _distinctive_term(query: str) -> str:
    q = query.strip()
    quoted = re.search(r'"([^"]{6,})"', q)
    if quoted:
        return quoted.group(1)
    tokens = re.findall(r"[A-Za-z0-9][A-Za-z0-9./:_-]{5,}", q)
    if tokens:
        return max(tokens, key=len)
    return q[:80] if len(q) >= 6 else q


def _enrich(res: dict, *, cost_tier: str, subject: str,
            parallel_api_calls: int = 0) -> dict:
    out = dict(res)
    out["cost_tier"] = cost_tier
    out["cost_note"] = _COST_NOTE.get(cost_tier, cost_tier)
    out["parallel_api_calls"] = parallel_api_calls
    out["subject"] = subject
    if cost_tier == COST_FREE:
        out.setdefault("source", "dictionary")
    if res.get("label") == "NOT_CLEARED" and cost_tier != COST_LIVE:
        out["next_step"] = (
            "Call lookup with live=True, or science_search, to run paid web discovery."
        )
    return out


def last_exact_answer(con, query: str) -> Optional[dict]:
    """Same wording as a prior SOURCED query — instant replay.

    Do not replay UNSOURCED/UNKNOWN: those are failed or stale attempts and would
    block cheap routing and registry hits on repeat asks.
    """
    row = con.execute(
        "SELECT * FROM queries WHERE lower(trim(query_text)) = lower(trim(?)) "
        "AND result_label = 'SOURCED' ORDER BY id DESC LIMIT 1",
        (query.strip(),)).fetchone()
    if not row:
        return None
    return {
        "query": query.strip(),
        "label": row["result_label"],
        "verdict": row["verdict"],
        "cause": row["cause"],
        "why": row["cause"],
        "citation_url": row["citation_url"],
        "quoted_terms": row["quoted_terms"],
        "resolves_with": row["resolves_with"],
        "term": row["term"],
        "source": "dictionary_exact",
        "matches": 1,
    }


def _record(con, *, term: str, query: str, v, production: str) -> None:
    is_green = v.verdict == GREEN
    refusal_log.record(
        con,
        term=term,
        assertion=query,
        verdict=v.verdict,
        production=production,
        basis="primary" if is_green and "PRIMARY" in (v.reason or "") else None,
        cause=v.cause,
        citation_url=v.citation_url,
        quoted_terms=v.quoted_terms,
        resolves_with=None if is_green else (v.reason or v.cause),
    )


def _cheap_route(query: str, *, subject: str, con) -> Optional[dict]:
    """Construct known-primary URL, fetch, string-verify — no paid APIs."""
    term = _distinctive_term(query)
    if not routing.candidates_for(text=query, must_contain=term):
        return None
    claim = Claim("Q1", query, None, term)
    v = judge_claim(claim, locator=DEFAULT, live_search=False, fetch=True)
    label = refusal_log.surface_label(verdict=v.verdict, cause=v.cause)
    if label == "NOT_CLEARED":
        return None
    _record(con, term=term, query=query, v=v, production=subject)
    why = v.cause or v.reason if label != "SOURCED" else None
    result = {
        "query": query,
        "label": label,
        "verdict": v.verdict,
        "cause": v.cause,
        "why": why,
        "citation_url": v.citation_url,
        "quoted_terms": v.quoted_terms,
        "term": term,
        "source": routing.routed_probe(query, term) or "route:primary",
        "probe": routing.routed_probe(query, term),
    }
    refusal_log.log_query(con, query=query, result=result)
    return result


def lookup(query: str, *, subject: str = "stack", live: bool = False,
           db: Path | str | None = None,
           model: str | None = None,
           traffic: str | None = None) -> dict:
    """Daily entry point — dictionary first, live web search only when asked."""
    from clearance import traffic as traffic_mod

    raw = query.strip()
    tclass = traffic_mod.classify(raw, traffic=traffic, subject=subject)
    if not raw:
        out = _enrich({"query": raw, "label": "NOT_CLEARED", "cause": "empty_query",
                       "why": "query was empty", "source": "none", "traffic": tclass},
                      cost_tier=COST_FREE, subject=subject)
        out["traffic"] = tclass
        return out

    dbp = Path(db) if db else _db()
    con = refusal_log.connect(dbp)
    import ask_registry

    def _stamp(res: dict) -> dict:
        res = dict(res)
        res["traffic"] = tclass
        res["subject"] = subject
        return res

    def _try_shelf(q: str) -> Optional[dict]:
        hit = last_exact_answer(con, q)
        if hit:
            hit = _stamp(hit)
            hit["cost_tier"] = COST_FREE
            refusal_log.log_query(con, query=raw, result=hit)
            out = _enrich(hit, cost_tier=COST_FREE, subject=subject)
            out["traffic"] = tclass
            return out
        reg = ask_registry.ask(q, db=dbp)
        if reg.get("label") != "NOT_CLEARED":
            reg = _stamp(reg)
            reg["source"] = "registry"
            reg["query"] = raw
            out = _enrich(reg, cost_tier=COST_FREE, subject=subject)
            out["traffic"] = tclass
            return out
        return None

    with traffic_mod.scoped(traffic=tclass, subject=subject):
        canon = canonical_query(raw)
        for q in dict.fromkeys([raw, canon]):  # preserve order, de-dupe
            got = _try_shelf(q)
            if got:
                return got

        q = canon

        cheap = _cheap_route(q, subject=subject, con=con)
        if cheap:
            cheap = _stamp(cheap)
            cheap["cost_tier"] = COST_CHEAP
            cheap["query"] = raw
            out = _enrich(cheap, cost_tier=COST_CHEAP, subject=subject)
            out["traffic"] = tclass
            return out

        if not live:
            from clearance import contrary
            c = contrary.check(q)
            if c:
                c = _stamp(c)
                refusal_log.log_query(con, query=raw, result=c)
                out = _enrich(c, cost_tier=COST_FREE, subject=subject)
                out["traffic"] = tclass
                return out
            miss = _stamp({
                "query": raw,
                "label": "NOT_CLEARED",
                "cause": "not_in_registry",
                "why": ("nothing in the dictionary sources this yet — "
                        "try live=true or ingest a verified claim"),
            })
            miss["cost_tier"] = COST_FREE
            miss["source"] = "dictionary_miss"
            refusal_log.log_query(con, query=raw, result=miss)
            out = _enrich(miss, cost_tier=COST_FREE, subject=subject)
            out["traffic"] = tclass
            return out

        _search.reset_calls()
        term = _distinctive_term(q)
        claim = Claim("Q1", q, None, term)
        mdl = model or os.environ.get("GEMINI_MODEL", "gemini-3.5-flash-lite")
        try:
            v = judge_claim(claim, locator=GeminiLocator(model=mdl),
                            live_search=True, fetch=True)
        except RuntimeError as e:
            out = _enrich(_stamp({
                "query": q, "label": "NOT_CLEARED", "cause": "search_failed",
                "why": str(e), "source": "live_error",
            }), cost_tier=COST_LIVE, subject=subject, parallel_api_calls=_search.calls())
            out["traffic"] = tclass
            return out

        _record(con, term=term, query=q, v=v, production=subject)
        label = refusal_log.surface_label(verdict=v.verdict, cause=v.cause)
        why = v.cause or v.reason if label != "SOURCED" else None
        result = _stamp({
            "query": raw,
            "label": label,
            "verdict": v.verdict,
            "cause": v.cause,
            "why": why,
            "citation_url": v.citation_url,
            "quoted_terms": v.quoted_terms,
            "term": term,
            "source": "live",
            "cost_tier": COST_LIVE,
        })
        refusal_log.log_query(con, query=raw, result=result)
        out = _enrich(result, cost_tier=COST_LIVE, subject=subject,
                      parallel_api_calls=_search.calls())
        out["traffic"] = tclass
        return out


def economics(*, db: Path | str | None = None) -> dict:
    """How much the dictionary is saving — exact replays vs live-sized queries."""
    dbp = Path(db) if db else _db()
    con = refusal_log.connect(dbp)
    st = refusal_log.stats(con)
    rows = con.execute(
        "SELECT result_label, COUNT(*) n FROM queries GROUP BY result_label"
    ).fetchall()
    by_label = {r["result_label"]: r["n"] for r in rows}
    total_q = sum(by_label.values())
    not_cleared = by_label.get("NOT_CLEARED", 0)
    answered = total_q - not_cleared
    return {
        **st,
        "queries_logged": total_q,
        "queries_answered": answered,
        "queries_not_cleared": not_cleared,
        "dictionary_hit_rate": round(answered / total_q, 3) if total_q else 0.0,
        "aliases": len(_aliases()),
        "db": str(dbp),
    }
