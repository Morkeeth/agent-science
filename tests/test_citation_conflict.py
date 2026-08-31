"""The citation check — watch it go red BEFORE it is trusted green.

THE HOLE THIS CLOSES, measured on the shipping engine at 04:4x on 2026-08-31 against
the live EUR-Lex text of Regulation (EU) 2024/1689:

    claim   Article 50 transparency breaches are subject to
            "administrative fines of up to EUR 35 000 000"
    span    "Non-compliance with the prohibition of the AI practices referred to in
             Article 5 shall be subject to administrative fines of up to EUR
             35 000 000 or, if the offender is an undertaking, up to 7 % of its total
             worldwide annual turnover for the preceding financial year, whichever is
             higher."
    verdict GREEN

The span is verbatim, it is in the cited document, it carries 75 % of the claim's
content terms, and every one of the three existing checks returns None. It is
Article 99(3), which is about **Article 5**. Article 50 sits in Article 99(4)(g) and
its tier is EUR 15 000 000 / 3 %.

WHY NO EXISTING MECHANISM COULD SEE IT. A provision citation is TWO tokens that mean
one thing. `content()` splits them and then drops the numeral: the filter is
`len(t) > 1`, so "5" in "Article 5" is invisible to every bag-of-words path in the
guard, and the surviving token "article" MATCHES. The claim and the span agree on the
only token either of them can see. This is not a weak check; it is a check reading the
wrong object.

WHAT IT MUST NOT DO. Refuse on ABSENCE. `binding` and `coverage` were both measured and
cut as gates because they refuse ordinary prose whose subject sits in the previous
sentence, and this repo has lost a day to refusing too much. So the gate is CONFLICT
only: the carrier clause cites a rival provision with the same head noun. Absence is
measured (`citation_absence`) and is not a gate.

Run: python3 tests/test_citation_conflict.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from clearance import semantic as S  # noqa: E402

# The two spans, verbatim from the fetched document. Verified in
# t_the_two_spans_are_verbatim_in_the_fetched_regulation below — never from memory.
SPAN_995 = (
    "Non-compliance with the prohibition of the AI practices referred to in Article 5 "
    "shall be subject to administrative fines of up to EUR 35 000 000 or, if the "
    "offender is an undertaking, up to 7 % of its total worldwide annual turnover for "
    "the preceding financial year, whichever is higher.")
CLAIM_50 = ('Article 50 transparency breaches are subject to "administrative fines of '
            'up to EUR 35 000 000"')
MC = "administrative fines of up to EUR 35 000 000"


# ------------------------------------------------------------ the parse, on raw text

def t_a_provision_citation_is_parsed_as_one_object():
    """Head noun + number, from RAW text. The bag of words cannot hold this."""
    assert S.provisions("referred to in Article 5 shall be") == {("article", "5")}
    assert S.provisions("Article 50 transparency breaches") == {("article", "50")}


def t_the_numeral_is_invisible_to_the_bag_of_words_and_that_is_the_defect():
    """The reason a new mechanism was needed rather than a stronger old one."""
    assert "5" not in S.content("Article 5")      # dropped: len(t) > 1
    assert "article" in S.content("Article 5")
    assert "article" in S.content("Article 50")   # the two agree on the only token


def t_article_5_is_not_a_prefix_of_article_50():
    """The whole finding is one numeral. A prefix match would erase it."""
    assert S.provisions("Article 50") == {("article", "50")}
    assert ("article", "5") not in S.provisions("Article 50")


def t_a_subparagraph_is_the_same_provision():
    """'Article 33(1)' and 'Article 33' must not conflict with each other."""
    assert S.provisions("Article 33(1) and (3)") == {("article", "33")}


def t_plural_heads_normalise():
    assert S.provisions("other than those laid down in Articles 5") == {("article", "5")}


# --------------------------------------------------------------------- the gate

def t_the_conflict_is_refused_with_a_named_code():
    f = S.check_citation(SPAN_995, claim=CLAIM_50, must_contain=MC)
    assert f is not None, "the AI Act near-miss cleared"
    assert f.code == S.CITED_PROVISION_DIFFERS
    assert "Article 5" in f.detail and "Article 50" in f.detail, f.detail


def t_the_true_span_for_article_50_is_not_refused():
    span = ("Non-compliance with any of the following provisions related to operators "
            "or notified bodies, other than those laid down in Articles 5, shall be "
            "subject to administrative fines of up to EUR 15 000 000: (g) transparency "
            "obligations for providers and deployers pursuant to Article 50.")
    claim = 'Article 50 breaches are subject to "administrative fines of up to EUR 15 000 000"'
    assert S.check_citation(span, claim=claim,
                            must_contain="administrative fines of up to EUR 15 000 000") is None


def t_an_excluded_provision_is_not_a_rival():
    """Measured as a FALSE REFUSAL on the first run of the gate against a real statute.

    The clause that is the true source for the true claim names exactly one provision,
    and names it in order to EXCLUDE it. Reading an exception as the clause's subject
    refuses the right answer.
    """
    span = ("Non-compliance with any of the following provisions related to operators "
            "or notified bodies, other than those laid down in Articles 5, shall be "
            "subject to administrative fines of up to EUR 15 000 000 or, if the "
            "offender is an undertaking, up to 3 % of its total worldwide annual "
            "turnover for the preceding financial year, whichever is higher.")
    claim = ('Article 50 transparency breaches are subject to "administrative fines of '
             'up to EUR 15 000 000"')
    f = S.check_citation(span, claim=claim,
                          must_contain="administrative fines of up to EUR 15 000 000")
    assert f is None, f"an exception was read as the subject: {f}"


def t_the_exclusion_strip_never_eats_the_anchor():
    """Same law as the aside stripper: never delete the text under judgement."""
    span = "Fines apply excluding administrative fines of up to EUR 1 under Article 9."
    out = S._without_exclusions(span, "administrative fines of up to EUR 1")
    assert "administrative fines of up to EUR 1" in out


def t_absence_alone_never_refuses():
    """Topic continuity is how English works. The absence arm is measured, not a gate."""
    span = "For other uses you need to obtain permission from the rights-holder(s)."
    claim = "Article 50 requires permission"
    assert S.check_citation(span, claim=claim, must_contain="obtain permission") is None


def t_a_claim_with_no_citation_is_never_touched():
    assert S.check_citation("anything at all here", claim="a plain claim",
                            must_contain="anything") is None


def t_the_absence_arm_exists_and_is_separately_attributable():
    """It must be runnable alone so its cost can be counted before anyone gates on it."""
    span = "Fines of up to EUR 35 000 000 apply."
    claim = "Article 50 carries fines of up to EUR 35 000 000"
    assert S.check_citation(span, claim=claim, must_contain="EUR 35 000 000") is None
    f = S.check_citation(span, claim=claim, must_contain="EUR 35 000 000",
                          gate_absence=True)
    assert f is not None and f.code == S.CITATION_ABSENT


def t_conflict_is_read_in_the_carrier_clause_not_the_whole_passage():
    """Asymmetric on purpose, and both directions bias AWAY from refusing.

    Presence of the claimed provision anywhere in the span is enough to stand down.
    A RIVAL provision only counts when it sits in the clause carrying the anchor —
    a legal document names twenty provisions per paragraph and any of them would
    otherwise 'conflict'.
    """
    span = ("Article 5 is addressed elsewhere. Fines of up to EUR 35 000 000 apply "
            "under Article 50 of this Regulation.")
    claim = 'Article 50 attracts "EUR 35 000 000"'
    assert S.check_citation(span, claim=claim, must_contain="EUR 35 000 000") is None


def t_it_can_only_demote():
    """Same law as every other check: it may refuse, it may never rescue."""
    assert S.check_citation(SPAN_995, claim=CLAIM_50, must_contain=MC) is not None
    # and inspect() with the check off leaves the span standing
    assert S.inspect(SPAN_995, claim=CLAIM_50, must_contain=MC,
                     checks=("polarity",)) is None


def t_the_check_is_registered_and_attributable():
    assert "citation" in S.CHECKS
    assert S.CITED_PROVISION_DIFFERS in S.CODES
    S.inspect("some text about Article 5 here", claim="a claim", must_contain="text",
              checks=("citation",))


def t_the_guard_carries_no_site_specific_chrome():
    """The new list must be a genre convention, not the pages we happened to fetch."""
    from clearance import locate
    src = Path(S.__file__).read_text()
    for leaked in locate._CHROME:
        assert leaked not in src, f"{leaked!r} leaked into the guard"
    for leaked in ("arxiv", "eur-lex", "rightsstatements", "europeana", "1689",
                   "creativecommons"):
        assert leaked not in src.lower(), f"{leaked!r} — a site or a document in the guard"


def t_default_checks_is_read_at_call_time_not_bound_at_import():
    """The control arm must actually be a control arm.

    `inspect` used to take `checks=DEFAULT_CHECKS` as a default ARGUMENT. Python binds
    that once, at import, so the eval harness's BASE arm — which sets
    `semantic.DEFAULT_CHECKS` — changed nothing, and the control silently ran the
    treatment. The receipt printed BASE=REFUSED for a case measured GREEN on the same
    engine minutes earlier. A harness that substitutes a rule which never applies makes
    the control agree with the treatment and then reports the agreement as a result.
    """
    saved = S.DEFAULT_CHECKS
    try:
        S.DEFAULT_CHECKS = ("polarity",)
        assert S.inspect(SPAN_995, claim=CLAIM_50, must_contain=MC) is None
        S.DEFAULT_CHECKS = ("polarity", "citation")
        assert S.inspect(SPAN_995, claim=CLAIM_50, must_contain=MC) is not None
    finally:
        S.DEFAULT_CHECKS = saved


def t_the_wedge_receipt_is_the_engine_speaking_not_a_written_answer():
    """The exhibit module holds INPUTS. Every output on the page comes from the engine.

    The failure this prevents is the one the product sells against, committed inside the
    exhibit that sells it: a page that prints a verdict and a quoted span written by
    hand, indistinguishable from one the engine produced.
    """
    from clearance import wedge as W
    body = Path(W.__file__).read_text().split('"""', 2)[-1]   # past the module docstring
    assert S.CITED_PROVISION_DIFFERS not in body, "a refusal code is written into the exhibit"
    assert "Non-compliance with the prohibition" not in body, "a span is written into the exhibit"
    assert "73 %" not in body and "73%" not in body, "a measured number is written in"

    r = W.receipt()
    if r is None:
        print("    SKIP (no receipt — run python3 scripts/wedge_receipt.py)")
        return
    assert r["produced_by"] == W.COMMAND
    assert {c["id"] for c in r["cases"]} == {c.case_id for c in W.CASES}
    for c in r["cases"]:
        assert c["engine_agrees_with_label"], f"{c['id']} disagrees with its label"
        # every span on the receipt is the engine's, and it is real
        for row in c["base"]["trail"] + c["ships"]["trail"]:
            assert row["span"], "a trail row with no span"
    one = next(c for c in r["cases"] if c["id"] == "WEDGE-1")
    assert one["base"]["label"] == "SOURCED", "the exhibit no longer shows a false GREEN"
    assert one["ships"]["refusal_code"] == S.CITED_PROVISION_DIFFERS
    two = next(c for c in r["cases"] if c["id"] == "WEDGE-2")
    assert two["ships"]["label"] == "SOURCED", "the gate now refuses the true claim too"


# ------------------------------------------------------- the span, against the source

def t_the_two_spans_are_verbatim_in_the_fetched_regulation():
    """Never quote a source from memory. This test is the reason the exhibit may ship."""
    from clearance import instruments
    URL = "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32024R1689"
    body = instruments.document(URL, fetch=True)
    if not body:
        print("    SKIP (no document — run python3 scripts/wedge_receipt.py online)")
        return
    assert SPAN_995 in body, "the 35M span is not verbatim in the fetched Regulation"
    assert "pursuant to Article 50" in body
    assert "EUR 15 000 000" in body


# --------------------------------------------------------- the whole engine, end to end

def t_the_shipping_engine_refuses_the_near_miss():
    """Not inspect() — judge_claim, the path a production actually runs."""
    from clearance import instruments
    from clearance.facts import Claim, judge_claim
    URL = "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32024R1689"
    body = instruments.document(URL, fetch=True)
    if not body:
        print("    SKIP (no document — run python3 scripts/wedge_receipt.py online)")
        return
    v = judge_claim(Claim("W1", CLAIM_50, URL, MC), fetch=True)
    assert v.verdict != "GREEN", f"the near-miss still clears: {v.quoted_terms!r}"
    # `cause` stays the closed registry vocabulary; the MECHANISM rides beside it.
    assert v.cause == "source_does_not_state_it", v.cause
    assert v.refusal_code == S.CITED_PROVISION_DIFFERS, v.refusal_code
    assert v.trail, "a refusal with no trail is a refusal you must trust"
    assert v.trail[0]["code"] == S.CITED_PROVISION_DIFFERS


def t_the_engine_still_clears_the_TRUE_article_50_claim():
    """The gate must not simply refuse everything about Article 50."""
    from clearance import instruments
    from clearance.facts import Claim, judge_claim
    URL = "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32024R1689"
    if not instruments.document(URL, fetch=True):
        print("    SKIP (no document)")
        return
    claim = ('Article 50 transparency breaches are subject to "administrative fines of '
             'up to EUR 15 000 000"')
    v = judge_claim(Claim("W2", claim, URL,
                          "administrative fines of up to EUR 15 000 000"), fetch=True)
    assert v.verdict == "GREEN", f"{v.verdict}/{v.refusal_code}: {v.quoted_terms!r}"
    assert "15 000 000" in (v.quoted_terms or "")


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
