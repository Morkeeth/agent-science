"""Adversarial claim identity, replay, route and uncertainty checks; no paid APIs."""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from clearance import dictionary as D, instruments, refusal_log as L, search as S
from clearance.facts import Claim, judge_claim
from clearance.locate import DEFAULT

URL = "https://www.legislation.gov.uk/ukpga/2024/1/section/3"
POSITIVE = "The Acme project permits commercial redistribution of its software."
NEGATIVE = "The Acme project does not permit commercial redistribution of its software."


class Network:
    def __init__(self, document=POSITIVE):
        self.document_text = document
        self.searches = []
        self.fetches = []

    def search(self, objective, queries, **kwargs):
        self.searches.append((objective, queries))
        return [S.Candidate(url=URL, title="Terms", excerpt=self.document_text)]

    def document(self, url, **kwargs):
        self.fetches.append(url)
        return self.document_text if url == URL else None

    def __enter__(self):
        self.patches = [patch.object(S, "find_sources", self.search),
                        patch.object(instruments, "document", self.document),
                        patch.object(D, "GeminiLocator", lambda **kw: DEFAULT)]
        for p in self.patches:
            p.start()
        return self

    def __exit__(self, *args):
        for p in reversed(self.patches):
            p.stop()


def seed(con, assertion=POSITIVE, verdict="GREEN", cause=None):
    L.record(con, term="redistribution", assertion=assertion, verdict=verdict,
             cause=cause, production="test", citation_url=URL, quoted_terms=assertion)


def test_polarity_uses_actual_verifier_in_both_directions_and_positive_controls():
    for claim, doc, supported in ((NEGATIVE, POSITIVE, False),
                                  (POSITIVE, NEGATIVE, False),
                                  (POSITIVE, POSITIVE, True),
                                  (NEGATIVE, NEGATIVE, True)):
        with Network(doc):
            result = judge_claim(Claim("Q", claim, URL, "commercial redistribution"),
                                 locator=DEFAULT, fetch=True, live_search=False)
        assert (result.verdict == "GREEN") is supported, (claim, doc, result)


def test_substring_uncertainty_never_becomes_a_sourced_answer_or_replay():
    with tempfile.TemporaryDirectory() as d:
        db = Path(d) / "claims.db"
        con = L.connect(db)
        uncertain = "It is uncertain whether " + POSITIVE[0].lower() + POSITIVE[1:]
        seed(con, uncertain)
        with Network() as net:
            for _ in range(2):
                result = D.lookup(POSITIVE, db=db)
                assert result["label"] == "NOT_CLEARED", result
                assert result["candidates"][0]["established"] == uncertain
            assert not net.searches and not net.fetches
        assert con.execute("SELECT count(*) FROM queries").fetchone()[0] == 2


def test_exact_reuse_preserves_wording_and_only_traces_executed_routes():
    with tempfile.TemporaryDirectory() as d:
        db = Path(d) / "claims.db"
        con = L.connect(db)
        seed(con)
        with Network() as net:
            first = D.lookup(POSITIVE, db=db)
            second = D.lookup(POSITIVE, db=db)
        assert first["label"] == second["label"] == "SOURCED"
        assert first["established"] == second["established"] == POSITIVE
        assert [t["route"] for t in first["trace"]] == ["dictionary_exact", "registry"]
        assert second["trace"] == [{"route": "dictionary_exact", "query": POSITIVE, "outcome": "hit"}]
        assert not net.searches and not net.fetches
        rows = L.browse_queries(con)
        assert len(rows) == 2
        assert json.loads(rows[0]["trace"]) == second["trace"]


def test_latest_observation_displaces_green_and_retains_history():
    con = L.connect(":memory:")
    seed(con)
    seed(con, verdict="RED", cause="contradicted")
    result = L.lookup(con, term="redistribution", assertion=POSITIVE)
    assert result["verdict"] == "RED"
    assert con.execute("SELECT count(*) FROM claims").fetchone()[0] == 1
    history = [json.loads(r[0])["verdict"] for r in con.execute("SELECT payload FROM claim_observations ORDER BY id")]
    assert history == ["GREEN", "RED"]


def test_latest_query_refutation_cannot_resurrect_old_green():
    with tempfile.TemporaryDirectory() as d:
        db = Path(d) / "claims.db"
        con = L.connect(db)
        seed(con)
        D.lookup(POSITIVE, db=db)
        L.log_query(con, query=POSITIVE, result={"label": "REFUTED", "verdict": "RED"})
        with Network() as net:
            result = D.lookup(POSITIVE, db=db)
        assert result["label"] != "SOURCED", result
        assert not net.searches


def test_claim_slots_do_not_merge_predicates_values_scope_or_negation():
    con = L.connect(":memory:")
    claims = ["Acme was founded in 2012", "Acme was dissolved in 2024",
              "Acme was founded in 2013", "Acme was not founded in 2012",
              "Acme was founded in France in 2012"]
    for claim in claims:
        L.record(con, term="Acme", assertion=claim, verdict="UNKNOWN", production="test")
    assert L.stats(con)["n"] == len(claims)
    for claim in claims:
        assert L.lookup(con, term="Acme", assertion=claim)["established"] == claim
    assert L.lookup(con, term="Acme", assertion="Acme was founded") is None


def test_refresh_bypasses_both_saved_routes_and_uses_real_verifier():
    with tempfile.TemporaryDirectory() as d:
        db = Path(d) / "claims.db"
        con = L.connect(db)
        seed(con, NEGATIVE)
        # A saved green for a negative claim is invalid against this changed source.
        D.lookup(NEGATIVE, db=db)
        with Network(POSITIVE) as net:
            result = D.lookup(NEGATIVE, db=db, refresh=True, live=True)
        assert net.searches and net.fetches
        assert result["label"] != "SOURCED"
        assert [t["route"] for t in result["trace"]] == ["primary_route", "live_search"]
        assert L.lookup(con, term="redistribution", assertion=NEGATIVE)["verdict"] != "GREEN"
        assert con.execute("SELECT count(*) FROM queries").fetchone()[0] == 2


def test_unsettled_claims_retry_and_recover_without_double_logging():
    for cause in ("no_independent_source", "source_does_not_state_it", "search_found_no_admissible_source"):
        with tempfile.TemporaryDirectory() as d:
            db = Path(d) / "claims.db"
            con = L.connect(db)
            seed(con, verdict="UNKNOWN", cause=cause)
            with Network() as net:
                result = D.lookup(POSITIVE, db=db, live=True)
            assert net.searches and net.fetches
            assert result["label"] == "SOURCED", result
            assert result["trace"][1]["outcome"] == "unsettled"
            assert con.execute("SELECT count(*) FROM queries").fetchone()[0] == 1


def test_legacy_claims_migrate_without_fabricating_missing_collisions():
    with tempfile.TemporaryDirectory() as d:
        db = Path(d) / "claims.db"
        con = L.connect(db)
        seed(con)
        con.execute("UPDATE claims SET slot='identity'")
        con.commit()
        con.close()
        con = L.connect(db)
        assert L.lookup(con, term="redistribution", assertion=POSITIVE)["verdict"] == "GREEN"
        assert L.stats(con)["n"] == 1


def test_legacy_sourced_query_without_assertion_provenance_is_not_replayed():
    con = L.connect(":memory:")
    L.log_query(con, query=POSITIVE, result={"label": "SOURCED", "verdict": "GREEN", "quoted_terms": POSITIVE})
    assert D.last_exact_answer(con, POSITIVE) is None


def test_topic_browse_and_alias_do_not_consume_a_reuse_credit():
    with tempfile.TemporaryDirectory() as d:
        db = Path(d) / "claims.db"
        con = L.connect(db)
        seed(con)
        topic = L.search_registry(con, "redistribution")
        assert topic["label"] == "NOT_CLEARED"
        assert topic["candidates"][0]["established"] == POSITIVE
        assert L.stats(con)["reuses"] == 0
        # An alias can retrieve a claim but cannot prove the original assertion.
        with patch.object(D, "_aliases", lambda: {"acme topic": POSITIVE}):
            result = D.lookup("acme topic", db=db)
        assert result["label"] == "NOT_CLEARED"
        assert L.stats(con)["reuses"] == 0


def test_live_failure_has_one_query_event_and_an_observed_error_trace():
    with tempfile.TemporaryDirectory() as d:
        db = Path(d) / "claims.db"
        with Network(), patch.object(S, "find_sources", side_effect=RuntimeError("transport failed")):
            result = D.lookup(POSITIVE, db=db, live=True)
        assert result["cause"] == "search_failed"
        assert result["trace"][-1] == {"route": "live_search", "query": POSITIVE,
                                       "outcome": "error", "reason": "transport failed"}
        con = L.connect(db)
        assert con.execute("SELECT count(*) FROM queries").fetchone()[0] == 1


def test_economics_counts_reuse_separately_from_successful_live_answers():
    with tempfile.TemporaryDirectory() as d:
        db = Path(d) / "claims.db"
        with Network():
            D.lookup(POSITIVE, db=db, live=True)
            D.lookup(POSITIVE, db=db)
        stats = D.economics(db=db)
        assert stats["queries_logged"] == 2
        assert stats["queries_answered"] == 2
        assert stats["dictionary_hits"] == 1
        assert stats["dictionary_hit_rate"] == 0.5


if __name__ == "__main__":
    tests = [fn for name, fn in list(globals().items()) if name.startswith("test_")]
    for test in tests:
        test()
        print("PASS", test.__name__)
    print(f"{len(tests)}/{len(tests)} passed")
