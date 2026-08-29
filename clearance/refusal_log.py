"""The cross-production claim log — and the refusal log inside it.

The corpus compounds inside ONE production's subject. This compounds across every
production that ever ran, which is a different economic object: a claim established
once should be free for everyone afterwards, forever.

**The asset is the negative space.** Anyone can rebuild "what is true" — that is a
search, and four funded companies do it. Nobody else accumulates **what CANNOT be
proven, and why**, because no competing product emits refusals at all. A refusal is
expensive to produce (a full search, several documents fetched and read, an independence
assessment) and it is the half a marketplace has no reason to build.

Cross-production reuse is LOOSER than same-subject reuse and therefore riskier, so every
record keeps the wording it was established under. A reuse whose original assertion was
phrased differently is flagged, never silently served.
"""
from __future__ import annotations

import json
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

DB = Path(__file__).resolve().parent.parent / "cache" / "refusal_log.db"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS claims (
    term          TEXT NOT NULL,     -- the distinctive term, normalised
    slot          TEXT NOT NULL,     -- what ABOUT it: a date, a quantity, a name
    established   TEXT NOT NULL,     -- the assertion as first proven or refused
    verdict       TEXT NOT NULL,
    basis         TEXT,              -- primary | corroborated | (refusals: null)
    cause         TEXT,              -- for refusals
    citation_url  TEXT,
    quoted_terms  TEXT,
    origins       TEXT,              -- json list of origin keys
    resolves_with TEXT,              -- for a refusal: what WOULD settle it
    first_seen_in TEXT NOT NULL,     -- which production established it
    first_seen_at TEXT NOT NULL,
    reused        INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (term, slot)
);
CREATE TABLE IF NOT EXISTS queries (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    query_text    TEXT NOT NULL,
    result_label  TEXT NOT NULL,     -- SOURCED | UNSOURCED | UNKNOWN | NOT_CLEARED
    verdict       TEXT,
    cause         TEXT,
    term          TEXT,
    citation_url  TEXT,
    quoted_terms  TEXT,
    resolves_with TEXT,
    asked_at      TEXT NOT NULL
);
"""

# User-facing labels on the registry surface. Collapsing no_source and search-empty
# into one blob was the defect this product refuses everywhere else.
_UNSOURCED_CAUSES = frozenset({
    "no_source_offered",
    "search_found_no_admissible_source",
    "source_does_not_state_it",
    "source_never_fetched",
    "terms_never_fetched",
})


def surface_label(*, verdict: str | None, cause: str | None = None) -> str:
    """Map an engine verdict to the registry's three poles (+ honest miss)."""
    if verdict == "GREEN":
        return "SOURCED"
    if verdict == "RED":
        return "REFUTED"
    if verdict == "UNKNOWN" and (cause or "") in _UNSOURCED_CAUSES:
        return "UNSOURCED"
    if verdict == "UNKNOWN":
        return "UNKNOWN"
    return "NOT_CLEARED"

# What a claim is ABOUT, so "adopted in 2012" and "was known as the Orphan Works
# Directive" do not collide on the same distinctive term. This is the collision the
# per-subject corpus could only flag; here it is prevented.
_SLOTS = (
    (r"\b(1[6-9]\d{2}|20\d{2})\b", "date"),
    (r"\b\d[\d,\.]*\s*(%|percent|million|billion|thousand|hours|titles|items|works|licences|licenses)\b", "quantity"),
    (r"\bsection\s+\d+|\barticle\s+\d+\b", "provision"),
)


def slot_of(assertion: str, term: str = "") -> str:
    """What the assertion is ABOUT, with the TERM REMOVED FIRST.

    The term itself carries digits - "Directive 2012/28/EU", "Section 108" - so
    classifying the raw sentence made every claim about that directive a date-claim, and
    two different assertions would have collided on one primary key. The collision the
    per-subject corpus could only flag would have been silently merged here, which is
    strictly worse. Strip the term, then classify what remains.
    """
    a = assertion.lower()
    if term:
        a = a.replace(norm_term(term), " ")
    for pattern, name in _SLOTS:
        if re.search(pattern, a):
            return name
    return "identity"


def norm_term(term: str) -> str:
    return re.sub(r"\s+", " ", (term or "").strip().lower())


def connect(path: Path | str = DB) -> sqlite3.Connection:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(p)
    con.row_factory = sqlite3.Row
    con.executescript(_SCHEMA)
    return con


def record(con, *, term: str, assertion: str, verdict: str, production: str,
           basis: Optional[str] = None, cause: Optional[str] = None,
           citation_url: Optional[str] = None, quoted_terms: Optional[str] = None,
           origins: Optional[list] = None, resolves_with: Optional[str] = None) -> None:
    """Write a claim OR a refusal. Refusals are first-class here, not a side effect."""
    con.execute(
        "INSERT OR IGNORE INTO claims VALUES (?,?,?,?,?,?,?,?,?,?,?,?,0)",
        (norm_term(term), slot_of(assertion, term), assertion, verdict, basis, cause,
         citation_url, quoted_terms, json.dumps(origins or []), resolves_with,
         production, datetime.now(timezone.utc).isoformat(timespec="seconds")))
    con.commit()


def lookup(con, *, term: str, assertion: str) -> Optional[dict]:
    r = con.execute("SELECT * FROM claims WHERE term=? AND slot=?",
                    (norm_term(term), slot_of(assertion, term))).fetchone()
    if not r:
        return None
    con.execute("UPDATE claims SET reused = reused + 1 WHERE term=? AND slot=?",
                (norm_term(term), slot_of(assertion, term)))
    con.commit()
    d = dict(r)
    d["origins"] = json.loads(d["origins"] or "[]")
    # Cross-production reuse is looser than same-subject reuse. If the assertion that
    # established this record was worded differently, say so rather than serving it as
    # though it were the same sentence.
    d["reused_from_wording"] = (d["established"] if d["established"].strip().lower()
                                != assertion.strip().lower() else None)
    return d


def stats(con) -> dict:
    row = con.execute(
        "SELECT COUNT(*) n, SUM(verdict='GREEN') cleared, SUM(verdict!='GREEN') refused,"
        " SUM(reused) reuses, COUNT(DISTINCT first_seen_in) productions FROM claims"
    ).fetchone()
    return {k: (row[k] or 0) for k in row.keys()}


def log_query(con, *, query: str, result: dict) -> int:
    """Every query becomes a browsable registry row — the refusal is the product."""
    cur = con.execute(
        "INSERT INTO queries (query_text, result_label, verdict, cause, term, "
        "citation_url, quoted_terms, resolves_with, asked_at) VALUES (?,?,?,?,?,?,?,?,?)",
        (query.strip(), result["label"], result.get("verdict"), result.get("cause"),
         result.get("term"), result.get("citation_url"), result.get("quoted_terms"),
         result.get("resolves_with"),
         datetime.now(timezone.utc).isoformat(timespec="seconds")))
    con.commit()
    return cur.lastrowid


def browse_queries(con, *, limit: int = 50) -> list[dict]:
    """Recent registry queries — what strangers actually asked."""
    return [dict(r) for r in con.execute(
        "SELECT * FROM queries ORDER BY id DESC LIMIT ?", (limit,))]


def search_registry(con, query: str, *, limit: int = 5) -> dict:
    """Query in → SOURCED span, UNSOURCED, or UNKNOWN with named refusal."""
    q = query.strip()
    if not q:
        return {"query": q, "label": "NOT_CLEARED", "cause": "empty_query",
                "why": "query was empty", "matches": 0}

    qnorm = f"%{norm_term(q)}%"
    rows = con.execute(
        "SELECT * FROM claims WHERE lower(term) LIKE ? OR lower(established) LIKE ? "
        "OR lower(quoted_terms) LIKE ? ORDER BY (verdict='GREEN') DESC, reused DESC "
        "LIMIT ?",
        (qnorm, qnorm, qnorm, limit)).fetchall()

    if not rows:
        result = {
            "query": q,
            "label": "NOT_CLEARED",
            "verdict": None,
            "cause": "not_in_registry",
            "why": ("nothing in the registry sources this yet — run a clearance or "
                    "backfill; do not trust an unsourced answer"),
            "matches": 0,
        }
        log_query(con, query=q, result=result)
        return result

    best = dict(rows[0])
    best["origins"] = json.loads(best.get("origins") or "[]")
    label = surface_label(verdict=best["verdict"], cause=best.get("cause"))
    why = None
    if label == "UNSOURCED":
        why = best.get("resolves_with") or best.get("cause") or "no admissible source"
    elif label == "UNKNOWN":
        why = best.get("cause") or "unknown gap"
    result = {
        "query": q,
        "label": label,
        "verdict": best["verdict"],
        "cause": best.get("cause"),
        "term": best["term"],
        "established": best["established"],
        "citation_url": best.get("citation_url"),
        "quoted_terms": best.get("quoted_terms"),
        "resolves_with": best.get("resolves_with"),
        "reused": best.get("reused", 0),
        "first_seen_in": best.get("first_seen_in"),
        "matches": len(rows),
        "why": why,
    }
    log_query(con, query=q, result=result)
    # Bump reuse on the matched claim when a registry query hits it.
    lookup(con, term=best["term"], assertion=best["established"])
    return result


def as_claimreview(con, limit: int = 100) -> list:
    """Export to schema.org ClaimReview — the standard other tools already read.

    ClaimReview has no vocabulary for "cannot be sourced", so a refusal exports with
    reviewRating 0 and the reason in the body. We do not pretend the standard carries
    what it does not.
    """
    out = []
    for r in con.execute("SELECT * FROM claims LIMIT ?", (limit,)):
        cleared = r["verdict"] == "GREEN"
        out.append({
            "@context": "https://schema.org",
            "@type": "ClaimReview",
            "claimReviewed": r["established"],
            "author": {"@type": "Organization", "name": "Agent Science"},
            "reviewRating": {
                "@type": "Rating",
                "ratingValue": 5 if cleared else 0,
                "bestRating": 5, "worstRating": 0,
                "alternateName": (f"SOURCED ({r['basis']})" if cleared
                                  else f"NOT SOURCED ({r['cause']})"),
            },
            "itemReviewed": {"@type": "Claim", "appearance": {"@type": "CreativeWork"}},
            "url": r["citation_url"],
            "reviewBody": (r["quoted_terms"] if cleared
                           else (r["resolves_with"] or r["cause"] or "")),
        })
    return out
