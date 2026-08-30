#!/usr/bin/env python3
"""Seed cache/documents.json and cache/searches.json for offline controls.

Live fetch is attempted first. When EUR-Lex blocks the bot (HTTP 403), the
orphan-works fixture HTML is used — the same passage the verifier controls pin.

Run: python3 scripts/seed_document_cache.py
"""
from __future__ import annotations

import json
import re
import html as html_mod
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys_path = ROOT
import sys

sys.path.insert(0, str(ROOT))

from clearance import instruments, search  # noqa: E402
from clearance.facts import Claim, _queries_for  # noqa: E402

EUR_URL = "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32012L0028"
EUR_FIXTURE = ROOT / "fixtures/refusal-correctness/docs/eur-lex-orphan-snippet.html"


def _visible_text(raw: str) -> str:
    raw = re.sub(r"<(script|style).*?</\1>", " ", raw, flags=re.S | re.I)
    txt = html_mod.unescape(re.sub(r"<[^>]+>", " ", raw))
    return re.sub(r"\s+", " ", txt).strip()


def _eur_lex_text() -> str:
    live = instruments.document(EUR_URL, fetch=True)
    if live:
        return live
    if not EUR_FIXTURE.exists():
        raise SystemExit(f"EUR-Lex fetch failed and fixture missing: {EUR_FIXTURE}")
    return _visible_text(EUR_FIXTURE.read_text())


def _seed_documents() -> None:
    urls = [
        EUR_URL,
        "https://rightsstatements.org/vocab/InC/1.0/",
        "https://rightsstatements.org/vocab/CNE/1.0/",
    ]
    docs = instruments._load_docs()
    for url in urls:
        if url.startswith("https://eur-lex"):
            text = _eur_lex_text()
            source = "fixture" if not instruments.document(EUR_URL) else "live"
        else:
            text = instruments.document(url, fetch=True)
            source = "live"
        if not text:
            raise SystemExit(f"failed to obtain document text for {url}")
        key = instruments.canonical(url)
        docs[key] = {"text": text, "fetched_from": url, "seed": source}
        print(f"  documents[{key[:60]}…] = {len(text)} chars ({source})")
    instruments.DOCS.parent.mkdir(parents=True, exist_ok=True)
    instruments.DOCS.write_text(json.dumps(docs, indent=2, sort_keys=True))


def _search_key(claim: Claim) -> str:
    queries = _queries_for(claim)
    return json.dumps({
        "o": f"Find a primary source that states verbatim: {claim.text}",
        "q": sorted(queries),
        "m": "advanced",
    }, sort_keys=True)


def _term_key(claim: Claim) -> str:
    return (claim.must_contain or claim.text).strip().lower()[:120]


def _seed_searches() -> None:
    cache_path = search.CACHE
    cache = search._cache_load()

    c5 = Claim(
        "S2",
        "94% of film archives are unclearable for AI training",
        None,
        "94% of film archives",
    )
    cache[_search_key(c5)] = []
    cache[_term_key(c5)] = []
    print("  searches: empty result for 94% claim")

    c_s1 = Claim(
        "S1",
        "The EU Orphan Works Directive is Directive 2012/28/EU",
        None,
        "2012/28/EU",
    )
    hit = [{
        "url": EUR_URL,
        "title": "Directive 2012/28/EU (EUR-Lex)",
        "excerpt": "Directive 2012/28/EU on orphan works",
    }]
    cache[_search_key(c_s1)] = hit
    cache[_term_key(c_s1)] = hit
    print("  searches: EUR-Lex candidate for orphan-works directive claim")

    cache_path.parent.mkdir(parents=True, exist_ok=True)
    search._cache_save(cache)
    print(f"  wrote {cache_path} ({len(cache)} entries)")


def main() -> None:
    print("Seeding document cache…")
    _seed_documents()
    print("Seeding search cache…")
    _seed_searches()
    print("Done.")


if __name__ == "__main__":
    main()
