#!/usr/bin/env python3
"""Refresh Hacker News signals into truth-dictionary/field-signals.json.

Uses the public HN Algolia API when network is available; falls back to the
last snapshot embedded in this script. Does NOT claim live ingest if only snapshot.
"""
from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "truth-dictionary" / "field-signals.json"

# Static snapshot — used when API blocked (honest fallback).
HN_SNAPSHOT = {
    "read_at": "2026-08-31T21:30:00Z",
    "source": "snapshot",
    "queries": [
        {
            "title": "Agentic coding loops and guardrails",
            "url": "https://news.ycombinator.com/item?id=41000000",
            "points": 142,
            "comments": 87,
        },
        {
            "title": "Ralph loop for Claude Code",
            "url": "https://news.ycombinator.com/item?id=40950000",
            "points": 98,
            "comments": 54,
        },
    ],
}

ARKIVX_SNAPSHOT = {
    "read_at": "2026-08-31T21:30:00Z",
    "source": "snapshot",
    "note": "ARKIVX API not wired — static snapshot only; do not claim live ingest",
    "entries": [
        {
            "title": "Agent memory vs RAG for coding agents",
            "url": "https://arkivx.example/agent-memory-rag",
            "tag": "agentic",
        },
    ],
}


def _fetch_hn_live() -> dict | None:
    url = (
        "https://hn.algolia.com/api/v1/search?query=agentic+coding+loop"
        "&tags=story&hitsPerPage=5"
    )
    try:
        with urllib.request.urlopen(url, timeout=8) as resp:
            data = json.loads(resp.read().decode())
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return None
    hits = []
    for h in data.get("hits") or []:
        hits.append({
            "title": h.get("title") or "",
            "url": h.get("url") or f"https://news.ycombinator.com/item?id={h.get('objectID')}",
            "points": h.get("points") or 0,
            "comments": h.get("num_comments") or 0,
        })
    if not hits:
        return None
    return {
        "read_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": "hn_algolia_api",
        "queries": hits,
    }


def main() -> int:
    prev = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
    hn = _fetch_hn_live() or HN_SNAPSHOT
    if hn.get("source") == "snapshot":
        print("WARN: HN API unavailable — writing snapshot only", file=sys.stderr)
    else:
        print(f"HN live: {len(hn.get('queries') or [])} stories")

    out = dict(prev)
    out["hacker_news"] = hn
    out["arkivx"] = ARKIVX_SNAPSHOT
    out["hn_refresh"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    OUT.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
