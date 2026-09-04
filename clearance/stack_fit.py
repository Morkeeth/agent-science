"""Stack-fit magnet eval — how well a truth fits *your* repo stack."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parent.parent

# Signals we can detect at repo root without network.
_STACK_MARKERS = {
    "python": ["pyproject.toml", "requirements.txt", "setup.py"],
    "node": ["package.json"],
    "cursor": [".cursor", "AGENTS.md"],
    "rust": ["Cargo.toml"],
    "go": ["go.mod"],
}

# Query/truth keywords → stack dimensions they improve.
_IMPROVEMENT_HINTS = {
    "context": "retrieval / memory — fewer wasted tokens per ask",
    "ralph": "agent loop discipline — one unit of work per session",
    "loop": "UX guardrails — stop conditions and verify paths",
    "rules": "project context — CLAUDE.md / AGENTS.md alignment",
    "verify": "cost — refuse early instead of live search churn",
    "registry": "cost — free tier on repeat asks",
    "parallel": "cost — only pay when dictionary misses",
    "obsidian": "retrieval — local shelf vs RAG re-fetch",
    "rag": "retrieval — span verify beats embedding guess",
    "memory": "context — personal truth DB compounds",
    "cursor": "UX — stack-native MCP hooks",
    "mcp": "UX — science_lookup in editor without raw search",
}


def detect_stack(root: Path | str | None = None) -> dict[str, Any]:
    """Detect stack from repo root markers."""
    base = Path(root or _ROOT).resolve()
    found: list[str] = []
    files: list[str] = []
    for kind, markers in _STACK_MARKERS.items():
        for m in markers:
            p = base / m
            if p.exists():
                found.append(kind)
                files.append(m)
                break
    # De-dupe preserving order
    seen: set[str] = set()
    stack = [x for x in found if not (x in seen or seen.add(x))]
    return {
        "root": str(base),
        "stack": stack or ["unknown"],
        "markers": sorted(set(files)),
        "has_agents_md": (base / "AGENTS.md").exists(),
        "has_cursor": (base / ".cursor").is_dir(),
    }


def _tokens(q: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9]{3,}", q.lower()) if t}


def _improvement_line(query: str, stack: list[str]) -> str:
    toks = _tokens(query)
    hits = [hint for kw, hint in _IMPROVEMENT_HINTS.items() if kw in toks or kw in query.lower()]
    if "cursor" in stack and any(k in toks for k in ("mcp", "lookup", "science", "registry")):
        hits.append("UX — MCP science_lookup routes fleet websearch through truth layer")
    if "python" in stack and "verify" in toks:
        hits.append("context — pytest + structural verify in CI")
    if not hits:
        return "general — adds sourced/refused discipline to agent websearch"
    return hits[0]


def score(query: str, *, root: Path | str | None = None) -> dict[str, Any]:
    """Score how well a query/truth fits the detected stack."""
    det = detect_stack(root or Path.cwd())
    return {
        "query": query,
        "fit": "unassessed",
        "improvement": "Compare the proposed practice against a pinned baseline on this repo.",
        "reasons": ["Stack markers are context; they do not demonstrate that a practice helps."],
        "stack": det,
    }


def format_result(data: dict) -> str:
    s = data.get("stack") or {}
    lines = [
        f"# Stack-fit · {data.get('query', '')[:70]}",
        f"  fit={data.get('fit')}  stack={','.join(s.get('stack') or [])}",
        f"  markers={','.join(s.get('markers') or [])}",
        f"  improvement: {data.get('improvement')}",
    ]
    for r in data.get("reasons") or []:
        lines.append(f"  reason: {r}")
    return "\n".join(lines) + "\n"
