"""Delivered gap-row format — both eval arms emit identical text the scorer reads."""
from __future__ import annotations

import re
from typing import Optional


def render_gap_row(
    *,
    claim: str,
    label: str,
    span: Optional[str] = None,
    cause: Optional[str] = None,
    url: Optional[str] = None,
) -> str:
    """Registry-facing row both baseline and shipping must print."""
    if label not in ("SOURCED", "UNSOURCED"):
        raise ValueError(f"label must be SOURCED|UNSOURCED, got {label!r}")
    lines = [f"CLAIM: {claim.strip()}", f"LABEL: {label}"]
    if label == "SOURCED":
        if not span:
            raise ValueError("SOURCED row requires SPAN")
        lines.append(f"SPAN: {span.strip()}")
        if url:
            lines.append(f"URL: {url.strip()}")
    else:
        lines.append(f"CAUSE: {(cause or 'unspecified').strip()}")
    return "\n".join(lines)


def parse_gap_row(text: str) -> dict[str, str]:
    """Blind parse — scorer sees only delivered text, not internal verdict enums."""
    fields: dict[str, str] = {}
    for line in text.strip().splitlines():
        if ":" not in line:
            continue
        key, val = line.split(":", 1)
        fields[key.strip().upper()] = val.strip()
    label = fields.get("LABEL", "")
    if label not in ("SOURCED", "UNSOURCED"):
        raise ValueError(f"unparseable LABEL in delivered row:\n{text}")
    return fields


def gold_from_delivered(text: str) -> str:
    """Map delivered LABEL to held-out gold vocabulary."""
    label = parse_gap_row(text)["LABEL"]
    return "SUPPORTED" if label == "SOURCED" else "NOT_SUPPORTED"


def score_delivered(text: str, expected: str) -> bool:
    return gold_from_delivered(text) == expected


def excerpt_around(haystack: str, needle: str, *, radius: int = 80) -> str:
    """Verbatim excerpt for baseline arm — no paraphrase."""
    low = haystack.lower()
    idx = low.find(needle.lower())
    if idx < 0:
        return ""
    start = max(0, idx - radius)
    end = min(len(haystack), idx + len(needle) + radius)
    snippet = haystack[start:end].strip()
    snippet = re.sub(r"\s+", " ", snippet)
    return snippet
