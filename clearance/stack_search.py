"""Stack-wide websearch — registry first, live clearance on miss.

Every query: SOURCED (verbatim span + URL), UNSOURCED/UNKNOWN (named cause), or
NOT_CLEARED. Results are logged to the registry for free reuse.
"""
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Optional

from clearance import refusal_log, search as _search
from clearance.facts import Claim, judge_claim
from clearance.gemini import GeminiLocator
from clearance.verdict import FACT, GREEN, Verdict

_DEFAULT_SUBJECT = "stack"
_DEFAULT_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash-lite")


def _db() -> Path:
    return Path(os.environ.get("REFUSAL_LOG_DB", refusal_log.DB))


def _distinctive_term(query: str) -> str:
    q = query.strip()
    quoted = re.search(r'"([^"]{6,})"', q)
    if quoted:
        return quoted.group(1)
    # longest alphanumeric token sequence ≥6 chars
    tokens = re.findall(r"[A-Za-z0-9][A-Za-z0-9./:_-]{5,}", q)
    if tokens:
        return max(tokens, key=len)
    return q[:80] if len(q) >= 6 else q


def _record_live(con, *, term: str, query: str, v: Verdict, production: str) -> None:
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


def _verdict_to_stack(v: Verdict, *, query: str, source: str,
                      parallel_api_calls: int = 0) -> dict:
    label = refusal_log.surface_label(verdict=v.verdict, cause=v.cause)
    why = None
    if label == "UNSOURCED":
        why = v.cause or v.reason
    elif label == "UNKNOWN":
        why = v.cause or v.reason
    return {
        "query": query,
        "label": label,
        "verdict": v.verdict,
        "cause": v.cause,
        "why": why,
        "citation_url": v.citation_url,
        "quoted_terms": v.quoted_terms,
        "source": source,
        "parallel_api_calls": parallel_api_calls,
        "engine": v.reason.split("locator:")[-1].strip(" )") if "locator:" in (v.reason or "") else None,
    }


def search(query: str, *, subject: str = _DEFAULT_SUBJECT, live: bool = True,
           db: Path | str | None = None, model: str = _DEFAULT_MODEL) -> dict:
    """THE stack websearch entry point. Registry hit = free; miss = live clearance."""
    q = query.strip()
    if not q:
        return {"query": q, "label": "NOT_CLEARED", "cause": "empty_query",
                "why": "query was empty", "source": "none", "parallel_api_calls": 0}

    dbp = Path(db) if db else _db()
    con = refusal_log.connect(dbp)

    # Import here to avoid circular import at module load
    import ask_registry
    cached = ask_registry.ask(q, db=dbp)
    if cached.get("label") != "NOT_CLEARED":
        cached["source"] = "registry"
        cached["parallel_api_calls"] = 0
        cached["subject"] = subject
        return cached

    if not live:
        cached["source"] = "registry_miss"
        cached["subject"] = subject
        return cached

    _search.reset_calls()
    term = _distinctive_term(q)
    claim = Claim("Q1", q, None, term)
    try:
        v = judge_claim(claim, locator=GeminiLocator(model=model),
                        live_search=True, fetch=True)
    except RuntimeError as e:
        return {
            "query": q, "label": "NOT_CLEARED", "cause": "search_failed",
            "why": str(e), "source": "live_error", "parallel_api_calls": _search.calls(),
            "subject": subject,
        }

    _record_live(con, term=term, query=q, v=v, production=subject)
    out = _verdict_to_stack(v, query=q, source="live", parallel_api_calls=_search.calls())
    out["subject"] = subject
    out["term"] = term
    return out


def stats(*, db: Path | str | None = None) -> dict:
    dbp = Path(db) if db else _db()
    con = refusal_log.connect(dbp)
    st = refusal_log.stats(con)
    recent = refusal_log.browse_queries(con, limit=10)
    return {
        **st,
        "recent_queries": recent,
        "db": str(dbp),
    }
