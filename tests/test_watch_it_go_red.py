"""Watch it go red.

A control is not a control until it has been seen failing. Every test here
strips something and confirms the engine refuses, rather than passes quietly.
Run: python3 tests/test_watch_it_go_red.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from clearance import corpus, engine, instruments
from clearance.verdict import (Verdict, UncitedVerdict, GREEN, RED, UNKNOWN, ASSET,
                               NO_INSTRUMENT, UNRULED, UNREAD_TERMS, NOT_EVALUATED)

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
    items = json.loads(
        (Path(__file__).resolve().parents[1] / "fixtures" /
         "europeana-film-archive.json").read_text())
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
    items = json.loads(
        (Path(__file__).resolve().parents[1] / "fixtures" /
         "europeana-broad.json").read_text())
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

    items = json.loads(
        (Path(__file__).resolve().parents[1] / "fixtures" /
         "europeana-broad.json").read_text())

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
    items = json.loads(
        (Path(__file__).resolve().parents[1] / "fixtures" /
         "europeana-broad.json").read_text())
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


print("WATCH IT GO RED — control tests\n")
for n, f in list(globals().items()):
    if n.startswith("t_"):
        check(n[2:].replace("_", " "), f)
print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
