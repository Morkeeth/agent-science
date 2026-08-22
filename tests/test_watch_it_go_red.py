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
from clearance.verdict import Verdict, UncitedVerdict, GREEN, RED, UNKNOWN, ASSET

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
    assert v.citation_url is None


def t_unrecognised_instrument_is_unknown():
    v = engine.judge(subject_id="x", subject_title="odd licence",
                     instrument_uri="http://example.com/some-licence",
                     use=engine.AI_TRAINING)
    assert v.verdict == UNKNOWN, f"unruled instrument must be UNKNOWN, got {v.verdict}"


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
    finally:
        instruments._save(real)


def t_cannot_construct_uncited_verdict():
    for kwargs in (
        dict(verdict=RED, citation_url=None, quoted_terms=None),
        dict(verdict=GREEN, citation_url="http://x", quoted_terms=""),
        dict(verdict=UNKNOWN, citation_url="http://x", quoted_terms="terms"),
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


print("WATCH IT GO RED — control tests\n")
for n, f in list(globals().items()):
    if n.startswith("t_"):
        check(n[2:].replace("_", " "), f)
print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
