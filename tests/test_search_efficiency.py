"""Search efficiency — fewer Parallel calls and fetches without weakening verdicts."""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from clearance import facts, instruments, search as _search
from clearance.facts import Claim, judge_claim, _queries_for
from clearance.locate import DEFAULT
from clearance.verdict import GREEN

_PRIMARY = "https://www.legislation.gov.uk/ukpga/2024/1/section/3"
_WIKI = "https://en.wikipedia.org/wiki/Example"
_MUST = "came into force on 1 April 2024"
_TEXT = "The Act came into force on 1 April 2024."
_DOC = (
    "Explanatory notes.\n"
    "The Act came into force on 1 April 2024 across England and Wales.\n"
)


def t_queries_prefer_distinctive_term():
    q = _queries_for(Claim("C1", _TEXT, None, _MUST))
    assert q == [_MUST], q


def t_primary_hit_skips_extra_fetches_and_second_search():
    saved_find = _search.find_sources
    saved_doc = instruments.document
    fetches = []

    def fake_find(objective, queries, *, live=False, max_results=5, **kw):
        return [
            _search.Candidate(url=_PRIMARY, title="primary", excerpt=""),
            _search.Candidate(url=_WIKI, title="wiki", excerpt=""),
        ]

    def fake_doc(url, fetch=False, **kw):
        fetches.append(url)
        return _DOC if url == _PRIMARY else "unrelated page"

    _search.find_sources = fake_find
    instruments.document = fake_doc
    try:
        v = judge_claim(
            Claim("C1", _TEXT, None, _MUST),
            locator=DEFAULT, live_search=True, fetch=True,
        )
    finally:
        _search.find_sources = saved_find
        instruments.document = saved_doc

    assert v.verdict == GREEN, (v.verdict, v.cause)
    assert fetches == [_PRIMARY], f"should stop after primary verified, got {fetches}"


def t_term_cache_reuses_search_across_query_shapes():
    with tempfile.TemporaryDirectory() as d:
        cache = Path(d) / "searches.json"
        saved = _search.CACHE
        _search.CACHE = cache
        _search.reset_calls()
        try:
            first = _search.find_sources(
                "Find X", ["term one"], live=False, term="directive 2012/28/eu")
            assert first is None
            cache.write_text('{"directive 2012/28/eu": [{"url": "http://a", "title": "t", "excerpt": "e"}]}')
            second = _search.find_sources(
                "Different objective", ["other query"], live=False,
                term="directive 2012/28/eu")
            assert second and second[0].url == "http://a"
        finally:
            _search.CACHE = saved


if __name__ == "__main__":
    for fn in (t_queries_prefer_distinctive_term,
               t_primary_hit_skips_extra_fetches_and_second_search,
               t_term_cache_reuses_search_across_query_shapes):
        fn()
        print(f"PASS  {fn.__name__}")
    print("\n3/3 passed")
