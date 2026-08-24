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
"""

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
