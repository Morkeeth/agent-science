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


def test_the_curve_never_renders_without_its_provenance():
    """The adjacency trap, bound.

    The curve (0 -> 20 -> 39 -> 46%) is measured on 56 claims across four scripts. The
    registry rendered beside it is a different population whose live reuse counter has
    read 0. Printing the curve next to those counters, without saying they are different
    objects, is a sentence the page's own data contradicts — which is the exact failure
    that got three of four builds rejected on 2026-08-30.
    """
    import ask_registry as ar
    from clearance import curve
    with tempfile.TemporaryDirectory() as d:
        db = Path(d) / "r.db"
        page = ar.render_page(db=db)
        assert "46%" in page, "the curve is not on the page at all"
        assert curve.SOURCE in page, "the curve renders with no source file named"
        assert "56 claims" in page, "the curve renders without its population"
        assert "SEPARATE measurement" in page, \
            "the curve renders without separating itself from the live counters"
        assert "not comparable" in page


def test_the_separation_note_survives_a_non_zero_reuse_counter():
    """It must not switch itself off the moment someone uses the desk."""
    import ask_registry as ar
    with tempfile.TemporaryDirectory() as d:
        db = Path(d) / "r.db"
        con = L.connect(db)
        L.record(con, term="1 April 2024", assertion="The Act came into force on "
                 "1 April 2024", verdict="GREEN", production="p", basis="primary",
                 citation_url="https://example.gov/act",
                 quoted_terms="The Act came into force on 1 April 2024 across England.")
        for _ in range(3):
            L.search_registry(con, "1 April 2024")
        assert L.stats(con)["reuses"] > 0, "premise: the counter should have moved"
        page = ar.render_page(db=db)
        assert "SEPARATE measurement" in page and "not comparable" in page, \
            "the live-vs-cited separation vanished once the desk was used"


def test_thin_evidence_is_counted_and_shown_not_hidden():
    """A cleared claim quoting page furniture is worse than an honest refusal."""
    import ask_registry as ar
    with tempfile.TemporaryDirectory() as d:
        db = Path(d) / "r.db"
        con = L.connect(db)
        L.record(con, term="Widget Report", assertion="The Widget Report found that "
                 "eighty-one per cent of surveyed factories missed their quota in 1998",
                 verdict="GREEN", production="p", basis="primary",
                 citation_url="https://example.org/w",
                 quoted_terms="Home About Contact Widget Report Subscribe Sign in Menu")
        thin, sourced = L.thin_evidence_count(con)
        assert (thin, sourced) == (1, 1), f"thin evidence not counted: {thin}/{sourced}"
        page = ar.render_page(db=db)
        assert "thin evidence" in page.lower(), "the page hides its own weakest row"
        assert "rest on thin evidence" in page, "the count is not stated up front"


def test_a_full_span_is_not_flagged_thin():
    """The flag must discriminate, or it is decoration on every row."""
    with tempfile.TemporaryDirectory() as d:
        con = L.connect(Path(d) / "r.db")
        L.record(con, term="1 April 2024",
                 assertion="The Act came into force on 1 April 2024",
                 verdict="GREEN", production="p", basis="primary",
                 citation_url="https://example.gov/act",
                 quoted_terms="The Act came into force on 1 April 2024 across England "
                              "and Wales.")
        assert L.thin_evidence_count(con) == (0, 1)


def test_every_refusal_says_what_would_settle_it():
    """A refusal nobody can act on is a dead end wearing a label."""
    from clearance.verdict import CAUSES
    missing = [c for c in CAUSES if not L.explain(c)[1]]
    assert not missing, \
        f"engine causes with no plain-English resolution on the surface: {missing}"


def test_the_template_is_never_run_through_format():
    """CSS custom properties look like format fields. `.format()` on this page raises.

    The page carries `--paper`, `--rule`, `--sourced` and friends; `str.format` reads
    every one of those braces as a replacement field. The template is therefore assembled
    with explicit `.replace()` of named markers, and this control keeps it that way by
    proving the rendered page still carries the custom properties AND that no
    single-brace marker survived into the output.
    """
    import ask_registry as ar
    with tempfile.TemporaryDirectory() as d:
        page = ar.render_page(db=Path(d) / "r.db")
    assert "--paper" in page and "--sourced" in page, "the palette did not render"
    assert "__CSS__" not in page and "__BODY__" not in page, \
        "a template marker survived into the page"
    assert "{q}" not in page and "{result}" not in page, \
        "an unreplaced placeholder is showing on the page"
    assert page.strip().startswith("<!DOCTYPE html>") and page.rstrip().endswith("</html>")


def test_the_shelf_shows_a_refusal_in_the_same_column_as_evidence():
    """The product's argument, rendered as a layout rather than asserted in prose."""
    import ask_registry as ar
    with tempfile.TemporaryDirectory() as d:
        db = Path(d) / "r.db"
        con = L.connect(db)
        L.record(con, term="Dust Bowl", assertion="The Dust Bowl ruined forty million "
                 "acres of farmland", verdict="UNKNOWN", production="p",
                 cause="source_does_not_state_it",
                 citation_url="https://example.org/d",
                 quoted_terms="document opened, 4,000 characters read")
        page = ar.render_page(db=db)
        assert "class=\"refusal\"" in page, "a refusal renders as nothing at all"
        assert "It does not state this" in page, \
            "the refusal shows a machine cause and no plain-English meaning"
        assert "Settled by" in page, "the refusal does not say what would settle it"


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items())
           if k.startswith("test_") and callable(v)]
    bad = 0
    for fn in fns:
        try:
            fn()
            print(f"PASS  {fn.__name__}")
        except AssertionError as e:
            bad += 1
            print(f"FAIL  {fn.__name__}: {e}")
    print(f"\n{len(fns) - bad}/{len(fns)} passed")
    sys.exit(1 if bad else 0)
