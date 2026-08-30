"""Registry surface — slice 2 controls."""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from clearance import refusal_log as L


def test_every_query_becomes_a_browsable_row():
    con = L.connect(":memory:")
    L.record(con, term="Dust Bowl", assertion="The Dust Bowl ruined forty million acres",
             verdict="UNKNOWN", production="dust-bowl", cause="search_found_no_admissible_source",
             resolves_with="a primary agricultural census from the 1930s")
    before = len(L.browse_queries(con))
    res = L.search_registry(con, "Dust Bowl")
    after = L.browse_queries(con)
    assert len(after) == before + 1
    assert after[0]["query_text"] == "Dust Bowl"
    assert after[0]["result_label"] == "UNSOURCED"


def test_sourced_returns_verbatim_span():
    con = L.connect(":memory:")
    span = "The Act came into force on 1 April 2024 across England and Wales."
    L.record(con, term="1 April 2024", assertion="The Act came into force on 1 April 2024",
             verdict="GREEN", production="test", basis="primary",
             citation_url="https://example.gov/act", quoted_terms=span)
    res = L.search_registry(con, "1 April 2024")
    assert res["label"] == "SOURCED"
    assert res["quoted_terms"] == span
    assert res["citation_url"].startswith("https://")


def test_unknown_carries_named_refusal():
    con = L.connect(":memory:")
    L.record(con, term="CNE status", assertion="Copyright was never evaluated for this item",
             verdict="UNKNOWN", production="test", cause="holder_states_not_evaluated",
             citation_url="https://rightsstatements.org/vocab/CNE/1.0/",
             quoted_terms="has not been evaluated")
    res = L.search_registry(con, "has not been evaluated")
    assert res["label"] == "UNKNOWN"
    assert res["cause"] == "holder_states_not_evaluated"


def test_miss_is_honest_not_cleared():
    con = L.connect(":memory:")
    res = L.search_registry(con, "zzqq-no-such-claim")
    assert res["label"] == "NOT_CLEARED"
    assert res["cause"] == "not_in_registry"
    rows = L.browse_queries(con)
    assert rows[0]["result_label"] == "NOT_CLEARED"


def test_serve_page_renders_without_format_keyerror():
    """CSS custom properties use {--name}; .format() must not touch the template."""
    import ask_registry as ar
    page = (ar._PAGE
            .replace("{q}", "")
            .replace("{result}", "")
            .replace("{browse}", "<p>ok</p>"))
    assert "Registry" in page and "--paper" in page


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="Registry surface controls (slice 2)")
    ap.add_argument("-q", "--quiet", action="store_true", help="print summary line only")
    args = ap.parse_args()

    fns = [v for k, v in sorted(globals().items())
           if k.startswith("test_") and callable(v)]
    bad = 0
    for fn in fns:
        try:
            fn()
            if not args.quiet:
                print(f"PASS  {fn.__name__}")
        except AssertionError as e:
            bad += 1
            if not args.quiet:
                print(f"FAIL  {fn.__name__}: {e}")
    passed = len(fns) - bad
    print(f"\n{passed}/{len(fns)} passed")
    sys.exit(1 if bad else 0)
