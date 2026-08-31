"""CONTRARY_TO_RESEARCH — field practice outruns stale peer research.

When practitioner corpus + field adoption strongly support a practice but the
best available research predates the agentic stack or does not generalize to it,
surface CONTRARY_TO_RESEARCH with a named why — not a paraphrase verdict.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Optional

from clearance.verdict import CONTRARY_TO_RESEARCH

_ROOT = Path(__file__).resolve().parent.parent
_SIGNALS = _ROOT / "truth-dictionary" / "field-signals.json"
_PRACTICES = _ROOT / "docs" / "inspiration" / "PRACTICES-CORPUS.md"
_CONTRARY_SEEDS = _ROOT / "truth-dictionary" / "contrary-seeds.json"


def _tokens(q: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9]{3,}", q.lower()) if t}


def _load_seeds() -> list[dict]:
    if not _CONTRARY_SEEDS.exists():
        return []
    try:
        data = json.loads(_CONTRARY_SEEDS.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    return list(data.get("claims") or [])


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
    """Return a CONTRARY_TO_RESEARCH result when field outruns research."""
    q = query.strip()
    if not q:
        return None

    primary = primary or {}
    label = primary.get("label") or primary.get("result_label")
    if label == "SOURCED":
        return None

    practices = practices if practices is not None else _practice_hits(q)
    field = field if field is not None else _field_hits(q)

    for seed in _load_seeds():
        aliases = [a.lower() for a in seed.get("aliases") or []]
        canon = (seed.get("canonical") or "").lower()
        qlow = q.lower()
        if qlow not in aliases and qlow != canon and not (canon and canon in qlow):
            if not (_tokens(q) & _tokens(seed.get("canonical", ""))):
                continue
        why = seed.get("why") or ""
        research = seed.get("stale_research") or {}
        return {
            "query": q,
            "label": CONTRARY_TO_RESEARCH,
            "verdict": CONTRARY_TO_RESEARCH,
            "why": why,
            "cause": "field_outruns_research",
            "stale_research": research,
            "field_support": {
                "practices": len(practices),
                "field_signals": len(field),
            },
            "practitioner": (practices[0]["who"] if practices else seed.get("practitioner")),
            "cost_tier": "free",
            "source": "contrary_check",
            "citation_url": research.get("url"),
            "quoted_terms": research.get("span"),
        }

    # Heuristic: strong Ralph-loop field + practices, research paper is generic control
    ralph_toks = {"ralph", "loop", "huntley", "commit", "unit"}
    if len(practices) >= 1 and len(field) >= 1 and (_tokens(q) & ralph_toks):
        p0 = practices[0]
        f0 = field[0]
        return {
            "query": q,
            "label": CONTRARY_TO_RESEARCH,
            "verdict": CONTRARY_TO_RESEARCH,
            "why": (
                "Practitioner corpus documents Ralph loop (fresh agent, one unit, commit, exit) "
                f"with field adoption ({f0.get('repo') or f0.get('title', 'signal')}); "
                "peer research arXiv:2512.14012 predates Ralph tooling and generalizes to "
                "'control not vibe' — not this named loop pattern."
            ),
            "cause": "field_outruns_research",
            "stale_research": {
                "id": "arXiv:2512.14012",
                "url": "https://arxiv.org/abs/2512.14012",
                "span": "Professional developers don't vibe, they control",
                "predates": "Ralph loop repos (2025+)",
            },
            "field_support": {"practices": len(practices), "field_signals": len(field)},
            "practitioner": p0.get("who"),
            "cost_tier": "free",
            "source": "contrary_heuristic",
            "citation_url": "https://arxiv.org/abs/2512.14012",
            "quoted_terms": "Professional developers don't vibe, they control",
        }
    return None
