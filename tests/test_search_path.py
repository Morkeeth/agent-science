"""The no-source_url LIVE-SEARCH path — the branch production actually runs.

`agent_science.clear_script` judges every claim with `live_search=True`, so a claim
arrives with NO source_url and `judge_claim` must find one itself (Parallel search →
fetch → locate → verify). The held-out refusal set exercises only the named-source
path; this closes the gap the held-out lane flagged.

Only the two NETWORK boundaries are faked — `search.find_sources` (Parallel) and
`instruments.document` (the fetch). The locator is the real shipping `StringLocator`
(`DEFAULT`), and `verify`, `assess_independence` and the verdict logic all run for
real. We substitute EFFECTS (what the network returns), never a RULE
(what counts as verified) — the same line the codebase's own contract draws.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from clearance import facts, instruments, search as _search
from clearance.facts import Claim, judge_claim
from clearance.locate import DEFAULT
from clearance.verdict import (GREEN, UNKNOWN, NO_SOURCE, SEARCH_FOUND_NOTHING)

_PRIMARY_URL = "https://www.legislation.gov.uk/ukpga/2024/1/section/3"  # classifies primary
_DOC_STATES_IT = (
    "Explanatory notes.\n"
    "The Act came into force on 1 April 2024 across England and Wales.\n"
    "Unrelated boilerplate follows and should be ignored by the locator.\n"
)
_DOC_SILENT = (
    "Explanatory notes.\n"
    "This document concerns fishing quotas in the North Sea and nothing else.\n"
)
_MUST = "came into force on 1 April 2024"
_TEXT = "The Act came into force on 1 April 2024."


def _claim() -> Claim:
    # source_url = None -> the branch that must search for a source itself.
    return Claim(claim_id="S1", text=_TEXT, source_url=None, must_contain=_MUST)


def _run(*, find_returns, doc_body=None, live_search=True):
    """Swap the two network boundaries, run the REAL judge_claim, restore."""
    saved_find = _search.find_sources
    saved_doc = instruments.document

    def fake_find(objective, queries, *, live=False, max_results=5, **kw):
        return find_returns

    def fake_doc(url, fetch=False):
        return doc_body

    _search.find_sources = fake_find
    instruments.document = fake_doc
    try:
        return judge_claim(_claim(), locator=DEFAULT, live_search=live_search, fetch=True)
    finally:
        _search.find_sources = saved_find
        instruments.document = saved_doc


def _cand(url):
    return _search.Candidate(url=url, title="t", excerpt="e")


def t_no_source_and_no_search_is_no_source_not_a_guess():
    # live_search=False and no source_url -> find_sources returns None -> NO_SOURCE.
    v = _run(find_returns=None, live_search=False)
    assert v.verdict == UNKNOWN and v.cause == NO_SOURCE, (v.verdict, v.cause)


def t_search_returns_nothing_is_honest_refusal():
    v = _run(find_returns=[])
    assert v.verdict == UNKNOWN and v.cause == SEARCH_FOUND_NOTHING, (v.verdict, v.cause)


def t_found_a_document_that_is_silent_still_refuses():
    # A search HIT whose document does not state the claim must not clear it.
    v = _run(find_returns=[_cand(_PRIMARY_URL)], doc_body=_DOC_SILENT)
    assert v.verdict == UNKNOWN and v.cause == SEARCH_FOUND_NOTHING, (v.verdict, v.cause)


def t_supported_claim_found_by_search_is_cleared_not_falsely_unknown():
    # THE false-UNKNOWN guard for the search path: a supported claim, whose source the
    # search finds and whose document states it verbatim, must be GREEN — not refused
    # for want of a source. gov.uk classifies primary, so independence holds.
    v = _run(find_returns=[_cand(_PRIMARY_URL)], doc_body=_DOC_STATES_IT)
    assert v.verdict == GREEN, (v.verdict, v.cause, v.reason)
    assert v.citation_url == _PRIMARY_URL
    # and it must never be one of the "no source" refusals
    assert v.cause not in (NO_SOURCE, SEARCH_FOUND_NOTHING)


def t_not_gameable_same_locator_both_poles():
    # The same real locator clears the supported doc and refuses the silent one — so a
    # test can't pass by an engine that says GREEN to everything or UNKNOWN to
    # everything.
    green = _run(find_returns=[_cand(_PRIMARY_URL)], doc_body=_DOC_STATES_IT)
    silent = _run(find_returns=[_cand(_PRIMARY_URL)], doc_body=_DOC_SILENT)
    assert green.verdict == GREEN and silent.verdict == UNKNOWN


if __name__ == "__main__":
    import sys
    fns = [v for k, v in sorted(globals().items()) if k.startswith("t_") and callable(v)]
    failed = 0
    for fn in fns:
        try:
            fn()
            print(f"PASS  {fn.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL  {fn.__name__}: {e}")
    print(f"\n{len(fns) - failed}/{len(fns)} passed")
    sys.exit(1 if failed else 0)
