"""Truth dictionary — daily lookup tiers."""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from clearance import dictionary, refusal_log


def t_alias_canonicalizes():
    assert dictionary.canonical_query("orphan works directive") == "2012/28/EU"
    assert dictionary.canonical_query("Directive 2012/28/EU") == "2012/28/EU"


def t_exact_query_replay_is_free():
    with tempfile.TemporaryDirectory() as d:
        db = Path(d) / "t.db"
        con = refusal_log.connect(db)
        refusal_log.log_query(
            con,
            query="test query alpha",
            result={
                "label": "SOURCED",
                "established": "test query alpha",
                "verdict": "GREEN",
                "citation_url": "http://example.invalid",
                "quoted_terms": "exact span",
            },
        )
        hit = dictionary.last_exact_answer(con, "test query alpha")
        assert hit and hit["label"] == "SOURCED"
        out = dictionary.lookup("test query alpha", db=db, live=False)
        assert out["cost_tier"] == "free"
        assert out["parallel_api_calls"] == 0


def t_unsourced_exact_is_not_replayed():
    with tempfile.TemporaryDirectory() as d:
        db = Path(d) / "t.db"
        con = refusal_log.connect(db)
        refusal_log.log_query(
            con,
            query="Directive 2012/28/EU",
            result={
                "label": "UNSOURCED",
                "verdict": "UNKNOWN",
                "cause": "search_found_no_admissible_source",
            },
        )
        assert dictionary.last_exact_answer(con, "Directive 2012/28/EU") is None


def t_miss_without_live_is_free_not_cleared():
    with tempfile.TemporaryDirectory() as d:
        db = Path(d) / "t.db"
        out = dictionary.lookup("totally unknown xyz claim 99999", db=db, live=False)
        assert out["label"] == "NOT_CLEARED"
        assert out["cost_tier"] == "free"
        assert out.get("next_step")


if __name__ == "__main__":
    for fn in (t_alias_canonicalizes, t_exact_query_replay_is_free,
               t_unsourced_exact_is_not_replayed,
               t_miss_without_live_is_free_not_cleared):
        fn()
        print(f"PASS  {fn.__name__}")
    print("\n4/4 passed")
