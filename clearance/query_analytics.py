"""Popular queries — what devs ask, what costs money, what to optimize next."""
from __future__ import annotations

import json
import os
import re
from collections import Counter
from pathlib import Path
from typing import Optional

from clearance import refusal_log

_ROOT = Path(__file__).resolve().parent.parent
_RECEIPTS = _ROOT / "cache" / "search_receipts.jsonl"
_ALIASES = _ROOT / "truth-dictionary" / "aliases.json"


def _db(path: Path | str | None = None) -> Path:
    if path:
        return Path(path)
    return Path(os.environ.get("REFUSAL_LOG_DB", refusal_log.DB))


def popular_queries(*, db: Path | str | None = None, limit: int = 25) -> list[dict]:
    """Rank queries by how often they were asked (normalized case/trim)."""
    con = refusal_log.connect(_db(db))
    rows = con.execute(
        """
        SELECT lower(trim(query_text)) AS qnorm,
               COUNT(*) AS asks,
               MAX(query_text) AS example,
               SUM(result_label = 'SOURCED') AS sourced,
               SUM(result_label = 'NOT_CLEARED') AS not_cleared,
               SUM(result_label IN ('UNSOURCED', 'UNKNOWN', 'REFUTED')) AS refused,
               SUM(cost_tier = 'live') AS live_asks,
               SUM(cost_tier = 'free') AS free_asks,
               MAX(asked_at) AS last_asked
        FROM queries
        GROUP BY qnorm
        ORDER BY asks DESC, last_asked DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    return [dict(r) for r in rows]


def optimization_targets(*, db: Path | str | None = None, limit: int = 15) -> list[dict]:
    """Queries worth fixing — repeated misses or repeated live spend."""
    con = refusal_log.connect(_db(db))
    rows = con.execute(
        """
        SELECT lower(trim(query_text)) AS qnorm,
               COUNT(*) AS asks,
               MAX(query_text) AS example,
               SUM(result_label = 'NOT_CLEARED') AS not_cleared,
               SUM(cost_tier = 'live') AS live_asks,
               MAX(term) AS term,
               MAX(cause) AS last_cause
        FROM queries
        GROUP BY qnorm
        HAVING asks >= 1 AND (not_cleared > 0 OR live_asks > 0)
        ORDER BY live_asks DESC, not_cleared DESC, asks DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    out = []
    for r in rows:
        row = dict(r)
        row["action"] = _suggest_action(row)
        out.append(row)
    return out


def _suggest_action(row: dict) -> str:
    live = int(row.get("live_asks") or 0)
    miss = int(row.get("not_cleared") or 0)
    if live > 0:
        return "ingest verified answer or add alias — stop paying live"
    if miss > 0:
        return "boot_registry / ingest / add routing pattern"
    return "review"


def top_terms(*, db: Path | str | None = None, limit: int = 20) -> list[dict]:
    """Distinctive terms with highest cross-production reuse."""
    con = refusal_log.connect(_db(db))
    rows = con.execute(
        """
        SELECT term, reused, verdict, established, citation_url, first_seen_in
        FROM claims
        WHERE reused > 0
        ORDER BY reused DESC, term
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    return [dict(r) for r in rows]


def alias_candidates(*, db: Path | str | None = None, limit: int = 15) -> list[dict]:
    """Same term, different phrasings — add to truth-dictionary/aliases.json."""
    con = refusal_log.connect(_db(db))
    rows = con.execute(
        """
        SELECT term,
               COUNT(DISTINCT lower(trim(query_text))) AS phrasings,
               GROUP_CONCAT(DISTINCT query_text) AS examples
        FROM queries
        WHERE term IS NOT NULL AND trim(term) != ''
        GROUP BY term
        HAVING phrasings > 1
        ORDER BY phrasings DESC, term
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    existing = set()
    if _ALIASES.exists():
        try:
            existing = {k.lower() for k in json.loads(_ALIASES.read_text()).keys()}
        except json.JSONDecodeError:
            pass
    out = []
    for r in rows:
        examples = (r["examples"] or "").split(",")
        canonical = max(examples, key=len) if examples else r["term"]
        for ex in examples[:3]:
            key = ex.strip().lower()
            if key and key not in existing and key != canonical.strip().lower():
                out.append({
                    "alias": ex.strip(),
                    "canonical": canonical.strip(),
                    "term": r["term"],
                })
    return out[:limit]


def parallel_probes(*, limit: int = 15) -> list[dict]:
    """What Parallel was actually asked — from search_receipts.jsonl."""
    if not _RECEIPTS.exists():
        return []
    probes: Counter[str] = Counter()
    for line in _RECEIPTS.read_text().splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        for q in row.get("queries") or []:
            probes[q.strip().lower()] += 1
    return [{"probe": p, "asks": n} for p, n in probes.most_common(limit)]


def report(*, db: Path | str | None = None, limit: int = 15) -> dict:
    """Full dev-facing analytics bundle."""
    return {
        "popular_queries": popular_queries(db=db, limit=limit),
        "optimization_targets": optimization_targets(db=db, limit=limit),
        "top_reused_terms": top_terms(db=db, limit=limit),
        "alias_candidates": alias_candidates(db=db, limit=limit),
        "parallel_probes": parallel_probes(limit=limit),
        "db": str(_db(db)),
    }
