"""The semantic guard — watch it go red BEFORE it is trusted green.

THE HOLE THIS CLOSES. `verify()` proves a passage is real and carries the claim's
distinctive term. It cannot prove the passage *asserts* the claim, and the reason is
structural, not clever: **`verify()` was never given the claim.** Its whole signature is
`verify(passage, document=, must_contain=)`. A guard cannot read a claim it does not
receive. RC5 in `fixtures/refusal-correctness/set.json` is that gap, pinned as a defect
since 2026-08-22:

    claim    "This Item is free of known copyright restrictions worldwide."
    document "Some collections elsewhere are free of known copyright restrictions;
              this Item is not one of them until evaluated."

Real span, verbatim, carrying the terms — and the sentence says the opposite. GREEN.

Every test in this file was written and RUN RED before `clearance/semantic.py` existed.
That is not a formality here: this product exists to catch controls whose red light was
never observed, and a guard shipped inside it without that observation would be the
joke of the year.

Run: python3 tests/test_semantic_guard.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from clearance import instruments, semantic as S, verify as V
from clearance.facts import Claim, judge_claim
from clearance.locate import DEFAULT
from clearance.verdict import GREEN, UNKNOWN, SOURCE_SILENT

SET = json.loads((ROOT / "fixtures/refusal-correctness/set.json").read_text())
BY_ID = {it["id"]: it for it in SET["items"]}

RC5 = BY_ID["RC5"]
RC5_DOC = (ROOT / RC5["document"]).read_text()
RC5_SPAN = ("Some collections elsewhere are free of known copyright restrictions; "
            "this Item is not\none of them until evaluated.")


def _doc(rel: str) -> str:
    return (ROOT / rel).read_text()


def _with_doc(url: str, body: str, claim: Claim, **kw):
    """judge_claim against a document served from memory — no network, no cache write."""
    saved = instruments.document

    def fake(u, fetch=False):
        return body if u == url else saved(u, fetch=fetch)

    instruments.document = fake
    try:
        return judge_claim(claim, **kw)
    finally:
        instruments.document = saved


# ---------------------------------------------------------------- the headline hole

def t_the_shipping_span_for_rc5_really_is_verbatim():
    """Establish the premise before testing the fix.

    If this ever fails, the fixture moved and every number below is about the wrong
    object. The span the locator proposes IS in the document, character for character.
    """
    proposed = DEFAULT.propose(claim=RC5["claim"], must_contain=RC5["must_contain"],
                               document=RC5_DOC)
    assert proposed is not None, "the shipping locator proposes nothing for RC5"
    assert proposed in RC5_DOC, "RC5's proposed span is not verbatim — premise broken"
    assert RC5["must_contain"] in proposed, "RC5's span lost the distinctive term"
    assert V.verify(proposed, document=RC5_DOC,
                    must_contain=RC5["must_contain"]) is None, \
        "the STRUCTURAL verifier already refuses RC5 — there is no hole to close"


def t_guard_refuses_the_rc5_span():
    """THE ONE. A verbatim span whose own sentence disowns the claim."""
    f = S.inspect(RC5_SPAN, claim=RC5["claim"], must_contain=RC5["must_contain"])
    assert f is not None, \
        "the guard admitted RC5: a span that says 'this Item is NOT one of them'"
    assert f.code in S.CODES, f"unnamed refusal code {f.code!r}"


def t_guard_reaches_rc5_through_verify_when_the_claim_is_passed():
    """The seam: verify() can only guard what it is given."""
    assert V.verify(RC5_SPAN, document=RC5_DOC,
                    must_contain=RC5["must_contain"]) is None, \
        "claim not passed: verify must behave exactly as it did before"
    r = V.verify(RC5_SPAN, document=RC5_DOC, must_contain=RC5["must_contain"],
                 claim=RC5["claim"], semantic=True)
    assert r is not None and r.code in S.CODES, \
        f"verify(claim=..., semantic=True) admitted RC5: {r}"


# ------------------------------------------------------- the false-refusal direction

def t_guard_keeps_every_labelled_supported_item():
    """The direction this product is most likely to drift in.

    A guard that closes RC5 by refusing RC1/RC2/RC6 is a worse product than the hole.
    """
    lost = []
    for it in SET["items"]:
        if it["expected"] != "SUPPORTED":
            continue
        f = S.inspect(it["accepted_passage"], claim=it["claim"],
                      must_contain=it["must_contain"])
        if f is not None:
            lost.append(f"{it['id']}: {f.code} — {f.detail}")
    assert not lost, "TRUE GREENS LOST — the guard refuses supported claims:\n  " \
        + "\n  ".join(lost)


def t_shipping_path_greens_supported_items_on_the_RIGHT_span():
    """The control the held-out set never had — and the reason it read 5/6.

    `set.json` labels whether a claim is SUPPORTED. It never checks WHICH passage
    supported it, so a GREEN on a `<nav>` link that happens to carry the date scored
    exactly like a GREEN on the operative sentence. Measured 2026-08-31: that is what
    RC1 and RC2 were doing. Two false GREENs, inside the labelled-correct column, in the
    fixture written to catch false GREENs.

    A label is a claim about an object. This one was about the verdict; the defect was in
    the span. So: run the real path, and assert on the span.
    """
    wrong = []
    for it in SET["items"]:
        if it["expected"] != "SUPPORTED":
            continue
        url = f"fixture://span-{it['id']}"
        v = _with_doc(url, _doc(it["document"]),
                      Claim(it["id"], it["claim"], url, it["must_contain"]),
                      semantic=True)
        if v.verdict != GREEN:
            wrong.append(f"{it['id']}: refused a supported claim — {v.reason}")
        elif it["accepted_passage"] not in v.quoted_terms:
            wrong.append(f"{it['id']}: GREEN on a span that is not the labelled "
                         f"evidence:\n         got {v.quoted_terms[:120]!r}\n"
                         f"      wanted {it['accepted_passage'][:120]!r}")
    assert not wrong, "SUPPORTED items cleared on the wrong span:\n  " + "\n  ".join(wrong)


def t_a_negation_inside_the_claim_is_not_a_flip():
    """RC6 is a claim ABOUT a negation. Its supporting sentence must carry that 'not'.

    A polarity check that fires on any 'not' in the span would refuse every claim whose
    own subject matter is an absence — and 'the status has not been evaluated' is the
    single most common real verdict this engine emits.
    """
    rc6 = BY_ID["RC6"]
    assert "not" in rc6["claim"].lower() and "not" in rc6["accepted_passage"].lower()
    assert S.inspect(rc6["accepted_passage"], claim=rc6["claim"],
                     must_contain=rc6["must_contain"]) is None, \
        "the guard refused a claim whose own assertion is a negation"


def t_identical_claim_and_span_is_never_refused():
    """The floor. If the document states the claim word for word, no guard may object."""
    for text in ("Member States shall bring into force the laws by 29 October 2014.",
                 "The copyright and related rights status of this Item has not been "
                 "evaluated.",
                 "No party may reproduce the work without written permission."):
        f = S.inspect(text, claim=text, must_contain=text.split()[1])
        assert f is None, f"guard refused an exact restatement: {f} — {text!r}"


def t_a_correction_is_not_a_denial():
    """"not A but B" AFFIRMS B. Found by measuring, not by thinking about grammar.

    Registry replay, 2026-08-31: the guard refused a real span reading "We find that
    these files are not static documentation but complex, difficult-to-read artifacts
    that evolve like configuration code…" — for the claim that they evolve like
    configuration code, which that sentence states. Two defects in one row: the carrier
    clause was being found by searching each clause for `must_contain`, which fails
    whenever the term ends on the punctuation the splitter just consumed; and a `but`
    boundary was being read as though it were a `;`.
    """
    span = ("We find that these files are not static documentation but complex, "
            "difficultto-read artifacts that evolve like configuration code through "
            "frequent, small additions. Our content analysis follows.")
    mc = "evolve like configuration code through frequent, small additions."
    assert "evolve like configuration code" in S._carrier(span, mc), \
        f"carrier clause is wrong: {S._carrier(span, mc)[:90]!r}"
    assert S.inspect(span, claim="agent context files evolve like configuration code "
                                 "through frequent, small additions",
                     must_contain=mc) is None, \
        "a contrastive correction was read as a denial"


def t_negators_are_function_words_not_lexical_verbs():
    """The list must stay the closed class the module claims it is.

    `fails`, `lacks`, `unable` were in it. They are lexical verbs: a product whose
    subject is failure says "fails" in true sentences. Measured as a false refusal on a
    span ending "…then fails."
    """
    for verb in ("fails", "failed", "lacks", "lacking", "unable", "nothing", "nowhere"):
        assert verb not in S._NEGATORS, \
            f"{verb!r} is a lexical verb, not a negation cue — it refuses true prose"
    for word in ("not", "no", "never", "cannot", "neither", "without", "unlike"):
        assert word in S._NEGATORS, f"the closed class lost {word!r}"


# ----------------------------------------------------------------- the invariants

def t_guard_only_demotes_never_rescues():
    """Monotone. The guard may turn GREEN into a refusal; it may never do the reverse.

    This is the constitution made executable: a semantic layer that could RESCUE a span
    the structural verifier refused would be a model authoring a verdict.
    """
    inc = instruments.document("http://rightsstatements.org/vocab/InC/1.0/")
    if not inc:
        raise AssertionError("UNMEASURABLE: InC document not on disk (seed the cache)")
    probes = [
        (None, "any claim", "terms"),                       # no passage
        ("A sentence that is nowhere in any document.", "x", "sentence"),
        ("rights-holder", "The rights-holder must be asked", "rights-holder"),
        (inc[:80], "unrelated claim about tractors", "zzz-not-present"),
    ]
    for passage, claim, mc in probes:
        off = V.verify(passage, document=inc, must_contain=mc)
        on = V.verify(passage, document=inc, must_contain=mc, claim=claim, semantic=True)
        assert not (off is not None and on is None), \
            f"the guard RESCUED a refusal: {off} -> {on} for {passage!r}"


def t_flag_off_restores_the_old_behaviour_exactly():
    """Recoverable. With the guard off, RC5 must green again — bit for bit."""
    url = "fixture://flagoff-RC5"
    claim = Claim("RC5", RC5["claim"], url, RC5["must_contain"])
    v = _with_doc(url, RC5_DOC, claim, semantic=False)
    assert v.verdict == GREEN, \
        f"guard off must reproduce the documented false GREEN, got {v.verdict}/{v.cause}"
    assert v.quoted_terms in RC5_DOC


def t_no_door_into_green_verifies_without_the_claim():
    """A guard wired into ONE of three doors tests green and ships two-thirds off.

    `judge_claim` reaches GREEN by three routes — the named source, the search loop and
    the escalation loop. This asserts the PROPERTY, not a call count: every `verify()` in
    the module passes the claim, and no route may call the locator directly and skip the
    candidate loop that the guard needs.

    An earlier version of this control counted call sites, and went red the moment the
    three sites were refactored into one correct helper. A control that fails on a fix is
    measuring the shape of the code, not the property the code has to hold.
    """
    import re as _re
    from clearance import facts as _f
    src = Path(_f.__file__).read_text()
    body = src.split("from .verify import verify", 1)[1]
        # verify() with no argument is prose about the function, not a call to it.
    calls = [m for m in _re.finditer(r"\bverify\((?!\))", body)]
    assert calls, "no verify() call sites found — this control is hollow"
    for m in calls:
        window = body[m.start():m.start() + 260]
        assert "claim=claim.text" in window, (
            f"a verify() call does not pass the claim, so no guard can fire on that "
            f"path:\n{window[:200]}")
    proposes = [m.start() for m in _re.finditer(r"locator\.propose\(", body)]
    helper = body.index("def _admissible")
    nxt = body.index("def judge_claim")
    for at in proposes:
        assert helper < at < nxt, (
            "a route calls locator.propose() outside _admissible — it takes the first "
            "span and never lets the guard ask for another")


def t_named_source_path_refuses_rc5_with_the_guard_on():
    url = "fixture://ship-RC5"
    claim = Claim("RC5", RC5["claim"], url, RC5["must_contain"])
    v = _with_doc(url, RC5_DOC, claim, semantic=True)
    assert v.verdict == UNKNOWN, f"named-source path still greens RC5: {v.verdict}"
    assert v.cause == SOURCE_SILENT, f"wrong cause for a read-and-refused doc: {v.cause}"
    assert any(c in (v.quoted_terms or "") for c in S.CODES), \
        f"the refusal does not name which guard fired: {v.quoted_terms!r}"


def t_search_path_refuses_rc5_with_the_guard_on():
    """The second door. A candidate Parallel proposes must meet the same guard."""
    from clearance import search as _search

    url = "https://rightsstatements.org/vocab/CNE/1.0/"
    saved_find, saved_doc = _search.find_sources, instruments.document

    def fake_find(**kw):
        return [_search.Candidate(url=url, title="CNE", excerpt="")]

    def fake_doc(u, fetch=False):
        return RC5_DOC if u == url else saved_doc(u, fetch=fetch)

    _search.find_sources, instruments.document = fake_find, fake_doc
    try:
        claim = Claim("RC5s", RC5["claim"], None, RC5["must_contain"])
        off = judge_claim(claim, semantic=False)
        on = judge_claim(claim, semantic=True)
    finally:
        _search.find_sources, instruments.document = saved_find, saved_doc
    assert off.verdict == GREEN, \
        f"premise broken: the search path did not green RC5 with the guard off ({off.verdict})"
    assert on.verdict == UNKNOWN, "the SEARCH path still greens RC5 with the guard on"


# ------------------------------------------------------------- keep it general

def t_guard_carries_no_site_specific_chrome():
    """Same law as the verifier: general language, never the pages we happened to fetch.

    Negation cues are a closed class of ENGLISH. 'Skip to main content' is a property of
    two websites. One belongs in a guard; the other belongs in a locator.
    """
    from clearance import locate
    src = Path(S.__file__).read_text()
    for leaked in locate._CHROME:
        assert leaked not in src, \
            f"{leaked!r} leaked into the semantic guard — it is overfitted to pages"
    for leaked in ("arxiv", "eur-lex", "rightsstatements", "europeana", "creativecommons"):
        assert leaked not in src.lower(), f"{leaked!r} — a site name inside the guard"


def t_every_check_is_separately_attributable():
    """Measurement requires attribution: 'the guard fired' is not a finding."""
    assert set(S.CHECKS) and set(S.CODES)
    for check in S.CHECKS:
        # each check can be run alone, so its own contribution is countable
        S.inspect("some text here about things", claim="a claim", must_contain="text",
                  checks=(check,))


if __name__ == "__main__":
    failed = 0
    names = [n for n in globals() if n.startswith("t_")]
    for n in sorted(names, key=lambda k: list(globals()).index(k)):
        fn = globals()[n]
        try:
            fn()
            print(f"  PASS  {n[2:].replace('_', ' ')}")
        except Exception as e:
            failed += 1
            print(f"  FAIL  {n[2:].replace('_', ' ')}\n        {type(e).__name__}: {e}")
    print(f"\n{len(names) - failed} passed, {failed} failed")
    raise SystemExit(1 if failed else 0)
