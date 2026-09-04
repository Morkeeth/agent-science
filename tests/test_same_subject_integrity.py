"""Drive same-subject reuse through the real pipeline; replace only external effects."""
from __future__ import annotations

import json
import os
import sys
import tempfile
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import agent_science as A
from clearance import corpus, refusal_log as L
from clearance.verdict import Verdict, FACT, GREEN, UNKNOWN
from clearance.locate import DEFAULT
from test_evidence_integrity import Network, POSITIVE, NEGATIVE, URL


class Extractor:
    name = "test extraction boundary"

    def __init__(self, **kwargs):
        pass

    def extract(self, script):
        return [A.Claim("C1", script, None, "commercial redistribution")]


def run(tmp, text, subject="same"):
    with patch.object(A, "GeminiExtractor", Extractor), \
         patch.object(A, "GeminiLocator", lambda **kw: DEFAULT), \
         patch.dict(os.environ, {"RUN_HISTORY_JSON": str(tmp / "runs.json")}):
        return A.clear_script(text, subject=subject, corpus_db=tmp / "corpus.db", log_db=tmp / "claims.db")


def test_identical_support_reuses_but_opposite_claim_with_same_anchor_searches():
    with tempfile.TemporaryDirectory() as d, Network(POSITIVE) as net:
        tmp = Path(d)
        first = run(tmp, POSITIVE)
        assert first["rows"][0]["label"] == "SOURCED"
        before = len(net.searches)
        same = run(tmp, POSITIVE)
        assert same["corpus_hits"] == 1 and len(net.searches) == before
        opposite = run(tmp, NEGATIVE)
        assert opposite["corpus_hits"] == opposite["log_hits"] == 0
        assert len(net.searches) > before
        assert opposite["rows"][0]["label"] != "SOURCED"


def test_later_uncertainty_in_shared_log_invalidates_same_subject_support():
    with tempfile.TemporaryDirectory() as d, Network(POSITIVE) as net:
        tmp = Path(d)
        run(tmp, POSITIVE)
        con = L.connect(tmp / "claims.db")
        L.record(con, term="commercial redistribution", assertion=POSITIVE,
                 verdict=UNKNOWN, cause="source_does_not_state_it", production="other")
        before = len(net.searches)
        net.document_text = NEGATIVE
        result = run(tmp, POSITIVE)
        assert result["corpus_hits"] == result["log_hits"] == 0
        assert len(net.searches) > before
        assert result["rows"][0]["label"] != "SOURCED"


def test_later_query_refutation_also_invalidates_both_saved_paths():
    with tempfile.TemporaryDirectory() as d, Network(POSITIVE) as net:
        tmp = Path(d)
        run(tmp, POSITIVE)
        con = L.connect(tmp / "claims.db")
        L.log_query(con, query=POSITIVE, result={"label": "REFUTED", "verdict": "RED"})
        before = len(net.searches)
        net.document_text = NEGATIVE
        result = run(tmp, POSITIVE)
        assert result["corpus_hits"] == result["log_hits"] == 0
        assert len(net.searches) > before
        assert result["rows"][0]["label"] != "SOURCED"


def test_unknown_same_subject_retries_and_recovers_on_new_evidence():
    with tempfile.TemporaryDirectory() as d, Network(NEGATIVE) as net:
        tmp = Path(d)
        first = run(tmp, POSITIVE)
        assert first["rows"][0]["label"] != "SOURCED"
        before = len(net.searches)
        net.document_text = POSITIVE
        second = run(tmp, POSITIVE)
        assert second["rows"][0]["label"] == "SOURCED"
        assert second["corpus_hits"] == second["log_hits"] == 0
        assert len(net.searches) > before


def test_changed_source_span_in_shared_log_replaces_the_local_quote():
    with tempfile.TemporaryDirectory() as d, Network(POSITIVE) as net:
        tmp = Path(d)
        run(tmp, POSITIVE)
        con = L.connect(tmp / "claims.db")
        new_span = POSITIVE + " These terms apply from September 2026."
        L.record(con, term="commercial redistribution", assertion=POSITIVE,
                 verdict=GREEN, citation_url=URL, quoted_terms=new_span, production="other")
        before = len(net.searches)
        second = run(tmp, POSITIVE)
        assert second["corpus_hits"] == 0 and second["log_hits"] == 1
        assert second["rows"][0]["quoted_terms"] == new_span
        assert len(net.searches) == before


def test_later_shared_refutation_replaces_local_green_without_search():
    with tempfile.TemporaryDirectory() as d, Network(POSITIVE) as net:
        tmp = Path(d)
        run(tmp, POSITIVE)
        con = L.connect(tmp / "claims.db")
        L.record(con, term="commercial redistribution", assertion=POSITIVE,
                 verdict="RED", citation_url=URL, quoted_terms=NEGATIVE, production="other")
        before = len(net.searches)
        second = run(tmp, POSITIVE)
        assert second["corpus_hits"] == 0 and second["log_hits"] == 1
        assert second["rows"][0]["label"] == "REFUTED"
        assert second["rows"][0]["quoted_terms"] == NEGATIVE
        assert len(net.searches) == before


def test_corpus_checks_assertion_even_if_a_caller_supplies_a_wrong_key():
    con = corpus.connect(":memory:")
    v = Verdict(subject_id="key", subject_title=POSITIVE, noun=FACT, use="sourcing:same",
                verdict=GREEN, reason="verified", citation_url=URL, quoted_terms=POSITIVE)
    corpus.remember(con, [v])
    assert corpus.recall(con, "key", v.use, assertion=POSITIVE)
    assert corpus.recall(con, "key", v.use, assertion=NEGATIVE) is None


def test_older_observations_cannot_restore_green_and_history_keeps_both():
    con = corpus.connect(":memory:")
    new = Verdict(subject_id="key", subject_title=POSITIVE, noun=FACT, use="sourcing:same",
                  verdict=UNKNOWN, cause="search_found_no_admissible_source", reason="no support",
                  observed_at="2026-09-04T10:00:00+00:00")
    old = replace(new, verdict=GREEN, cause=None, reason="old support", citation_url=URL,
                  quoted_terms=POSITIVE, observed_at="2026-09-03T10:00:00+00:00")
    corpus.remember(con, [new])
    corpus.remember(con, [old])
    assert corpus.recall(con, "key", new.use).verdict == UNKNOWN
    assert corpus.recall(con, "key", new.use, assertion=POSITIVE) is None
    history = [json.loads(row[0])["verdict"] for row in con.execute("SELECT payload FROM verdict_observations ORDER BY id")]
    assert history == [UNKNOWN, GREEN]


if __name__ == "__main__":
    tests = [fn for name, fn in list(globals().items()) if name.startswith("test_")]
    for test in tests:
        test()
        print("PASS", test.__name__)
    print(f"{len(tests)}/{len(tests)} passed")
