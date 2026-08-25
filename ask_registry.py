"""ask_registry — the websearch companion, POC #1 (Oscar's spine, VISION-2026-08).

The front surface of Agent Science: ask a question, get the SOURCED answer from the
registry of already-cleared truths, or an honest "not cleared yet." No model, no network
— it reads the compounding log (clearance/refusal_log.py) that every clearance run writes.

    python3 ask_registry.py "EU AI Act penalties"
    python3 ask_registry.py "React 19"          --> GREEN, sourced, or honest miss

This is the daily-use hook: a claim proven once is free for everyone afterward. A miss is
not a failure — it is the registry telling you this has not been cleared, so you know NOT
to trust an unsourced answer. That honesty is the product.
"""
from __future__ import annotations

import os
import sqlite3
import sys

DB = os.path.join(os.path.dirname(__file__), "cache", "refusal_log.db")

_VERDICT_GLOSS = {
    "GREEN": "SOURCED — a real document states this, verbatim",
    "UNKNOWN": "NOT CLEARED — searched/attempted, no admissible source yet",
    "RED": "REFUTED — a source contradicts it",
    "DISPUTED": "DISPUTED — sources conflict",
}


def ask(query: str, db: str = DB, limit: int = 5) -> dict:
    """Search the registry by distinctive term. Returns the cleared rows (verdict +
    citation) or an empty hit list — the honest 'not cleared yet'."""
    if not os.path.exists(db):
        return {"query": query, "rows": [], "note": "registry empty (no log yet — run a clearance)"}
    con = sqlite3.connect(db)
    q = f"%{query.lower().strip()}%"
    rows = con.execute(
        "SELECT term, verdict, cause, citation_url, quoted_terms, reused "
        "FROM claims WHERE lower(term) LIKE ? OR lower(quoted_terms) LIKE ? "
        "ORDER BY (verdict='GREEN') DESC, reused DESC LIMIT ?",
        (q, q, limit),
    ).fetchall()
    return {
        "query": query,
        "rows": [
            {"term": t, "verdict": v, "cause": c, "url": u,
             "quote": (qt or "")[:120], "reused": r}
            for (t, v, c, u, qt, r) in rows
        ],
    }


def _fmt(res: dict) -> str:
    L = [f"\n  registry ← {res['query']!r}"]
    if res.get("note"):
        L.append(f"    {res['note']}")
    if not res["rows"]:
        L.append("    NOT CLEARED YET — nothing in the registry sources this.")
        L.append("    (an honest miss: do not trust an unsourced answer. This is the product.)")
        return "\n".join(L) + "\n"
    for r in res["rows"]:
        gloss = _VERDICT_GLOSS.get(r["verdict"], r["verdict"])
        L.append(f"    [{r['verdict']}] {r['term'][:60]}")
        L.append(f"        {gloss}")
        if r["url"]:
            L.append(f"        source: {r['url'][:80]}")
        if r["reused"]:
            L.append(f"        reused {r['reused']}x — cleared once, free since")
    return "\n".join(L) + "\n"


def main(argv=None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if not args:
        print("usage: python3 ask_registry.py \"<your question>\"")
        return 2
    print(_fmt(ask(" ".join(args))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
