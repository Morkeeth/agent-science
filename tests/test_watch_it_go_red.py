"""Watch it go red.

A control is not a control until it has been seen failing. Every test here
strips something and confirms the engine refuses, rather than passes quietly.
Run: python3 tests/test_watch_it_go_red.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from clearance import corpus, engine, facts, instruments, verify as V
from clearance.sources import europeana
from clearance.verdict import (Verdict, UncitedVerdict, GREEN, RED, UNKNOWN, ASSET, FACT,
                               NO_INSTRUMENT, UNRULED, UNREAD_TERMS, NOT_EVALUATED,
                               NO_SOURCE, SOURCE_UNREAD, SOURCE_SILENT,
                               CITED_UNKNOWN_CAUSES)

REAL_INC = "http://rightsstatements.org/vocab/InC/1.0/"
passed, failed = 0, 0


def check(name, fn):
    global passed, failed
    try:
        fn()
        print(f"  PASS  {name}")
        passed += 1
    except AssertionError as e:
        print(f"  FAIL  {name}\n        {e}")
        failed += 1


def t_red_is_real():
    v = engine.judge(subject_id="/2051904/data_euscreenXL_1252769",
                     subject_title="The Film Archive in Berlin",
                     instrument_uri=REAL_INC, use=engine.AI_TRAINING,
                     holder="Deutsche Welle")
    assert v.verdict == RED, f"expected RED, got {v.verdict}"
    assert v.citation_url == REAL_INC, "RED must cite the instrument"
    assert "protected by copyright" in v.quoted_terms, \
        f"RED must quote the real instrument, got {v.quoted_terms!r}"


def t_no_instrument_is_unknown_not_green():
    v = engine.judge(subject_id="x", subject_title="orphan reel",
                     instrument_uri=None, use=engine.AI_TRAINING)
    assert v.verdict == UNKNOWN, f"missing instrument must be UNKNOWN, got {v.verdict}"
    assert v.cause == NO_INSTRUMENT, "an UNKNOWN must say WHOSE gap it is"
    assert v.citation_url is None


def t_unrecognised_instrument_is_unknown():
    v = engine.judge(subject_id="x", subject_title="odd licence",
                     instrument_uri="http://example.com/some-licence",
                     use=engine.AI_TRAINING)
    assert v.verdict == UNKNOWN, f"unruled instrument must be UNKNOWN, got {v.verdict}"
    assert v.cause == UNRULED, "our own missing coverage must not be billed to the archive"


def t_ruled_but_never_fetched_is_unknown():
    """Strip the evidence, keep the rule: the engine must stop asserting."""
    real = instruments._load()
    try:
        instruments._save({k: v for k, v in real.items() if k != REAL_INC})
        v = engine.judge(subject_id="x", subject_title="t",
                         instrument_uri=REAL_INC, use=engine.AI_TRAINING)
        assert v.verdict == UNKNOWN, \
            f"a rule without fetched terms must yield UNKNOWN, got {v.verdict}"
        assert "never been fetched" in v.reason
        assert v.cause == UNREAD_TERMS
    finally:
        instruments._save(real)


def t_cannot_construct_uncited_verdict():
    for kwargs in (
        dict(verdict=RED, citation_url=None, quoted_terms=None),
        dict(verdict=GREEN, citation_url="http://x", quoted_terms=""),
        dict(verdict=UNKNOWN, citation_url="http://x", quoted_terms="terms",
             cause=NO_INSTRUMENT),
    ):
        try:
            Verdict(subject_id="x", subject_title="t", noun=ASSET,
                    use="ai_training", reason="r", **kwargs)
        except UncitedVerdict:
            continue
        raise AssertionError(f"constructed an illegal verdict: {kwargs}")


def t_nd_is_flagged_as_interpretation():
    v = engine.judge(subject_id="x", subject_title="t",
                     instrument_uri="http://creativecommons.org/licenses/by-nd/4.0/",
                     use=engine.AI_TRAINING)
    assert v.verdict == RED and v.interpretive, \
        "ND->training is our legal reading and must be flagged interpretive"


def t_corpus_compounds():
    con = corpus.connect(":memory:")
    v = engine.judge(subject_id="s1", subject_title="t", instrument_uri=REAL_INC,
                     use=engine.AI_TRAINING)
    corpus.remember(con, [v])
    again = corpus.recall(con, "s1", engine.AI_TRAINING)
    assert again is not None and again.verdict == RED, "corpus must return the verdict"
    assert again.quoted_terms == v.quoted_terms, "corpus must preserve the citation"
    assert corpus.recall(con, "s1", engine.BROADCAST) is None, \
        "a verdict for one use must not be reused for another"


def t_every_real_item_gets_a_cited_or_unknown_verdict():
    items = europeana.load_fixture("europeana-film-archive.json")
    for it in items:
        v = engine.judge(subject_id=it["subject_id"], subject_title=it["subject_title"],
                         instrument_uri=it["instrument_uri"], use=engine.AI_TRAINING)
        if v.verdict != UNKNOWN:
            assert v.quoted_terms, f"{it['subject_id']} asserted without terms"


def t_cne_is_unknown_but_cited():
    """The holder saying "not evaluated" is evidence of absence, not absence of evidence."""
    v = engine.judge(subject_id="x", subject_title="t",
                     instrument_uri=engine.CNE, use=engine.AI_TRAINING)
    assert v.verdict == UNKNOWN and v.cause == NOT_EVALUATED, \
        f"CNE must be UNKNOWN/not-evaluated, got {v.verdict}/{v.cause}"
    assert v.citation_url == engine.CNE, "CNE is the one UNKNOWN that carries a citation"
    assert "has not been evaluated" in (v.quoted_terms or ""), \
        f"CNE must quote its OWN clause, not page boilerplate: {v.quoted_terms!r:.90}"


def t_not_evaluated_REQUIRES_a_citation():
    """The required direction, watched going red — not just the forbidden one."""
    try:
        Verdict(subject_id="x", subject_title="t", noun=ASSET, use="ai_training",
                verdict=UNKNOWN, reason="r", cause=NOT_EVALUATED)
    except UncitedVerdict:
        pass
    else:
        raise AssertionError(
            "holder_states_not_evaluated was constructed with no citation — "
            "the narrow permission has become a general one")
    # and the same in the half-evidenced case
    try:
        Verdict(subject_id="x", subject_title="t", noun=ASSET, use="ai_training",
                verdict=UNKNOWN, reason="r", cause=NOT_EVALUATED,
                citation_url="http://x", quoted_terms="  ")
    except UncitedVerdict:
        return
    raise AssertionError("a citation with no quoted terms was accepted")


def t_cne_never_read_degrades_to_unread_not_to_a_claim():
    """Strip the CNE terms: it must fall back to UNREAD_TERMS, not assert non-evaluation."""
    real = instruments._load()
    try:
        instruments._save({k: v for k, v in real.items() if k != engine.CNE})
        v = engine.judge(subject_id="x", subject_title="t",
                         instrument_uri=engine.CNE, use=engine.AI_TRAINING)
        assert v.cause == UNREAD_TERMS, \
            f"unread CNE must not claim the holder said anything, got cause={v.cause}"
    finally:
        instruments._save(real)


def t_orphan_work_is_red_with_its_own_reason():
    v = engine.judge(subject_id="x", subject_title="t",
                     instrument_uri="http://rightsstatements.org/vocab/InC-OW-EU/1.0/",
                     use=engine.COMMERCIAL)
    assert v.verdict == RED and "orphan" in v.reason.lower()


def t_versioned_licence_quotes_its_own_page():
    """3.0/es must quote the Spanish page it published, not the 4.0 English sibling."""
    uri = "http://creativecommons.org/licenses/by-nc-nd/3.0/es/"
    v = engine.judge(subject_id="x", subject_title="t", instrument_uri=uri,
                     use=engine.AI_TRAINING)
    assert v.verdict == RED
    assert not v.substituted, \
        f"quoted {v.citation_url} while archive published {v.published_instrument}"


def t_nc_nd_keeps_both_terms():
    v = engine.judge(subject_id="x", subject_title="t",
                     instrument_uri="http://creativecommons.org/licenses/by-nc-nd/4.0/",
                     use=engine.AI_TRAINING)
    assert "NoDerivatives" in v.reason, \
        f"aliasing NC-ND to NC silently drops a term: {v.reason!r}"


def t_no_verdict_quotes_a_document_it_did_not_read():
    """Across the whole real corpus: citation_url is always where the terms came from."""
    items = europeana.load_fixture("europeana-broad.json")
    bad = []
    for it in items:
        v = engine.judge(subject_id=it["subject_id"], subject_title=it["subject_title"],
                         instrument_uri=it["instrument_uri"], use=engine.AI_TRAINING)
        if v.substituted:
            bad.append((v.published_instrument, v.citation_url))
    assert not bad, f"{len(bad)} verdicts quote a sibling document, e.g. {bad[0]}"


def t_second_question_touches_no_network():
    """The compounding claim, enforced.

    If answering a NEW question about an ALREADY-INDEXED library reaches the network,
    then the corpus is a cache that misses, not a memory that compounds, and the
    'second production costs a fraction' line in the pitch is false.
    """
    import urllib.request

    items = europeana.load_fixture("europeana-broad.json")

    calls = []
    real_urlopen = urllib.request.urlopen

    def tripwire(*a, **kw):
        calls.append(a[0] if a else "?")
        raise AssertionError("network touched while answering a second question")

    urllib.request.urlopen = tripwire
    try:
        for use in engine.USES:
            for it in items:
                engine.judge(subject_id=it["subject_id"],
                             subject_title=it["subject_title"],
                             instrument_uri=it["instrument_uri"], use=use)
    finally:
        urllib.request.urlopen = real_urlopen
    assert not calls, f"{len(calls)} network call(s), first was {calls[0]}"


def t_the_second_question_actually_splits_the_library():
    """A second use case that changes nothing is not a second use case."""
    items = europeana.load_fixture("europeana-broad.json")
    a = {}
    b = {}
    for it in items:
        for use, sink in ((engine.AI_TRAINING, a), (engine.NONCOMMERCIAL_REUSE, b)):
            sink[it["subject_id"]] = engine.judge(
                subject_id=it["subject_id"], subject_title=it["subject_title"],
                instrument_uri=it["instrument_uri"], use=use).verdict
    moved = sum(1 for k in a if a[k] != b[k])
    assert moved / len(a) > 0.10, \
        f"only {moved}/{len(a)} items change verdict — the two buyers are one buyer"


def t_fact_and_asset_are_the_same_record():
    """The claim both trees assert and neither demonstrated. One class, one guard."""
    a = engine.judge(subject_id="a", subject_title="t", instrument_uri=REAL_INC,
                     use=engine.AI_TRAINING)
    f = facts.judge_claim(facts.Claim(
        "f", "An 'In Copyright' item requires permission from the rights-holder",
        "https://rightsstatements.org/vocab/InC/1.0/",
        "you need to obtain permission from the rights-holder"))
    assert type(a) is type(f) is Verdict, "two legs must not mean two classes"
    assert a.noun == ASSET and f.noun == FACT
    assert f.verdict == GREEN and f.citation_url and f.quoted_terms


def t_fact_leg_did_not_get_its_own_softer_guard():
    """A sourced fact with no citation must raise from the SAME constructor."""
    try:
        Verdict(subject_id="f", subject_title="t", noun=FACT, use="sourcing",
                verdict=GREEN, reason="the source states it")
    except UncitedVerdict:
        pass
    else:
        raise AssertionError("the FACT noun was given a relaxed path")
    # and the cited-UNKNOWN rule applies to the fact leg too
    try:
        Verdict(subject_id="f", subject_title="t", noun=FACT, use="sourcing",
                verdict=UNKNOWN, reason="read it, silent", cause=SOURCE_SILENT)
    except UncitedVerdict:
        return
    raise AssertionError("source_does_not_state_it was accepted with no document cited")


def t_unsourced_claim_is_unknown_with_the_right_cause():
    v = facts.judge_claim(facts.Claim("f", "94% of film archives are unclearable",
                                      None, "94%"))
    assert v.verdict == UNKNOWN and v.cause == NO_SOURCE, \
        f"an unsourced claim must be UNKNOWN/no_source, got {v.verdict}/{v.cause}"
    assert not v.citation_url


def t_silent_source_does_not_quote_furniture():
    """Quoting page navigation under the heading 'evidence' reads as evidence."""
    v = facts.judge_claim(facts.Claim(
        "f", "The Orphan Works Directive permits commercial use by cultural institutions",
        "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32012L0028",
        "commercial use is permitted"))
    if v.cause == SOURCE_UNREAD:
        return  # nothing fetched in this environment; nothing to assert
    assert v.cause == SOURCE_SILENT
    q = v.quoted_terms or ""
    assert "characters read;" in q, \
        f"a non-finding must be a stated fact about the document: {q!r:.90}"
    body = instruments.document(
        "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32012L0028")
    assert q not in (body or ""), \
        "the non-finding is an excerpt of the document, which reads as evidence"


def t_cited_unknown_set_is_closed():
    assert set(CITED_UNKNOWN_CAUSES) == {NOT_EVALUATED, SOURCE_SILENT}, \
        "the required-citation set grew; each member must be added deliberately"


def t_green_evidence_carries_the_claim():
    """The fix that went where I was looking.

    The furniture fix landed on the UNKNOWN branch only; the GREEN branch three
    lines down in the same report still printed navigation chrome under the word
    "evidence". A GREEN quoting furniture is worse than an UNKNOWN doing it: it is
    the product asserting a claim is sourced while showing text that does not
    source it.
    """
    from check_pitch import CLAIMS
    # Bound to the LIVE list, not a hand-copied one. A test carrying its own copy of
    # a shipping constant grades a frozen snapshot: add a string to locate._CHROME
    # tomorrow, let it leak into a quote, and this stays green.
    from clearance.locate import _CHROME as chrome
    checked = 0
    for c in CLAIMS:
        v = facts.judge_claim(c)
        if v.verdict != GREEN:
            continue
        checked += 1
        q = v.quoted_terms or ""
        assert c.must_contain in q, \
            f"{c.claim_id}: GREEN quote does not contain the claim's own terms"
        assert q[:1].isalnum() or q[:1] in "\"'(", \
            f"{c.claim_id}: quote starts mid-word or on punctuation: {q[:40]!r}"
        assert q.count(" ") >= 6, f"{c.claim_id}: quote is a run of labels: {q[:60]!r}"
        for ch in chrome:
            assert ch not in q, \
                f"{c.claim_id}: navigation text printed as evidence ({ch!r}): {q[:80]!r}"
    assert checked >= 3, f"only {checked} GREEN claims exercised this control"


def t_a_string_in_navigation_is_not_a_source():
    """If the only occurrence is chrome, refuse the GREEN rather than quote it."""
    body = ("Skip to main content Log in My EUR-Lex Hide table of contents "
            "All consolidated versions 2012/28/EU Select Display Text")
    from clearance.locate import StringLocator
    got = StringLocator().propose(claim="c", must_contain="2012/28/EU", document=body)
    assert got is None, \
        f"a match sitting only in navigation yielded a quotable passage: {got!r:.60}"


# ---------------------------------------------------------------------------
# Adversarial proposers. A locator is UNTRUSTED by design, so the verifier is only
# real if it has been watched refusing a locator that lies. These are the failures a
# model will actually produce - fluent text that is not in the document, and a real
# passage from the wrong one.
# ---------------------------------------------------------------------------
INC_URL = "https://rightsstatements.org/vocab/InC/1.0/"
INC_CLAIM = facts.Claim("f", "An 'In Copyright' item requires permission",
                        INC_URL, "you need to obtain permission from the rights-holder")


class _Loc:
    def __init__(self, name, fn):
        self.name, self._fn = name, fn

    def propose(self, *, claim, must_contain, document):
        return self._fn(document, must_contain)


def _judged_by(fn, name="adversarial", claim=None):
    return facts.judge_claim(claim or INC_CLAIM, locator=_Loc(name, fn))


def t_hallucinated_passage_is_refused():
    """Fluent, plausible, correct-sounding, and not in the document."""
    fake = ("This Item is in the public domain and you need to obtain permission "
            "from the rights-holder only for commercial reuse in the EU.")
    v = _judged_by(lambda doc, mc: fake)
    assert v.verdict == UNKNOWN, "a hallucinated passage became a GREEN"
    assert "not_in_document" in v.reason, v.reason


def t_real_passage_from_the_wrong_document_is_refused():
    """The substitution defect, arriving from the direction a model produces it."""
    other = instruments.document("https://rightsstatements.org/vocab/CNE/1.0/")
    if not other:
        return
    i = other.find("has not been evaluated")
    lifted = other[max(0, i - 80):i + 60]
    v = _judged_by(lambda doc, mc: lifted)
    assert v.verdict == UNKNOWN, "a passage from another document became a GREEN"
    assert "not_in_document" in v.reason, v.reason


def t_passage_that_does_not_carry_the_claim_is_refused():
    """In the document, verbatim, and about something else entirely."""
    def near_miss(doc, mc):
        i = doc.find(mc)
        return doc[i + len(mc):i + len(mc) + 220]
    v = _judged_by(near_miss)
    assert v.verdict == UNKNOWN, "a passage missing the claim's own terms became GREEN"
    assert "does_not_carry_the_claim" in v.reason, v.reason


def t_whole_page_is_refused():
    """Technically contains everything; evidences nothing."""
    v = _judged_by(lambda doc, mc: doc)
    assert v.verdict == UNKNOWN, "the entire document was accepted as a quote"
    assert "not_a_statement" in v.reason, v.reason


def t_midword_slice_is_refused():
    def midword(doc, mc):
        i = doc.find(mc)
        return doc[i - 3:i + len(mc) + 120]
    v = _judged_by(midword)
    assert v.verdict == UNKNOWN or v.quoted_terms[0].isalnum(), \
        f"a mid-word slice was accepted: {v.quoted_terms[:40]!r}"


def t_a_good_locator_still_passes():
    """The verifier must not refuse everything — that is the false-UNKNOWN direction."""
    v = facts.judge_claim(INC_CLAIM)
    assert v.verdict == GREEN, \
        f"the string locator's real passage was refused: {v.reason}"
    assert v.quoted_terms in instruments.document(INC_URL)


def t_verifier_carries_no_site_specific_chrome_list():
    """The guard must hold on the third website, not just the two we fetched."""
    from clearance import locate, verify as _v
    src = Path(_v.__file__).read_text()
    # Every string the locator overfits to, read from the locator itself. Hardcoding
    # the list here would let a NEW chrome string leak into the guard unnoticed.
    for leaked in locate._CHROME:
        assert leaked not in src, \
            f"{leaked!r} leaked into the verifier — it is overfitted to specific pages"
    assert len(locate._CHROME) >= 5, "the live chrome list vanished; this control is hollow"


print("WATCH IT GO RED — control tests\n")
for n, f in list(globals().items()):
    if n.startswith("t_"):
        check(n[2:].replace("_", " "), f)
print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
