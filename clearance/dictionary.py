"""Truth dictionary — daily lookups with explicit cost tiers.

The dictionary is the compounding shelf: every verified answer
you pay for once becomes free for the fleet. Agents should call `lookup()` before
any live web search.

Cost tiers (cheapest first):
  free  — exact query replay or registry exact assertion (0 API calls)
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
from clearance.verdict import GREEN

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
    """Replay only the latest settled result for the identical assertion.

    Legacy history without an established assertion is not proof of identity.
    A newer uncertain or contrary result invalidates earlier success.
    """
    row = con.execute(
        "SELECT * FROM queries WHERE lower(trim(query_text)) = lower(trim(?)) "
        "ORDER BY id DESC LIMIT 1", (query.strip(),)).fetchone()
    if not row or row["result_label"] not in ("SOURCED", "REFUTED"):
        return None
    if refusal_log.norm_term(row["established"]) != refusal_log.norm_term(query):
        return None
    current = con.execute("SELECT * FROM claims WHERE slot=? ORDER BY first_seen_at DESC LIMIT 1",
                          (refusal_log.claim_key(query),)).fetchone()
    if current and (current["verdict"] != row["verdict"]
                    or current["quoted_terms"] != row["quoted_terms"]
                    or current["citation_url"] != row["citation_url"]):
        return None
    return {
        "query": query.strip(), "label": row["result_label"],
        "verdict": row["verdict"], "cause": row["cause"], "why": row["cause"],
        "citation_url": row["citation_url"], "quoted_terms": row["quoted_terms"],
        "established": row["established"], "resolves_with": row["resolves_with"],
        "term": row["term"], "source": "dictionary_exact", "matches": 1,
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


def _cheap_route(query: str, *, subject: str, con, trace: list, refresh: bool = False) -> Optional[dict]:
    """Construct known-primary URL, fetch, string-verify — no paid APIs."""
    term = _distinctive_term(query)
    if not routing.candidates_for(text=query, must_contain=term):
        trace.append({"route": "primary_route", "query": query, "outcome": "no_candidate"})
        return None
    claim = Claim("Q1", query, None, term)
    v = judge_claim(claim, locator=DEFAULT, live_search=False, fetch=True, **({"refresh": True} if refresh else {}))
    label = refusal_log.surface_label(verdict=v.verdict, cause=v.cause)
    trace.append({"route": "primary_route", "query": query, "outcome": label,
                  "reason": v.cause or v.reason})
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
    result["established"] = query
    return result


def lookup(query: str, *, subject: str = "stack", live: bool = False,
           db: Path | str | None = None, model: str | None = None,
           refresh: bool = False) -> dict:
    """Look up an assertion; refresh bypasses saved verdicts, live permits paid discovery.

    Trace entries describe operations performed in this function. They do not claim
    that each source was fetched; the engine's source trail carries that information.
    Each user call writes exactly one query event, including failed discovery.
    """
    raw = query.strip()
    con = refusal_log.connect(Path(db) if db else _db())
    trace: list[dict] = []
    candidates: list[dict] = []

    def finish(result, tier=COST_FREE, calls=0):
        result = _enrich(result, cost_tier=tier, subject=subject, parallel_api_calls=calls)
        result["query"] = raw
        result["trace"] = trace
        result.setdefault("candidates", candidates)
        refusal_log.log_query(con, query=raw, result=result)
        return result

    try:
        if not raw:
            return finish({"label": "NOT_CLEARED", "cause": "empty_query",
                           "why": "query was empty", "source": "none"})
        if not refresh:
            hit = last_exact_answer(con, raw)
            trace.append({"route": "dictionary_exact", "query": raw,
                          "outcome": "hit" if hit else "miss"})
            if hit:
                return finish(hit)
            # Aliases aid topic retrieval only. They never authorize reusing a
            # different assertion's verdict as an answer to the original question.
            for q in dict.fromkeys([raw, canonical_query(raw)]):
                reg = refusal_log.search_registry(con, q, log=False, reuse=False)
                candidates.extend(reg.get("candidates", []))
                settled = (q == raw and reg.get("label") != "NOT_CLEARED"
                           and not reg.get("unsettled"))
                trace.append({"route": "registry", "query": q,
                              "outcome": "hit" if settled else "unsettled" if reg.get("unsettled") else "miss"})
                if settled:
                    refusal_log.lookup(con, term=reg["term"], assertion=reg["established"])
                    reg["source"] = "registry"
                    return finish(reg)

        cheap = _cheap_route(raw, subject=subject, con=con, trace=trace, **({"refresh": True} if refresh else {}))
        if cheap and refusal_log.is_settled_for_reuse(verdict=cheap.get("verdict"), cause=cheap.get("cause")):
            return finish(cheap, COST_CHEAP)
        if not live:
            return finish(cheap or {
                "label": "NOT_CLEARED", "cause": "not_in_registry",
                "why": "No evidence establishes this assertion yet. Enable live discovery to search.",
                "source": "dictionary_miss",
            }, COST_CHEAP if cheap else COST_FREE)

        _search.reset_calls()
        term = _distinctive_term(raw)
        claim = Claim("Q1", raw, None, term)
        mdl = model or os.environ.get("GEMINI_MODEL", "gemini-3.5-flash-lite")
        try:
            v = judge_claim(claim, locator=GeminiLocator(model=mdl), live_search=True, fetch=True, **({"refresh": True} if refresh else {}))
        except RuntimeError as e:
            trace.append({"route": "live_search", "query": raw, "outcome": "error", "reason": str(e)})
            return finish({"label": "NOT_CLEARED", "cause": "search_failed",
                           "why": str(e), "source": "live_error"}, COST_LIVE, _search.calls())
        label = refusal_log.surface_label(verdict=v.verdict, cause=v.cause)
        trace.append({"route": "live_search", "query": raw, "outcome": label,
                      "reason": v.cause or v.reason})
        _record(con, term=term, query=raw, v=v, production=subject)
        return finish({"label": label, "verdict": v.verdict, "cause": v.cause,
                       "why": (v.cause or v.reason) if label != "SOURCED" else None,
                       "citation_url": v.citation_url, "quoted_terms": v.quoted_terms,
                       "term": term, "established": raw, "source": "live"}, COST_LIVE, _search.calls())
    finally:
        con.close()


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
    hits = con.execute("SELECT COUNT(*) FROM queries WHERE source IN ('dictionary_exact', 'registry') "
                       "AND result_label IN ('SOURCED', 'REFUTED')").fetchone()[0]
    con.close()
    return {
        **st,
        "queries_logged": total_q,
        "queries_answered": answered,
        "queries_not_cleared": not_cleared,
        "dictionary_hits": hits,
        "dictionary_hit_rate": round(hits / total_q, 3) if total_q else 0.0,
        "aliases": len(_aliases()),
        "db": str(dbp),
    }
