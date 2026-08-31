#!/usr/bin/env python3
"""Mine search caches for optimization signals — domains, probes, cache hits."""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "cache"


def _domains(urls: list[str]) -> Counter:
    return Counter(urlparse(u).netloc for u in urls if u)


def main() -> int:
    searches = json.loads((CACHE / "searches.json").read_text()) if (CACHE / "searches.json").exists() else {}
    docs = json.loads((CACHE / "documents.json").read_text()) if (CACHE / "documents.json").exists() else {}
    receipts_path = CACHE / "search_receipts.jsonl"
    receipts = []
    if receipts_path.exists():
        for line in receipts_path.read_text().splitlines():
            if line.strip():
                receipts.append(json.loads(line))

    print("=== Agent Science search analytics ===\n")
    print(f"search cache entries: {len(searches)}")
    print(f"documents cached:     {len(docs)}")
    print(f"receipt lines:        {len(receipts)}")

    all_urls: list[str] = []
    for v in searches.values():
        for c in v:
            all_urls.append(c.get("url", ""))
    print("\nTop domains (search cache results):")
    for dom, n in _domains(all_urls).most_common(12):
        print(f"  {n:4d}  {dom}")

    print("\nTop domains (fetched documents):")
    for dom, n in _domains(list(docs.keys())).most_common(12):
        print(f"  {n:4d}  {dom}")

    if receipts:
        hits = sum(1 for r in receipts if r.get("cache_hit"))
        live = len(receipts) - hits
        print(f"\nReceipts: {hits} cache hits, {live} live Parallel calls logged")
        routed = sum(1 for r in receipts if r.get("source") == "route")
        if routed:
            print(f"  routed (no Parallel): {routed}")

    print("\nOptimization levers (in order):")
    print("  1. registry / corpus hit  → 0 Parallel, 0 fetch")
    print("  2. routing (CELEX, rights)  → 0 Parallel, 1 fetch")
    print("  3. searches.json term cache → 0 Parallel")
    print("  4. documents.json           → 0 re-fetch")
    print("  5. Parallel live            → paid discovery")
    return 0


if __name__ == "__main__":
    sys.exit(main())
