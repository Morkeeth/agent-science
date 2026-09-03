"""Popular queries — what devs ask, what costs money, what to optimize next.

Traffic split: gate/demo probes (ralph film loops, xyzzy probes) must not drive
alias/ingest priority. See clearance/traffic.py.
"""
from __future__ import annotations

import json
import os
import re
from collections import Counter
from pathlib import Path
from typing import Optional

from clearance import refusal_log, traffic as traffic_mod

_ROOT = Path(__file__).resolve().parent.parent
_RECEIPTS = _ROOT / "cache" / "search_receipts.jsonl"
_ALIASES = _ROOT / "truth-dictionary" / "aliases.json"


def _db(path: Path | str | None = None) -> Path:
    if path:
        return Path(path)
    return Path(os.environ.get("REFUSAL_LOG_DB", refusal_log.DB))


def _annotated_rows(con) -> list[dict]:
    """Every query row with effective traffic (stored or heuristic)."""
    have = {r["name"] for r in con.execute("PRAGMA table_info(queries)")}
    cols = "id, query_text, result_label, cost_tier, cause, term, asked_at"
    if "traffic" in have:
        cols += ", traffic"
    if "source" in have:
        cols += ", source"
    rows = []
    for r in con.execute(f"SELECT {cols} FROM queries"):
        d = dict(r)
        stored = d.get("traffic")
        d["traffic_effective"] = traffic_mod.effective_for_row(
            d.get("query_text") or "", stored
        )
        rows.append(d)
    return rows


def traffic_notes(*, db: Path | str | None = None) -> dict:
    """Human-readable split — prove whether /popular is gate-polluted."""
    con = refusal_log.connect(_db(db))
    rows = _annotated_rows(con)
    counts: Counter[str] = Counter()
    top_by: dict[str, Counter[str]] = {
        "human": Counter(),
        "gate": Counter(),
        "fleet": Counter(),
        "demo": Counter(),
        "unknown": Counter(),
    }
    for r in rows:
        t = r["traffic_effective"]
        counts[t] += 1
        q = re.sub(r"\s+", " ", (r.get("query_text") or "").strip().lower())
        if q:
            top_by.setdefault(t, Counter())[q] += 1
    total = sum(counts.values())
    demo_n = counts.get("demo", 0)
    gate_n = counts.get("gate", 0)
    polluted = total > 0 and (demo_n + gate_n) / total >= 0.25
    top_demo = top_by.get("demo", Counter()).most_common(3)
    notes = []
    if polluted:
        notes.append(
            f"POLLUTED: gate+demo are {demo_n + gate_n}/{total} "
            f"({round(100 * (demo_n + gate_n) / total)}%) of logged asks — "
            "do not optimize aliases from popular_all alone."
        )
    if top_demo:
        example = top_demo[0]
        notes.append(
            f"Top demo query: {example[0]!r} ×{example[1]} "
            "(film/visibility loops — excluded from popular_human)."
        )
    if counts.get("human", 0) == 0 and counts.get("unknown", 0):
        notes.append(
            "No rows tagged traffic=human yet — popular_human keeps unknown until "
            "operators pass traffic=human on real asks."
        )
    return {
        "total_asks": total,
        "by_traffic": dict(counts),
        "polluted": polluted,
        "top_demo": [{"q": q, "asks": n} for q, n in top_demo],
        "top_gate": [
            {"q": q, "asks": n}
            for q, n in top_by.get("gate", Counter()).most_common(3)
        ],
        "notes": notes,
    }


def _aggregate(rows: list[dict], *, limit: int) -> list[dict]:
    buckets: dict[str, dict] = {}
    for r in rows:
        qnorm = re.sub(r"\s+", " ", (r.get("query_text") or "").strip().lower())
        if not qnorm:
            continue
        b = buckets.setdefault(qnorm, {
            "qnorm": qnorm,
            "asks": 0,
            "example": r.get("query_text"),
            "sourced": 0,
            "not_cleared": 0,
            "refused": 0,
            "live_asks": 0,
            "free_asks": 0,
            "last_asked": r.get("asked_at"),
            "traffic_effective": r.get("traffic_effective"),
        })
        b["asks"] += 1
        label = r.get("result_label") or ""
        if label == "SOURCED":
            b["sourced"] += 1
        elif label == "NOT_CLEARED":
            b["not_cleared"] += 1
        elif label in ("UNSOURCED", "UNKNOWN", "REFUTED"):
            b["refused"] += 1
        if r.get("cost_tier") == "live":
            b["live_asks"] += 1
        if r.get("cost_tier") == "free":
            b["free_asks"] += 1
        if (r.get("asked_at") or "") > (b.get("last_asked") or ""):
            b["last_asked"] = r.get("asked_at")
            b["example"] = r.get("query_text")
        b["traffic_effective"] = r.get("traffic_effective")
    ranked = sorted(
        buckets.values(),
        key=lambda x: (-x["asks"], x.get("last_asked") or ""),
    )
    return ranked[:limit]


def popular_queries(*, db: Path | str | None = None, limit: int = 25,
                    traffic: str | None = None) -> list[dict]:
    """Rank queries by asks. traffic=human excludes gate/demo probes."""
    con = refusal_log.connect(_db(db))
    rows = _annotated_rows(con)
    if traffic == "human":
        rows = [r for r in rows if r["traffic_effective"] not in ("gate", "demo")]
    elif traffic and traffic != "all":
        rows = [r for r in rows if r["traffic_effective"] == traffic]
    return _aggregate(rows, limit=limit)


def optimization_targets(*, db: Path | str | None = None, limit: int = 15,
                         traffic: str | None = "human") -> list[dict]:
    """Queries worth fixing — default human view so gate spam cannot win the queue."""
    rows = popular_queries(db=db, limit=max(limit * 3, 30), traffic=traffic)
    out = []
    for row in rows:
        miss = int(row.get("not_cleared") or 0)
        live = int(row.get("live_asks") or 0)
        if miss <= 0 and live <= 0:
            continue
        item = dict(row)
        item["last_cause"] = None
        item["term"] = None
        item["action"] = _suggest_action(item)
        out.append(item)
        if len(out) >= limit:
            break
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
                # Skip demo/gate probe aliases
                if traffic_mod.classify(ex) in ("gate", "demo"):
                    continue
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
    """Full dev-facing analytics bundle with traffic split."""
    notes = traffic_notes(db=db)
    return {
        "popular_queries": popular_queries(db=db, limit=limit, traffic="all"),
        "popular_human": popular_queries(db=db, limit=limit, traffic="human"),
        "popular_gate_demo": [
            r for r in popular_queries(db=db, limit=limit, traffic="all")
            if r.get("traffic_effective") in ("gate", "demo")
            or traffic_mod.classify(r.get("example") or "") in ("gate", "demo")
        ],
        "optimization_targets": optimization_targets(
            db=db, limit=limit, traffic="human"
        ),
        "optimization_targets_all": optimization_targets(
            db=db, limit=limit, traffic="all"
        ),
        "top_reused_terms": top_terms(db=db, limit=limit),
        "alias_candidates": alias_candidates(db=db, limit=limit),
        "parallel_probes": parallel_probes(limit=limit),
        "traffic_notes": notes,
        "db": str(_db(db)),
    }
