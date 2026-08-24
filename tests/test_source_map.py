"""The source-of-truth map: which hosts the clearance engine will trust as primary.

The engine can only CLEAR a claim on a source it recognizes as an independent primary
origin. So the allowlist in clearance/independence.py IS the map of source-of-truths,
and it must (a) recognize the authoritative publishers — national official gazettes,
international institutions, standards bodies — and (b) never round a lookalike host up
to primary, because a false primary is the exact error this product refuses to make.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from clearance import independence as ind


def _cls(url: str) -> str:
    return ind.classify(url)[0]


def test_recognizes_authoritative_primary_publishers():
    primaries = [
        "https://www.legifrance.gouv.fr/loda/id/X",          # France gazette/legal
        "https://www.gesetze-im-internet.de/englisch_bgb/",  # Germany federal law
        "https://www.boe.es/eli/es/l/2024",                  # Spain BOE
        "https://www.gazzettaufficiale.it/atto/serie",       # Italy Gazzetta Ufficiale
        "https://www.un.org/en/about-us/charter",            # UN
        "https://www.who.int/publications/report",           # WHO
        "https://data.worldbank.org/indicator/X",            # World Bank data
        "https://www.ietf.org/rfc/rfc2119.txt",              # IETF RFC (the standard)
        "https://www.iso.org/standard/12345.html",           # ISO standard
        "https://eur-lex.europa.eu/legal-content/EN/",       # still there (regression)
    ]
    for url in primaries:
        assert _cls(url) == "primary", (url, ind.classify(url))


def test_never_rounds_a_lookalike_up_to_primary():
    # A false primary rounds a derived source up to a source of truth — the one error
    # the product must not make. The leading-dot fragments are what prevent it.
    for url in (
        "https://fun.org/anything",        # not *.un.org
        "https://notgov.example.com/x",     # contains "gov" but not a gov TLD
        "https://myiso.org.evil.com/x",     # not *.iso.org
        "https://en.wikipedia.org/wiki/X",  # derived, not primary
    ):
        assert _cls(url) != "primary", (url, ind.classify(url))


def test_derived_still_beats_primary_when_both_would_match():
    # Ordering guard: a wikipedia mirror must read DERIVED even though it is on .org.
    assert _cls("https://en.wikipedia.org/wiki/Copyright") == "derived"


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    failed = 0
    for fn in fns:
        try:
            fn(); print(f"PASS  {fn.__name__}")
        except AssertionError as e:
            failed += 1; print(f"FAIL  {fn.__name__}: {e}")
    print(f"\n{len(fns) - failed}/{len(fns)} passed")
    sys.exit(1 if failed else 0)
