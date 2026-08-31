"""The front surface — the properties that make it evidence rather than a poster.

A marketing page for a verification product is the easiest place in the world to commit
the thing the product refuses. Every control here pins one way this page could assert
something the engine did not.

Run: python3 tests/test_front_surface.py
"""
from __future__ import annotations

import json
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import ask_registry as A  # noqa: E402
from clearance import curve, refusal_log, semantic as S, wedge as W  # noqa: E402


def _tmpdb() -> Path:
    d = Path(tempfile.mkdtemp())
    return d / "registry.db"


# ------------------------------------------------- the page may only speak the engine

def t_the_wedge_renders_nothing_it_cannot_source():
    """With no receipt the hero must say so, not fall back to a written-down answer."""
    saved = W.RECEIPT
    try:
        W.RECEIPT = Path("/nonexistent/receipt.json")
        html = A._wedge_html()
    finally:
        W.RECEIPT = saved
    assert "REFUSED" not in html and "SOURCED" not in html
    assert S.CITED_PROVISION_DIFFERS not in html
    assert W.COMMAND in html, "it must name the command that would produce the receipt"


def t_every_span_on_the_hero_is_a_span_from_the_receipt():
    """The strongest form of the rule: no sentence of evidence without a source row."""
    r = W.receipt()
    if r is None:
        print("    SKIP (no receipt)")
        return
    page = A._wedge_html()
    known = set()
    for c in r["cases"]:
        for arm in ("base", "ships"):
            if c[arm].get("quoted_terms"):
                known.add(c[arm]["quoted_terms"])
            for t in c[arm].get("trail") or []:
                known.add(t.get("span") or "")
    # every marked-up span block on the page, tags stripped, must be one of those
    for block in re.findall(r'<p class="nm-span">(.*?)</p>', page, re.S):
        text = re.sub(r"<[^>]+>", "", block)
        text = (text.replace("&quot;", '"').replace("&#x27;", "'")
                    .replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&"))
        assert text in known, f"a span on the page is in no receipt row: {text[:90]!r}"


def t_the_mark_never_boxes_a_citation_the_engine_did_not_name():
    """The adjacency defect, pinned.

    The first version boxed EVERY provision and coloured it by whether the claim named
    it — which put a refusal-red box on "Articles 5" inside the span that CLEARS the
    true claim, because that sentence names Article 5 in order to exclude it. Two
    correct facts side by side, asserting a relation neither supports, on the row that
    was right.
    """
    span = ("Non-compliance with any of the following provisions, other than those laid "
            "down in Articles 5, shall be subject to fines of up to EUR 15 000 000.")
    out = A._mark_span(span, must_contain="fines of up to EUR 15 000 000",
                       claim='Article 50 breaches attract "fines of up to EUR 15 000 000"',
                       rivals=frozenset())
    assert 'class="nm-cite"' not in out, "an unnamed citation was marked as a rival"
    assert 'class="anchor"' in out, "the shared anchor is not marked"

    # and WITH the engine naming it, it is marked
    out2 = A._mark_span(span, must_contain="fines of up to EUR 15 000 000",
                        claim='Article 50 breaches attract "fines of up to EUR 15 000 000"',
                        rivals=frozenset({"5"}))
    assert 'class="nm-cite"' in out2


def t_rivals_are_read_out_of_the_engines_own_finding():
    f = S.check_citation(
        "Non-compliance referred to in Article 5 shall be subject to fines of X.",
        claim='Article 50 breaches attract "fines of X"', must_contain="fines of X")
    assert f is not None
    # The finding's own sentence names BOTH provisions ("cites Article 5 and never
    # Article 50"). A looser parse pulled both out and the page boxed the claim's own
    # provision in refusal-red.
    assert "Article 50" in f.detail and "Article 5 " in f.detail
    assert A._rivals_named_by(f.detail) == frozenset({"5"})
    assert A._rivals_named_by(f.detail, 'Article 50 breaches') == frozenset({"5"})


def t_the_mark_cannot_alter_the_span():
    """Strip the tags and you must get back exactly the text the engine judged."""
    span = 'A "quoted" <thing> & Article 5 and fines of up to EUR 1.'
    out = A._mark_span(span, must_contain="fines of up to EUR 1",
                       claim="Article 50 and fines of up to EUR 1", rivals=frozenset({"5"}))
    text = re.sub(r"<[^>]+>", "", out)
    for a, b in (("&quot;", '"'), ("&#x27;", "'"), ("&lt;", "<"), ("&gt;", ">"),
                 ("&amp;", "&")):
        text = text.replace(a, b)
    assert text == span, f"{text!r} != {span!r}"


# ---------------------------------------------------- the numbers carry their command

def t_the_measurement_strip_leads_with_eligible_rows_not_verdicts_changed():
    """The sentence this page must never print is 'measured on 312 claims, no cost'.

    Zero of the cleared claims on this shelf cite a provision, so the population cannot
    exercise the check. A flip count over a population with no eligible rows reads
    exactly like a safety result and is not one.
    """
    if not A.EVAL_PATH.exists():
        print("    SKIP (no eval file)")
        return
    e = json.loads(A.EVAL_PATH.read_text())
    strip = A._measurement_html()
    assert strip, "the front page carries no measurement"
    assert str(e["attribution"]["cite_a_provision"]) in strip
    assert str(e["attribution"]["greens"]) in strip
    assert "cannot" in strip.lower(), "the limit is not stated as a limit"
    assert A.EVAL_COMMAND in strip, "a number with no command beside it"
    assert "does NOT ship" in strip or "not ship" in strip, \
        "the unshipped arm is not disclosed"


def t_the_curve_cannot_render_without_its_provenance():
    page = A.render_front(db=_tmpdb())
    assert curve.PROVENANCE[:60] in page
    assert curve.WHAT_IS_NOT_TRUE[:40] in page, "only the flattering half is rendered"


def t_nothing_on_the_page_calls_the_cost_curve_flat():
    """The chart and the prose must describe the same four numbers the same way.

    The prose read "$0.00377 -> $0.00352, flat" while the panel drawn from those same
    numbers printed "7% below the first, and not monotonic". Two sentences on one page,
    describing one set, disagreeing — on the front page of the product that exists to
    catch exactly that.
    """
    page = A.render_front(db=_tmpdb())
    lo = min(l.cost_per_claim for l in curve.LEGS)
    hi = max(l.cost_per_claim for l in curve.LEGS)
    assert f"${lo:.4f}-${hi:.4f}" in page, "the cost panel hides its own spread"
    assert "not monotonic" in page
    assert ", flat" not in page and " flat." not in page, \
        "the page smooths a spread it draws"
    # and the prose carries the real range, from the same numbers as the bars
    assert f"${lo:.5f}" in curve.WHAT_IS_NOT_TRUE and f"${hi:.5f}" in curve.WHAT_IS_NOT_TRUE


def t_the_two_measures_are_never_on_one_axis():
    """A dual axis lets whoever drew it choose the crossing point and the conclusion."""
    page = A.render_front(db=_tmpdb())
    assert page.count("<svg") == 2, "the curve is not two single-measure panels"


def t_a_one_cause_negative_space_says_it_is_one_cause():
    """A shelf showing one cause must say so, and say how many it has NOT shown.

    THIS CONTROL WAS GREEN ON THE WRONG SENTENCE (rewritten 2026-08-31 ~09:00,
    adversarial pass). It asserted the literal string "the other nine causes are rare",
    which was the page's off-by-one: nine was `len(CAUSE_ENGLISH) - 1`, and
    CAUSE_ENGLISH is the rendering dictionary — the engine's nine causes plus
    `not_in_registry`, which lives in the `queries` table and can never appear in the
    `claims` table this box counts. So the test defended the defect against the fix:
    correcting the page turned this line red. The remainder is now DERIVED from the
    engine's closed set, so the control cannot pin a stale literal again.
    """
    from clearance import verdict as V
    db = _tmpdb()
    con = refusal_log.connect(db)
    refusal_log.record(con, term="only cause", assertion="a claim about 2019",
                       verdict="UNKNOWN", production="p", cause="source_does_not_state_it",
                       citation_url="https://example.gov/x", quoted_terms="read it")
    page = A.render_front(db=db)
    expected = A._spell(len(V.CAUSES) - 1)
    assert f"not a claim that the other {expected} causes are rare" in page, (
        f"a one-cause shelf must say the other {expected} of "
        f"{len(V.CAUSES)} engine causes are not shown to be rare")


# ------------------------------------------------------------------ the audit page

def t_the_heros_call_to_action_works_on_a_cold_clone():
    """The registry db is gitignored. The page's one CTA must not dead-end on a clone.

    A fresh clone has the committed receipt and an EMPTY shelf. Rendered against an
    empty database, the link the front page tells a stranger to click returned "Not on
    the shelf" — the product's own front door failing for exactly the reader it was
    written for. The fallback reads the RECEIPT, which is engine output, so the page
    still cannot print a verdict the engine did not produce.
    """
    r = W.receipt()
    if r is None:
        print("    SKIP (no receipt)")
        return
    case = next(c for c in r["cases"] if c["id"] == "WEDGE-1")
    page = A.render_refusal(term=case["must_contain"], db=_tmpdb())
    assert "Not on the shelf" not in page
    assert case["ships"]["refusal_code"] in page
    assert W.COMMAND in page, "the fallback must name where the row came from"
    assert "The spans considered — 1" in page


def t_no_surface_string_names_a_script_that_does_not_exist():
    """A test that SKIPs by naming a nonexistent script is a false sentence in the repo."""
    for path in sorted(ROOT.glob("tests/test_*.py")) + sorted(ROOT.glob("scripts/*.py")):
        for m in re.findall(r"scripts/[A-Za-z0-9_]+\.py", path.read_text()):
            assert (ROOT / m).exists(), f"{path.name} names {m}, which does not exist"


def t_the_hero_never_says_today():
    """A label dated 'today' becomes a sentence the receipt's own timestamp contradicts."""
    page = A._wedge_html()
    assert "today" not in page.lower()
    r = W.receipt()
    if r:
        assert r["produced_at"][:10] in page


def t_a_row_with_no_trail_says_so_rather_than_rendering_an_empty_audit():
    """'Nothing was considered' and 'nobody wrote it down' are different facts."""
    db = _tmpdb()
    con = refusal_log.connect(db)
    refusal_log.record(con, term="legacy row here", assertion="an old claim",
                       verdict="UNKNOWN", production="old",
                       cause="source_does_not_state_it",
                       citation_url="https://example.gov/y", quoted_terms="read it")
    page = A.render_refusal(term="legacy row here", db=db)
    assert "No trail was recorded" in page
    assert "The spans considered — 0" in page


def t_a_row_with_a_trail_renders_every_span_and_every_reason():
    db = _tmpdb()
    con = refusal_log.connect(db)
    trail = [{"span": "Alpha sentence about Article 5 here.", "admissible": False,
              "code": S.CITED_PROVISION_DIFFERS, "coverage": 0.7,
              "detail": "cited_provision_differs: the claim is about Article 50; "
                        "the clause cites Article 5"},
             {"span": "Beta sentence, also considered, and also refused.",
              "admissible": False, "code": "not_a_statement", "coverage": 0.2,
              "detail": "not_a_statement: a run of labels"}]
    refusal_log.record(con, term="alpha sentence", assertion="a claim about Article 50",
                       verdict="UNKNOWN", production="p",
                       cause="source_does_not_state_it",
                       citation_url="https://example.gov/z", quoted_terms="read it",
                       refusal_code=S.CITED_PROVISION_DIFFERS, trail=trail)
    page = A.render_refusal(term="alpha sentence", db=db)
    assert "The spans considered — 2" in page
    # Needles that do not straddle a mark: the anchor and the citation are wrapped in
    # tags, which is the device working, so a needle spanning one would fail for the
    # right reason and read as the wrong one.
    for needle in ("Alpha sentence", "here.", "Beta sentence", "also refused."):
        assert needle in page, needle
    assert "not_a_statement" in page and S.CITED_PROVISION_DIFFERS in page
    assert "candidate 2 of 2" in page


def t_the_trail_survives_a_write_and_a_read():
    """Written by NAMED column: a positional insert shifts every value on schema growth."""
    db = _tmpdb()
    con = refusal_log.connect(db)
    refusal_log.record(con, term="round trip", assertion="claim", verdict="UNKNOWN",
                       production="p", cause="no_source_offered",
                       trail=[{"span": "s", "admissible": False, "code": "c",
                               "detail": "d", "coverage": 0.5}])
    row = con.execute("SELECT * FROM claims WHERE term='round trip'").fetchone()
    assert row["first_seen_in"] == "p", "columns shifted"
    assert row["cause"] == "no_source_offered"
    assert refusal_log.trail_of(row)[0]["span"] == "s"


def t_the_shelf_still_renders_after_the_schema_grew():
    page = A.render_page(db=_tmpdb())
    assert "The shelf" in page


# ------------------------------------------------------------- the routes, requested

def t_every_internal_link_resolves_to_a_served_route():
    """A link nobody clicked is a route nobody ran.

    `/front` was named in the lane brief, in NIGHTRUN, in the FINDING and in the footer
    of the shelf, and the handler answered 404 on it: the branch list was `/`,
    `/index.html`, `/refusal`, `/registry`. It is the same defect as `serve()` calling a
    `_Handler` that did not exist for a week, one level down — and the same reason it
    survived, which is that rendering a page is not requesting it.

    So this control does not read the branch list. It starts the real server and GETs
    every internal href the three pages emit.
    """
    import threading
    import urllib.error
    import urllib.request
    from http.server import HTTPServer

    srv = HTTPServer(("127.0.0.1", 0), A._Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = "http://127.0.0.1:%d" % srv.server_address[1]
    try:
        seen, dead = set(), []
        for path in ("/", "/registry"):
            page = urllib.request.urlopen(base + path).read().decode()
            for href in re.findall(r'href="(/[^"]*)"', page):
                if href in seen:
                    continue
                seen.add(href)
                try:
                    urllib.request.urlopen(base + href).read()
                except urllib.error.HTTPError as e:
                    dead.append(f"{href} -> {e.code} (linked from {path})")
        assert seen, "no internal links were found to check"
        assert not dead, "the surface links to routes it does not serve: " + "; ".join(dead)
    finally:
        srv.shutdown()
        srv.server_close()


def t_the_provenance_line_does_not_overclaim():
    """The exhibit's provenance may not claim more than the exhibit can show.

    It read "nothing on this page is written by hand" while `wedge.CASES[].note` — a
    substantive reading of the instrument, "Article 99(4) sets EUR 15 000 000 / 3 % and
    reaches Article 50 at point (g)" — rendered two lines below it, and `_wedge_html`
    appended another hand-written sentence after that. Both are TRUE. The provenance
    claim about them was not, on the front page of the product that sells against
    exactly that.
    """
    r = W.receipt()
    if r is None:
        print("    SKIP (no receipt)")
        return
    page = A._wedge_html()
    hand = [c.note for c in W.CASES if c.note in page or c.note in page.replace("&#x27;", "'")]
    assert hand, "the exhibit no longer renders a hand-written note — retire this control"
    assert "nothing on this page is written by hand" not in page.lower(), \
        "the provenance denies hand-written prose the page is printing"
    low = W.PROVENANCE.lower()
    assert "written by hand" in low and "only thing" in low, \
        "the provenance no longer discloses the hand-written reading"


def t_every_surface_states_the_recall_boundary():
    """"Refuses the error" would be an overclaim; the gate refuses one SHAPE of it.

    The held-out probe (`scripts/probe_citation_heldout.py`, 11 claims labelled before
    the run) closes 9 against BASE's 7 — and the rows it misses cite a rival provision
    whose subject is named in words, so there is no numeral for the gate to conflict
    with. A surface that sells the mechanism without that sentence sells a recall it
    does not have.
    """
    b = W.RECALL_BOUNDARY
    assert "shape" in b.lower(), \
        "the boundary no longer says it refuses one SHAPE of the error"
    assert "probe_citation_heldout" in b, \
        "the boundary states a limit without the command that measures it"
    # A recall claim with no cost beside it is half a measurement. The 23-row set found
    # the first false refusal this gate has produced (T13, a clause that cross-references
    # another article in passing) and "zero false refusals" was a property of the
    # 11-row population, not of the mechanism.
    assert "false refusal" in b, \
        "the boundary sells recall without printing what the check costs"
    assert "zero false refusal" not in b.lower(), \
        "the boundary claims a cost the 23-row held-out set contradicts"
    r = W.receipt()
    if r is None:
        print("    SKIP (no receipt)")
        return
    page = A._wedge_html()
    assert "SHAPE of the error" in page.replace("&#x27;", "'"), \
        "the exhibit sells the mechanism without stating what it does not refuse"


def t_the_measured_population_is_named_frozen_on_the_page():
    """The denominator used to move when the product was used. Say so where it prints.

    The number is read from the eval receipt, and the receipt now carries the population
    block (files + the day it was frozen), so a hand-typed count cannot drift back in.
    """
    if not A.EVAL_PATH.exists():
        print("    SKIP (no eval file)")
        return
    e = json.loads(A.EVAL_PATH.read_text())
    pop = e["registry"].get("population")
    assert pop, "the eval receipt no longer names its population"
    strip = A._measurement_html()
    assert str(e["registry"]["total"]) in strip, "the page's claim count is not the receipt's"
    assert pop["frozen_at"] in strip and "MANIFEST" in strip, \
        "the page prints a denominator without saying it is frozen or where"
    from clearance import population as P
    assert e["registry"]["total"] == P.manifest()["claims"], \
        "the published number and the frozen manifest disagree about the population"


def t_the_measurement_strip_does_not_deny_the_heldout_probe():
    """The page must not say "its only evidence is the two cases" while printing eleven.

    The strip was written when n=2 was true. The adversarial pass built the held-out
    probe and this wave put its result on the same page, one block above — so the word
    "only" became a sentence the page's own neighbour contradicts. That is the exact
    defect this product exists to catch, printed on its own front page.
    """
    strip = A._measurement_html()
    if not strip:
        print("    SKIP (no eval file)")
        return
    assert "only evidence is the two cases" not in strip, \
        "the strip denies the held-out probe the same page prints"
    r = W.receipt()
    if r is None:
        return
    page = A.render_front()
    assert "SHAPE of the error" in page and "only evidence is the two cases" not in page, \
        "one page states the held-out result and denies it"


def t_the_declared_cause_vocabulary_is_the_engines_not_the_renderers():
    """"A closed set of 10" was counted over a dictionary that is not the engine's set.

    FOUND 2026-08-31 ~09:00, adversarial pass. The warn box read the denominator from
    `refusal_log.CAUSE_ENGLISH` — which is the RENDERING dictionary, the engine's nine
    causes PLUS `not_in_registry`. That tenth entry is returned by `refusal_log.ask()`
    for a query that matches nothing and written by `log_query` into the `queries`
    table; `by_cause` counts the `claims` table, which it can never enter. So the page
    sold "a closed set of 10" for a vocabulary of 9, over a population that can only
    ever exercise 9 — a number correct about the wrong object, in the one paragraph on
    the page whose job is to stop a reader inferring a number the data does not support.

    Two properties, because either alone passes the defect:
      1. the declared size IS the engine's closed set, `clearance.verdict.CAUSES`;
      2. every cause the shelf actually shows is a member of that set, so the
         numerator and the denominator are counted over the same vocabulary.
    """
    from clearance import verdict as V
    page = A.render_front()
    m = re.search(r"refusal vocabulary is a closed set of (\d+); this shelf has "
                  r"exercised (\d+) of them", page)
    if m is None:
        print("    SKIP (shelf shows more than one refusal cause; the box is off)")
        return
    declared, exercised = int(m.group(1)), int(m.group(2))
    assert declared == len(V.CAUSES), (
        f"the page declares a closed set of {declared}; the engine's closed set "
        f"clearance/verdict.py::CAUSES has {len(V.CAUSES)}")
    others = re.search(r"the other (\w+) causes are rare", page)
    assert others, "the warn box no longer names the unexercised remainder"
    assert others.group(1) == A._spell(declared - exercised), (
        f"'the other {others.group(1)}' does not equal {declared} - {exercised}")
    # The numerator's vocabulary must be the denominator's, or the ratio is over two
    # different sets: exactly the adjacency defect this test was written for.
    con = refusal_log.connect(A._db(None))
    shown = {c["cause"] for c in refusal_log.by_cause(con)
             if c["label"] != "SOURCED" and c["cause"]}
    stray = sorted(shown - set(V.CAUSES))
    assert not stray, (
        f"the shelf shows refusal causes that are not in the declared closed set: "
        f"{stray} — the ratio counts two different vocabularies")


if __name__ == "__main__":
    failed = 0
    names = [n for n in globals() if n.startswith("t_")]
    for n in sorted(names, key=lambda k: list(globals()).index(k)):
        try:
            globals()[n]()
            print(f"  PASS  {n[2:].replace('_', ' ')}")
        except Exception as exc:
            failed += 1
            print(f"  FAIL  {n[2:].replace('_', ' ')}\n        {exc}")
    print(f"\n{len(names) - failed} passed, {failed} failed")
    raise SystemExit(1 if failed else 0)
