"""Retrieve practitioner candidates, but abstain from ungrounded conflict verdicts.

A research/practice contradiction requires comparable claims, scope and measurements.
Titles, seed keywords, chronology and popularity alone do not establish one.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Optional

_ROOT = Path(__file__).resolve().parent.parent
_SIGNALS = _ROOT / "truth-dictionary" / "field-signals.json"
_PRACTICES = _ROOT / "docs" / "inspiration" / "PRACTICES-CORPUS.md"


def _tokens(q: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9]{3,}", q.lower()) if t}


def _practice_hits(query: str) -> list[dict]:
    if not _PRACTICES.exists():
        return []
    toks = _tokens(query)
    hits: list[dict] = []
    for line in _PRACTICES.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|") or "Practitioner" in line or line.startswith("|---"):
            continue
        parts = [p.strip() for p in line.strip("|").split("|")]
        if len(parts) < 3:
            continue
        blob = f"{parts[0]} {parts[1]} {parts[2]}".lower()
        if toks & set(re.findall(r"[a-z0-9]{3,}", blob)):
            hits.append({"who": parts[0], "practice": parts[1], "source": parts[2]})
    return hits


def _field_hits(query: str) -> list[dict]:
    if not _SIGNALS.exists():
        return []
    try:
        data = json.loads(_SIGNALS.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    toks = _tokens(query)
    out = []
    for row in data.get("github") or []:
        blob = f"{row.get('repo', '')} {row.get('why', '')}".lower()
        if toks & set(re.findall(r"[a-z0-9]{3,}", blob)):
            out.append({"kind": "github", **row})
    for row in data.get("blogs_and_docs") or []:
        blob = f"{row.get('title', '')} {row.get('kind', '')}".lower()
        if toks & set(re.findall(r"[a-z0-9]{3,}", blob)):
            out.append({"kind": "blog", **row})
    return out


def check(
    query: str,
    primary: dict | None = None,
    *,
    practices: list[dict] | None = None,
    field: list[dict] | None = None,
) -> Optional[dict[str, Any]]:
    """Abstain until a versioned, comparable evidence case establishes conflict.

    The existing corpora contain titles, popularity and practitioner descriptions.
    None records a measured research result and a contradictory field result on a
    comparable task, scope and metric. Token overlap cannot supply that relation.
    Keep candidate retrieval available for evidence browsing, without a verdict.
    """
    return None
