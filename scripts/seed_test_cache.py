#!/usr/bin/env python3
"""Seed offline test cache — documents.json + searches.json.

`tests/test_watch_it_go_red.py` requires both files on disk. They are gitignored
because they hold fetched page text. Run this once after clone:

    python3 scripts/seed_test_cache.py

RightsStatements pages are fetched live. EUR-Lex returns HTTP 403 from many CI/VM
egress paths; when that happens we seed from
`fixtures/refusal-correctness/docs/eur-lex-orphan-snippet.html` and record the
provenance in the cache entry (not silent substitution).
"""
from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from clearance import instruments
from clearance.instruments import canonical, DOCS, _visible_text

EUR_URL = "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32012L0028"
RS_URLS = [
    "https://rightsstatements.org/vocab/InC/1.0/",
    "https://rightsstatements.org/vocab/CNE/1.0/",
]
EMPTY_SEARCH_CLAIM = (
    "94% of film archives are unclearable for AI training",
    "94% of film archives",
)


def _fetch_eur_lex() -> tuple[str, str]:
    """Live fetch, or fixture fallback with honest provenance string."""
    ua = "CLEARED-probe/0.1 (hackathon; contact omorke@gmail.com)"
    req = urllib.request.Request(EUR_URL, headers={"User-Agent": ua})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            text = _visible_text(r.read().decode("utf-8", errors="ignore"))
        if text.strip():
            return text, EUR_URL
    except urllib.error.HTTPError as e:
        note = f"HTTP {e.code} from EUR-Lex on this host"
    except Exception as e:
        note = f"{type(e).__name__}: {e}"
    fixture = ROOT / "fixtures/refusal-correctness/docs/eur-lex-orphan-snippet.html"
    text = _visible_text(fixture.read_text())
    return text, f"fixture:{fixture.name} ({note})"


def _seed_documents() -> None:
    for url in RS_URLS:
        body = instruments.document(url, fetch=True)
        if not body:
            raise SystemExit(f"FAIL: could not fetch {url}")

    eur_text, prov = _fetch_eur_lex()
    docs = json.loads(DOCS.read_text()) if DOCS.exists() else {}
    docs[canonical(EUR_URL)] = {"text": eur_text, "fetched_from": prov}
    DOCS.parent.mkdir(parents=True, exist_ok=True)
    DOCS.write_text(json.dumps(docs, indent=2, sort_keys=True))
    print(f"documents.json: {len(docs)} entries (EUR-Lex via {prov[:60]}…)")


def _seed_searches() -> None:
    from clearance import search as _search

    claim_text, must = EMPTY_SEARCH_CLAIM
    objective = f"Find a primary source that states verbatim: {claim_text}"
    queries = [claim_text, must]
    ck = json.dumps({"o": objective, "q": sorted(queries), "m": "advanced"}, sort_keys=True)

    cache_path = ROOT / "cache" / "searches.json"
    cache = json.loads(cache_path.read_text()) if cache_path.exists() else {}
    cache[ck] = []  # search ran, returned nothing — honest empty probe
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(cache, indent=2, sort_keys=True))
    print(f"searches.json: {len(cache)} entries (empty probe for C5 claim)")


def main() -> int:
    _seed_documents()
    _seed_searches()
    print("OK — run: python3 tests/test_watch_it_go_red.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
