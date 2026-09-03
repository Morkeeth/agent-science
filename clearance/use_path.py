"""Use-bar interceptor — truth layer before raw websearch.

Agents call `intercept()` (or CLI `use-bar`) before any raw browser/search tool.
Every call writes a session receipt so a human can prove the path was used.

This is a habit + measurable stub, not a hard OS-level hook. Cursor/Claude cannot
be forced to skip WebSearch; the receipt is the evidence Oscar fills.
"""
from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from clearance import stack_search, traffic as traffic_mod

_ROOT = Path(__file__).resolve().parent.parent
_DEFAULT_RECEIPTS = Path.home() / ".agent-science" / "session-receipts.jsonl"
_REPO_RECEIPTS = _ROOT / "cache" / "session_receipts.jsonl"


def receipts_path() -> Path:
    env = os.environ.get("AGENT_SCIENCE_RECEIPTS")
    if env:
        return Path(env)
    if os.environ.get("AGENT_SCIENCE_RECEIPTS_REPO"):
        return _REPO_RECEIPTS
    return _DEFAULT_RECEIPTS


def new_session_id() -> str:
    return os.environ.get("AGENT_SCIENCE_SESSION") or f"sess-{uuid.uuid4().hex[:12]}"


def write_receipt(row: dict, *, path: Path | None = None) -> Path:
    p = path or receipts_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return p


def read_receipts(*, path: Path | None = None, limit: int = 50) -> list[dict]:
    p = path or receipts_path()
    if not p.exists():
        return []
    lines = p.read_text(encoding="utf-8").splitlines()
    out = []
    for line in lines[-limit:]:
        if not line.strip():
            continue
        out.append(json.loads(line))
    return out


def intercept(
    query: str,
    *,
    mode: str = "lookup",
    live: bool = False,
    traffic: str = "human",
    subject: str = "stack",
    session_id: Optional[str] = None,
    db=None,
    write: bool = True,
) -> dict:
    """Run truth-layer lookup (default) or visibility; always emit a receipt row.

    mode:
      lookup     — science_lookup / dictionary (default free tier)
      visibility — full panel when available; primary verdict + receipt
    """
    q = (query or "").strip()
    sid = session_id or new_session_id()
    tclass = traffic_mod.classify(q, traffic=traffic, subject=subject)
    mode = (mode or "lookup").strip().lower()

    if mode == "visibility":
        from clearance import visibility
        panel = visibility.panel(
            q, live=live, subject=subject, full=True, personal=False
        )
        primary = (panel.get("primary") or {}) if isinstance(panel, dict) else {}
        # visibility.panel already called lookup (may have logged). Re-tag receipt.
        result = {
            "query": q,
            "label": primary.get("label") or primary.get("result_label") or "UNKNOWN",
            "verdict": primary.get("verdict"),
            "cause": primary.get("cause"),
            "citation_url": primary.get("citation_url"),
            "quoted_terms": primary.get("quoted_terms"),
            "cost_tier": primary.get("cost_tier") or ("live" if live else "free"),
            "source": primary.get("source") or "visibility",
            "mode": "visibility",
            "panel_keys": sorted(panel.keys()) if isinstance(panel, dict) else [],
        }
    else:
        result = stack_search.lookup(
            q, live=live, subject=subject, db=db, traffic=tclass
        )
        result = dict(result)
        result["mode"] = "lookup"

    result["traffic"] = tclass
    result["session_id"] = sid
    receipt_id = f"rcpt-{uuid.uuid4().hex[:10]}"
    result["receipt_id"] = receipt_id

    row = {
        "receipt_id": receipt_id,
        "session_id": sid,
        "asked_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "query": q,
        "mode": result.get("mode"),
        "label": result.get("label"),
        "cost_tier": result.get("cost_tier"),
        "traffic": tclass,
        "live": bool(live),
        "citation_url": result.get("citation_url"),
        "cause": result.get("cause"),
        "path": "agent-science-use-bar",
    }
    if write:
        path = write_receipt(row)
        result["receipt_path"] = str(path)
    return result


def assert_receipt_exists(
    query: str,
    *,
    session_id: Optional[str] = None,
    path: Path | None = None,
    within_last: int = 20,
) -> dict:
    """Prove a prior intercept covered this query (or raise)."""
    rows = read_receipts(path=path, limit=max(within_last, 1))
    qnorm = query.strip().lower()
    for row in reversed(rows):
        if session_id and row.get("session_id") != session_id:
            continue
        if (row.get("query") or "").strip().lower() == qnorm:
            return row
    raise AssertionError(
        f"no use-bar receipt for {query!r} "
        f"(session={session_id or 'any'}); run intercept() before raw websearch"
    )


def use_bar_summary(*, path: Path | None = None, limit: int = 20) -> dict:
    rows = read_receipts(path=path, limit=limit)
    by_traffic: dict[str, int] = {}
    by_label: dict[str, int] = {}
    for r in rows:
        by_traffic[r.get("traffic") or "unknown"] = (
            by_traffic.get(r.get("traffic") or "unknown", 0) + 1
        )
        by_label[r.get("label") or "?"] = by_label.get(r.get("label") or "?", 0) + 1
    return {
        "n": len(rows),
        "by_traffic": by_traffic,
        "by_label": by_label,
        "path": str(path or receipts_path()),
        "recent": rows[-5:],
    }
