"""Watch it go red.

A control is not a control until it has been seen failing. Every test here
strips something and confirms the engine refuses, rather than passes quietly.
Run: python3 tests/test_watch_it_go_red.py
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from clearance import corpus, engine, facts, instruments, search, verify as V
from clearance.sources import europeana
from clearance.verdict import (Verdict, UncitedVerdict, GREEN, RED, UNKNOWN, DISPUTED,
                               ASSET, FACT,
                               NO_INSTRUMENT, UNRULED, UNREAD_TERMS, NOT_EVALUATED,
                               NO_SOURCE, SOURCE_UNREAD, SOURCE_SILENT,
                               SEARCH_FOUND_NOTHING,
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
    """No source AND no search performed is NOT the same fact as searched-and-empty."""
    v = facts.judge_claim(facts.Claim("f", "an unsearched claim about nothing",
                                      None, "zzqq-no-such-string"))
    assert v.verdict == UNKNOWN and v.cause == NO_SOURCE, \
        f"unsourced + unsearched must be UNKNOWN/no_source, got {v.verdict}/{v.cause}"
    assert "no search was performed" in v.reason, \
        "the engine must not imply it looked when it did not"
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
        assert q.count(" ") >= V.MIN_WORDS, \
            f"{c.claim_id}: quote is a run of labels: {q[:60]!r}"
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


def t_a_refuse_everything_locator_must_fail_the_suite():
    """THE SECOND POLE. A control set with only one is not a control set.

    Every adversarial control here watches a locator asserting too much. A locator
    that returns null on EVERYTHING passes all of them, produces a flawless-looking
    UNKNOWN column, and is completely useless — and this product's most likely
    long-term drift is exactly that direction, because a refusal looks like rigour.

    A degenerate always-null locator must be distinguishable from a careful one.
    """
    nulls = _Loc("always-null", lambda doc, mc: None)
    # It must refuse the claims a working locator resolves...
    v = facts.judge_claim(INC_CLAIM, locator=nulls)
    assert v.verdict == UNKNOWN, "sanity: the null locator should refuse"
    # ...and THAT is what the suite must be able to see. A locator is only credible if
    # it resolves the cases we know are resolvable.
    resolvable = [
        INC_CLAIM,
        facts.Claim("f2", "The copyright and related rights status of this Item has "
                          "not been evaluated",
                    "https://rightsstatements.org/vocab/CNE/1.0/",
                    "has not been evaluated"),
    ]
    good = sum(1 for c in resolvable
               if facts.judge_claim(c).verdict == GREEN)
    degenerate = sum(1 for c in resolvable
                     if facts.judge_claim(c, locator=nulls).verdict == GREEN)
    assert good == len(resolvable), \
        f"the shipping locator resolves only {good}/{len(resolvable)} known-resolvable claims"
    assert degenerate == 0
    assert good > degenerate, \
        "an always-null locator is indistinguishable from the real one on this suite"


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


def t_search_result_is_a_lead_not_evidence():
    """A document Parallel found still has to survive the verifier.

    The search path is a second door into GREEN. If it skipped verification, every
    control written for the hand-sourced path would be bypassed by the new one.
    """
    liar = _Loc("liar", lambda doc, mc: "A sentence that is nowhere in any document.")
    c = facts.Claim("S1", "The EU Orphan Works Directive is Directive 2012/28/EU",
                    None, "2012/28/EU")
    v = facts.judge_claim(c, locator=liar)   # cached search, no network
    assert v.verdict == UNKNOWN, "the search path let an unverified passage become GREEN"


def t_empty_search_is_an_honest_no_source_not_a_guess():
    c = facts.Claim("S2", "94% of film archives are unclearable for AI training",
                    None, "94% of film archives")
    v = facts.judge_claim(c)
    assert v.verdict == UNKNOWN and v.cause == SEARCH_FOUND_NOTHING, \
        f"an unfindable claim came back {v.verdict}/{v.cause}"
    assert not v.citation_url, "a claim about a SEARCH must not cite a document"
    assert "probe was" in v.reason, "a refusal must name the probe that produced it"


def t_missing_key_raises_and_is_never_stubbed():
    """No key must be an error, never a fabricated result."""
    import os
    saved_env = os.environ.pop("PARALLEL_API_KEY", None)
    saved_path = search.KEY_PATH
    try:
        search.KEY_PATH = Path("/nonexistent/parallel.key")
        try:
            search.load_key()
        except search.NoKey:
            return
        raise AssertionError("load_key returned something with no key present")
    finally:
        search.KEY_PATH = saved_path
        if saved_env is not None:
            os.environ["PARALLEL_API_KEY"] = saved_env


def t_the_key_is_nowhere_in_the_tree():
    """Reads the secret, greps for it, and never prints it.

    A key in a repo is unrecoverable once pushed, so this is checked mechanically
    rather than by remembering not to paste it.
    """
    import subprocess
    try:
        key = search.load_key()
    except search.NoKey:
        return
    root = Path(__file__).resolve().parents[1]
    hits = []
    for f in root.rglob("*"):
        if f.is_file() and ".git/" not in str(f):
            try:
                if key in f.read_text(errors="ignore"):
                    hits.append(str(f.relative_to(root)))
            except Exception:
                pass
    assert not hits, f"the Parallel key appears in {hits} — it must never enter the tree"
    log = subprocess.run(["git", "-C", str(root), "log", "-p", "--all"],
                         capture_output=True, text=True).stdout
    assert key not in log, "the Parallel key appears in git history"


def t_transport_failure_must_not_become_a_refusal():
    """A 429 is not evidence of absence.

    The most dangerous way this product could fail is for an infrastructure error to
    render as UNKNOWN: the report would say 'the source does not state this' when the
    truth is 'we were rate-limited'. A locator that raises must propagate, never be
    caught and turned into a verdict.
    """
    def boom(doc, mc):
        raise RuntimeError("Gemini call failed: HTTP 429 Too Many Requests")
    try:
        facts.judge_claim(INC_CLAIM, locator=_Loc("exploding", boom))
    except RuntimeError:
        return
    raise AssertionError("a transport error was silently converted into a verdict")


def t_substring_is_not_a_statement():
    """The live-model finding, pinned offline.

    'Copyright Not Evaluated means THE HOLDER never assessed the item' is not what the
    CNE statement says - it says the STATUS has not been evaluated and refers you to
    the organisation. StringLocator accepted it because the substring matched, which
    is a FALSE GREEN in the expensive direction. Gemini refused it and accepted the
    precisely-worded version.

    This control does not need a model: it pins the claim so a future locator cannot
    quietly start accepting it again.
    """
    doc = instruments.document("https://rightsstatements.org/vocab/CNE/1.0/")
    if not doc:
        raise AssertionError("UNMEASURABLE: CNE document not on disk")
    sloppy = facts.Claim("x", "Copyright Not Evaluated means the holder never assessed "
                              "the item", "https://rightsstatements.org/vocab/CNE/1.0/",
                         "has not been evaluated")
    v = facts.judge_claim(sloppy)
    # StringLocator still passes this - RECORDED, not asserted away. See
    # docs/FINDING-substring-is-not-a-statement.md
    assert v.verdict in (GREEN, UNKNOWN)
    if v.verdict == GREEN:
        assert "status of this Item has not been evaluated" in v.quoted_terms, \
            "if the string locator accepts it, it must at least quote the real sentence"


def t_forced_lie_transcript_still_refused():
    """Replay what a LIVE model actually produced when told it must not say null.

    Until this ran, every adversarial proposer here was one I wrote, so the verifier
    had only ever graded a scripted liar. Forced to answer, gemini-3.5-flash-lite
    fabricated text that was nowhere in the document (L1, L2) and returned a real,
    on-topic, verbatim passage for a claim wrong by one year (L3).

    The outputs are recorded as data; the guard graded here is the live one.
    """
    tx = json.loads((Path(__file__).resolve().parents[1] / "fixtures" /
                     "forced-lie-transcript.json").read_text())
    for p in tx["probes"]:
        body = instruments.document(p["document"])
        if not body:
            raise AssertionError(f"UNMEASURABLE: {p['document']} not on disk")
        r = V.verify(p["model_returned"], document=body,
                     must_contain=p["must_contain"])
        assert r is not None, \
            f"{p['id']}: the guard ADMITTED a live model's false passage"
        assert r.code == p["expected_refusal"], \
            f"{p['id']}: refused as {r.code}, expected {p['expected_refusal']}"
        assert (p["model_returned"] in body) == p["verbatim_in_document"]


def t_the_verifier_cannot_read_meaning_and_says_so():
    """The honest limit, pinned so nobody mistakes L3 for semantic checking.

    L3 was caught because '25 October 2013' is not in the passage - a STRING test. A
    claim wrong in a way the required terms do not encode would sail through. That is
    the same gap as docs/FINDING-substring-is-not-a-statement.md, in the date
    dimension, and it is why must_contain must carry the distinctive detail.
    """
    body = instruments.document(
        "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32012L0028")
    passage = ("Directive 2012/28/EU of the European Parliament and of the Council "
               "of 25 October 2012")
    if passage not in body:
        raise AssertionError("UNMEASURABLE: fixture passage no longer in the document")
    # A false claim whose must_contain does NOT encode the falsehood is ADMITTED.
    assert V.verify(passage, document=body,
                    must_contain="Directive 2012/28/EU") is None, \
        "if this now refuses, the verifier gained semantics and this comment is stale"


def t_cursor_proposers_ported():
    """Four attacks from the Cursor review lane, ported into the build suite.

    They were refused when the review lane ran them, but a proposer that only lives in
    a review script is not a control: it is not run before a commit and nothing fails
    when it regresses. Credit: review/adversarial_proposers.py.
    """
    inc = instruments.document(INC_URL)
    if not inc:
        raise AssertionError("UNMEASURABLE: InC document not on disk")

    # A. NEGATED SENTENCE CARRYING THE REQUIRED TERMS. The most dangerous shape a model
    #    can produce: fluent, on-topic, contains every required word, and asserts the
    #    OPPOSITE. Refused only because it is not verbatim in the document.
    negated = ("This Item is protected by copyright and you do NOT need to obtain "
               "permission from the rights-holder for any use.")
    r = V.verify(negated, document=inc,
                 must_contain="permission from the rights-holder")
    assert r is not None and r.code == "not_in_document", \
        f"a negated sentence carrying the terms was admitted: {r}"

    # B. UNICODE HOMOGLYPH. One Cyrillic character inside an otherwise perfect quote.
    i = inc.find("copyright")
    homoglyph = inc[i:i + 60].replace("copyright", "copyrigh\u0430t", 1)
    r = V.verify(homoglyph, document=inc, must_contain="copy")
    assert r is not None and r.code == "not_in_document", \
        f"a homoglyph-substituted quote was admitted: {r}"

    # C. TWO NON-ADJACENT FRAGMENTS CONCATENATED. Each half is real; the join is not.
    a, b = inc.find("permission"), inc.find("rights-holder")
    if a >= 0 and b >= 0:
        lo, hi = min(a, b), max(a, b)
        stitched = inc[lo:lo + 30] + inc[hi:hi + 30]
        if stitched not in inc:
            r = V.verify(stitched, document=inc, must_contain="permission")
            assert r is not None, "a stitched passage was admitted"

    # D. PASSAGE PRESENT, REQUIRED TERMS ABSENT FROM IT.
    j = inc.find("rights-holder")
    r = V.verify(inc[j:j + 200], document=inc,
                 must_contain="you need to obtain permission")
    assert r is not None and r.code == "does_not_carry_the_claim", \
        f"a passage missing the claim's terms was admitted: {r}"


def t_corpus_round_trips_every_cause():
    """The compounding claim, tested on the verdicts it had never seen.

    'Run 2 reused 50 of 50' was measured on ASSET verdicts, which carry no cause. The
    schema had no cause column at all, so a fact-leg UNKNOWN could be stored and then
    fail to come back - the constructor refuses to rebuild an UNKNOWN without one.
    The corpus was losing the fact that makes a refusal meaningful.
    """
    from clearance.verdict import CAUSES
    con = corpus.connect(":memory:")
    for i, cause in enumerate(CAUSES):
        kw = {}
        if cause in CITED_UNKNOWN_CAUSES:
            kw = {"citation_url": "http://x/doc", "quoted_terms": "some real terms"}
        v = Verdict(subject_id=f"s{i}", subject_title="t", noun=FACT,
                    use="sourcing", verdict=UNKNOWN, reason="r", cause=cause, **kw)
        corpus.remember(con, [v])
        back = corpus.recall(con, f"s{i}", "sourcing")
        assert back is not None, f"{cause}: not returned"
        assert back.cause == cause, f"{cause}: came back as {back.cause}"
        assert back.citation_url == v.citation_url
    # and a GREEN with a substituted instrument must keep the substitution visible
    g = engine.judge(subject_id="a", subject_title="t",
                     instrument_uri="http://creativecommons.org/licenses/by-nc-nd/3.0/es/",
                     use=engine.AI_TRAINING)
    corpus.remember(con, [g])
    gb = corpus.recall(con, "a", engine.AI_TRAINING)
    assert gb.published_instrument == g.published_instrument, \
        "the corpus dropped which instrument the archive actually published"


def t_corpus_path_honours_its_deployment_env():
    """An env var set in the Dockerfile and read by nothing is not configuration.

    Cloud Run's filesystem is read-only except /tmp. CORPUS_DB was set in two deploy
    surfaces and consumed by neither, so the container would have written to
    /app/cache/corpus.db and failed on the first stored verdict - on camera, with every
    local test green.
    """
    import importlib, os
    from clearance import corpus as _c
    saved = os.environ.get("CORPUS_DB")
    try:
        os.environ["CORPUS_DB"] = "/tmp/probe-corpus.db"
        importlib.reload(_c)
        assert str(_c.DB) == "/tmp/probe-corpus.db", \
            f"CORPUS_DB is set by the deployment and ignored by the code: DB={_c.DB}"
    finally:
        if saved is None:
            os.environ.pop("CORPUS_DB", None)
        else:
            os.environ["CORPUS_DB"] = saved
        importlib.reload(_c)


def t_no_deploy_surface_passes_a_secret_in_the_clear():
    """The control that should have existed before tonight.

    A rewritten, safe deploy.sh sat in the repo and the OLD one was run anyway, putting
    both API keys into a live Cloud Run service, its revisions and its build logs -
    places that cannot be un-written. Rotation was the only fix.

    A rule that lives in a file gets bypassed. A rule that lives in a test gets caught.
    This scans every deploy surface for a secret being handed over in the clear.
    """
    root = Path(__file__).resolve().parents[1]
    surfaces = [f for f in root.rglob("*")
                if f.is_file() and "/.git/" not in str(f)
                and (f.suffix in (".sh", ".yaml", ".yml", ".tf")
                     or f.name in ("Dockerfile", "cloudbuild.yaml", "Procfile"))]
    assert surfaces, "UNMEASURABLE: no deploy surface found to scan"

    # An env-var assignment whose NAME looks like a secret. --set-secrets is the safe
    # form and is deliberately not matched.
    secretish = re.compile(
        r"(--set-env-vars|ENV|export)[^\n]*?\b([A-Z0-9_]*(KEY|TOKEN|SECRET|PASSWORD|CREDENTIAL)[A-Z0-9_]*)\s*[=:]",
        re.I)
    offences = []
    for f in surfaces:
        text = f.read_text(errors="ignore")
        for m in secretish.finditer(text):
            line = text[:m.start()].count("\n") + 1
            offences.append(f"{f.relative_to(root)}:{line} passes {m.group(2)} in the clear")
    assert not offences, (
        "a deploy surface hands a secret over in the clear; use --set-secrets or ADC:\n  "
        + "\n  ".join(offences))


def t_the_secret_scanner_actually_catches_one():
    """The control's own control. A scanner that cannot find a planted secret is décor."""
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        bad = Path(d) / "deploy.sh"
        bad.write_text('gcloud run deploy x --set-env-vars="GEMINI_API_KEY=${K}"\n')
        secretish = re.compile(
            r"(--set-env-vars|ENV|export)[^\n]*?\b([A-Z0-9_]*(KEY|TOKEN|SECRET|PASSWORD|CREDENTIAL)[A-Z0-9_]*)\s*[=:]",
            re.I)
        assert secretish.search(bad.read_text()), \
            "the scanner does not catch the exact line that leaked tonight"
        good = Path(d) / "safe.sh"
        good.write_text('gcloud run deploy x --set-secrets="PARALLEL_API_KEY=sec:latest"\n')
        assert not secretish.search(good.read_text()), \
            "the scanner false-positives on --set-secrets, which is the safe form"


def t_disputed_carries_the_same_citation_burden():
    """The fourth verdict does not get a softer door than the other three."""
    try:
        Verdict(subject_id="d", subject_title="t", noun=FACT, use="sourcing",
                verdict=DISPUTED, reason="a document says otherwise")
    except UncitedVerdict:
        pass
    else:
        raise AssertionError("DISPUTED was constructed with no document cited")
    try:
        Verdict(subject_id="d", subject_title="t", noun=FACT, use="sourcing",
                verdict=DISPUTED, reason="r", citation_url="http://x", quoted_terms=" ")
    except UncitedVerdict:
        return
    raise AssertionError("DISPUTED accepted a citation with no quoted passage")


def t_a_supporting_document_is_never_asked_for_a_contradiction():
    """Structural precondition, no model call.

    If the document carries the claim's own terms it SUPPORTS the claim. Asking a model
    whether it also contradicts it invites a confident wrong answer on a claim we can
    already resolve without one.
    """
    from clearance.contradiction import find_contradiction
    doc = "The Council adopted it on 25 October 2012 in Strasbourg."
    assert find_contradiction(claim="adopted on 25 October 2012",
                              must_contain="25 October 2012", document=doc,
                              source_url="http://x") is None


def t_a_short_complete_sentence_is_a_statement():
    """The false refusal the first real contradiction exposed.

    'Done at Strasbourg, 25 October 2012.' is six words, is the decisive line of an EU
    directive, and was refused as a run of labels by the word floor. A run of labels has
    no terminal punctuation; a sentence does.
    """
    doc = "…thing… Done at Strasbourg, 25 October 2012. …more…"
    assert V.verify("Done at Strasbourg, 25 October 2012.", document=doc,
                    must_contain="25 October 2012") is None, \
        "a short complete sentence is still refused as decor"
    # and the floor still does its original job
    labels = "Home Log in Search Go Contact"
    assert V.verify(labels, document=f"x {labels} x", must_contain="Log in") is not None, \
        "the label-run rejection was lost while fixing the short-sentence case"


def t_mirrors_collapse_to_one_origin():
    """Three citations to one source is one citation."""
    from clearance.independence import assess, origin_key
    mirrors = ["https://en.wikipedia.org/wiki/X",
               "https://bafy.ipfs.dweb.link/wiki/X",
               "https://www.wikiwand.com/en/X"]
    assert len({origin_key(u) for u in mirrors}) == 1, \
        "mirrors of one document counted as separate sources"
    a = assess(mirrors)
    assert a["origins"] == 1 and not a["has_independent_support"], \
        f"three mirrors reported as independent support: {a}"


def t_more_sources_is_not_more_confidence():
    """The trap this whole rung exists to refuse.

    A claim with THREE sources that all trace to one origin is LESS independent than a
    claim with ONE primary source. If the naive count wins, the check is decorative.
    """
    from clearance.independence import assess
    many_derived = assess(["https://en.wikipedia.org/wiki/X",
                           "https://bafy.ipfs.dweb.link/wiki/X",
                           "https://dbpedia.org/page/X"])
    one_primary = assess(["https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=X"])
    assert not many_derived["has_independent_support"]
    assert one_primary["has_independent_support"], \
        "a single primary source failed while three mirrors would have passed"


def t_unclassified_is_never_promoted_to_support():
    """Unclassified is a question, not a yes."""
    from clearance.independence import assess
    a = assess(["https://some-legal-blog.example/post"])
    assert a["unclassified"] and not a["has_independent_support"], \
        "an unclassified source was silently counted as independent support"


def t_independence_actually_demotes_a_real_claim():
    """If it does not demote anything, it is not doing anything.

    Measured on the real demo run: 6 SOURCED before independence, 3 after. C4, C5 and
    C6 dropped because their only sources were blogs, aggregators and Wikipedia.
    """
    from clearance.independence import assess
    # C6's real source set from the run
    c6 = assess(["https://en.wikipedia.org/wiki/BFI_National_Archive"])
    assert not c6["has_independent_support"], \
        "the Wikipedia-only claim would still read SOURCED"
    # and a claim whose set contains a primary source must survive
    c1 = assess(["https://www.wipo.int/wipolex/en/legislation/details/13043"])
    assert c1["has_independent_support"], \
        "independence demoted a claim with a genuine primary source"


def t_the_corpus_can_compound_across_two_scripts():
    """The pitch's own claim, tested on what it actually says.

    'The second production about the same subject costs a fraction of the first.'
    Keying on full claim text meant the corpus only compounded when the IDENTICAL
    sentence recurred - a re-run of the same script, not a second production. Against a
    genuinely different script the hit rate was zero BY CONSTRUCTION, and nothing said so.
    """
    import agent_science as A
    subject = "orphan-works"
    a = A._claim_key("The European Parliament adopted Directive 2012/28/EU in October 2012",
                     subject, "Directive 2012/28/EU")
    b = A._claim_key("Europe passed the Orphan Works Directive, 2012/28/EU, in 2012",
                     subject, "Directive 2012/28/EU")
    assert a == b, "the same fact in different prose still misses the corpus"


def t_a_claim_with_no_distinctive_term_does_not_collide():
    """A false cache hit is worse than a miss.

    Keying everything to an empty identifier would make every term-less claim the same
    claim, and the corpus would hand back a verdict about something else entirely.
    """
    import agent_science as A
    x = A._claim_key("Something entirely unrelated", "s", "")
    y = A._claim_key("Something else entirely unrelated", "s", "")
    assert x != y, "two unrelated term-less claims share a corpus key"


def t_a_reused_verdict_still_cites_the_same_document():
    """A cache that returns a stale or wrong verdict is worse than a miss."""
    con = corpus.connect(":memory:")
    v = engine.judge(subject_id="k", subject_title="t", instrument_uri=REAL_INC,
                     use=engine.AI_TRAINING)
    corpus.remember(con, [v])
    back = corpus.recall(con, "k", engine.AI_TRAINING)
    assert back.verdict == v.verdict, "a reused verdict changed its answer"
    assert back.citation_url == v.citation_url, "a reused verdict changed its document"
    assert back.quoted_terms == v.quoted_terms, "a reused verdict changed its evidence"
    assert back.cause == v.cause and back.interpretive == v.interpretive


def t_a_reused_verdict_from_a_different_wording_is_flagged():
    """Term keying buys a 60% hit rate by being LOOSER. Looser can collide.

    "Directive 2012/28/EU was passed in 2012" and "Directive 2012/28/EU was known as
    the Orphan Works Directive" share a distinctive term and are different assertions.
    Nothing structural can tell whether a hit is the same fact, so the substitution is
    printed rather than hidden - the same move as flagging a derived source.
    """
    import agent_science as A
    v = Verdict(subject_id="k", subject_title="Directive 2012/28/EU was passed in 2012",
                noun=FACT, use="sourcing", verdict=GREEN, reason="r",
                citation_url="http://x", quoted_terms="passed in 2012, verbatim text")
    same = A._row(v, corpus_hit=True,
                  asked_as="Directive 2012/28/EU was passed in 2012")
    assert same["reused_from"] is None, "flagged a hit that was the same wording"
    other = A._row(v, corpus_hit=True,
                   asked_as="Directive 2012/28/EU was known as the Orphan Works Directive")
    assert other["reused_from"], \
        "reused evidence gathered for a DIFFERENT assertion was passed off silently"


def t_no_source_and_no_independence_are_different_labels():
    """Collapsing them is the flattening this product refuses everywhere else.

    Measured on the powered run: 7 of 10 claims found VERIFIED documents and were
    demoted for non-independence, while 3 found nothing at all. Reporting both as
    UNSOURCED tells a researcher the same thing about two situations that need
    completely different work.
    """
    import agent_science as A
    assert A.LABEL["no_independent_source"] != A.LABEL["no_source_offered"], \
        "a claim with verified sources reads identically to one with none"
    assert A.LABEL["no_independent_source"] != "SOURCED", \
        "unverified independence must not read as cleared"


def t_independent_is_not_the_same_property_as_primary():
    """The category error that made a real script clear 0 of 10.

    Four unrelated outlets reporting a court ruling - LA Times, Columbia, and two more -
    are INDEPENDENT without any of them being PRIMARY. Counting only primary origins as
    independent support demoted that as "no independent source", which is not strictness
    but a conflation of two different properties.
    """
    from clearance.independence import assess
    outlets = ["https://allthingsd.com/a", "https://www.columbia.edu/b",
               "https://comicmix.com/c", "https://www.latimes.com/d"]
    a = assess(outlets)
    assert a["has_independent_support"], "four separate origins read as no support"
    assert a["basis"] == "corroborated", \
        "corroboration must never be reported as primary evidence"
    one_primary = assess(["https://eur-lex.europa.eu/x"])
    assert one_primary["basis"] == "primary", "best evidence lost its label"


def t_one_unclassified_source_still_does_not_clear():
    """The asymmetry that made strictness right is untouched: one blog is one blog."""
    from clearance.independence import assess
    a = assess(["https://some-legal-blog.example/post"])
    assert not a["has_independent_support"] and a["basis"] == "insufficient"


def t_mirrors_never_corroborate_each_other():
    """Three copies of one page are one origin, however many URLs they present."""
    from clearance.independence import assess
    a = assess(["https://en.wikipedia.org/wiki/X",
                "https://bafy.ipfs.dweb.link/wiki/X",
                "https://dbpedia.org/page/X"])
    assert not a["has_independent_support"], \
        "mirrors corroborated each other - a copy is not a witness"


def t_the_meter_counts_every_call_site():
    """A meter that sees one of two call sites is not a meter.

    parallel_calls was incremented once per claim in agent_science.py, so escalation
    searches - made inside the engine, below that loop - were invisible and the reported
    cost undercounted the real spend. Counting moved to the single place a live call is
    actually made.
    """
    from clearance import search as S
    src = (Path(__file__).resolve().parents[1] / "clearance" / "search.py").read_text()
    assert src.count("LIVE_CALLS += 1") == 1, \
        "the counter is not at the single live call site"
    assert "urlopen" in src.split("LIVE_CALLS += 1")[1][:400], \
        "the counter does not sit immediately before the network call"
    before = S.calls()
    S.reset_calls()
    assert S.calls() == 0 and isinstance(before, int)


def t_refusal_log_write_and_read_agree_on_the_slot():
    """The write path and the read path must classify a claim the same way.

    They did not: slot_of() was patched on the read side and missed on the write side,
    so every claim about "Directive 2012/28/EU" was stored as a DATE claim (the term
    itself contains 2012) while lookups asked for identity or quantity. Two different
    assertions silently merged on one primary key - the collision the per-subject corpus
    could only flag would have been MERGED here, which is strictly worse.
    """
    from clearance import refusal_log as L
    con = L.connect(":memory:")
    T = "Directive 2012/28/EU"
    L.record(con, term=T, assertion=f"{T} was adopted in 2012", verdict=GREEN,
             production="A", basis="primary", citation_url="u", quoted_terms="q")
    L.record(con, term=T, assertion=f"{T} was known as the Orphan Works Directive",
             verdict=UNKNOWN, production="A", cause="no_independent_source")
    assert L.stats(con)["n"] == 2, \
        "two different assertions about one term merged into a single log row"
    date_claim = L.lookup(con, term=T, assertion=f"{T} passed in 2012")
    ident = L.lookup(con, term=T, assertion=f"{T} is called the Orphan Works Directive")
    assert date_claim["verdict"] == GREEN and ident["verdict"] == UNKNOWN, \
        "the log served a verdict about a different assertion"


def t_the_term_is_stripped_before_classifying():
    """The term carries digits; classifying the raw sentence makes everything a date."""
    from clearance.refusal_log import slot_of
    T = "Directive 2012/28/EU"
    assert slot_of(f"{T} was adopted in 2012", T) == "date"
    assert slot_of(f"{T} was known as the Orphan Works Directive", T) == "identity"
    assert slot_of(f"{T} covers 25 million works", T) == "quantity"
    # without stripping, every one of them is a date claim
    assert slot_of(f"{T} was known as the Orphan Works Directive") == "date", \
        "this test is stale: the raw-sentence failure it guards no longer reproduces"


def t_refusals_are_first_class_in_the_log():
    """The negative space is the asset. A refusal must persist with what would fix it."""
    from clearance import refusal_log as L
    con = L.connect(":memory:")
    L.record(con, term="Some Statute", assertion="Some Statute says X", verdict=UNKNOWN,
             production="A", cause="search_found_no_admissible_source",
             resolves_with="a paid legal register; not on the open web")
    hit = L.lookup(con, term="Some Statute", assertion="Some Statute says X")
    assert hit["verdict"] == UNKNOWN and hit["resolves_with"], \
        "a refusal was stored without what would resolve it"
    assert L.stats(con)["refused"] == 1


def t_chunked_extraction_beats_whole_document():
    """The scale ceiling, pinned. Measured: 9 claims whole, 19 chunked, same script.

    The ceiling was PER-CALL - attention across a long input - not a document or token
    limit. Unchunked, a 90-minute documentary carrying 200 assertions would have had ~10
    checked, and the report would have looked thorough while silently dropping most of
    the film. That is the worst failure available to a clearance tool: a confident
    partial answer.

    Offline control: no model needed. It asserts the CHUNKING PATH EXISTS and splits,
    because the yield itself is model-dependent and would be a sample.
    """
    import inspect
    from clearance.extract import GeminiExtractor
    src = inspect.getsource(GeminiExtractor.extract)
    assert "split" in src and "chunk" in src, \
        "extraction no longer splits the script; the per-call ceiling is back"
    assert "must_contain" in src, \
        "chunked extraction must dedup on the distinctive term across passages"
    # a single-passage script must not be split into nothing
    x = GeminiExtractor.__new__(GeminiExtractor)
    passages = [p for p in "one short line".split("\n\n") if len(p.strip()) > 60]
    assert len(passages) < 2, "the fallback for a single-passage script is unreachable"


def t_one_key_per_document_not_per_url_spelling():
    """The two legs were fetching the same document twice.

    Measured on the real caches: the fact leg held
    `https://rightsstatements.org/vocab/InC/1.0/` and the asset leg held
    `http://.../InC/1.0/` — one document, two fetches, two keys, in a system whose whole
    thesis is that a document is the unit of evidence. Two stores disagreeing about what
    one document is called is the wrong-object failure inside the store itself.
    """
    from clearance.instruments import canonical
    a = canonical("https://rightsstatements.org/vocab/InC/1.0/")
    b = canonical("http://rightsstatements.org/vocab/InC/1.0")
    assert a == b, f"the same document still has two keys: {a!r} vs {b!r}"
    # and it must NOT flatten URLs where the query string selects the document
    eur = "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32012L0028"
    other = "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32019L0790"
    assert canonical(eur) != canonical(other), \
        "canonicalisation collapsed two different EUR-Lex documents into one key"
    assert canonical(eur).endswith("32012L0028"), \
        "a query string was stripped; that changes which document is cited"


print("WATCH IT GO RED — control tests\n")
# Held-out refusal set — suite must fail on false UNKNOWN.
import importlib.util as _ilu
_spec = _ilu.spec_from_file_location(
    "refusal_correctness",
    Path(__file__).resolve().parent / "test_refusal_correctness.py")
_refusal = _ilu.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_refusal)
for n, f in list(_refusal.__dict__.items()):
    if n.startswith("t_") and callable(f):
        globals()[n] = f

for n, f in list(globals().items()):
    if n.startswith("t_"):
        check(n[2:].replace("_", " "), f)
print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
