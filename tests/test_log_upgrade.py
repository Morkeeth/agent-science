"""Unsettled independence refuses must not freeze the cross-subject log forever."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from clearance import refusal_log as L
from clearance.verdict import GREEN, UNKNOWN


def t_independence_refuse_is_not_settled_for_reuse():
    assert not L.is_settled_for_reuse(
        verdict="UNKNOWN", cause="no_independent_source")
    assert L.is_settled_for_reuse(
        verdict="UNKNOWN", cause="search_found_no_admissible_source")
    assert L.is_settled_for_reuse(verdict="GREEN", cause=None)


def t_green_upgrades_poisoned_independence_row():
    con = L.connect(":memory:")
    T = "Directive 2012/28/EU"
    assertion = f"{T} permits certain uses of orphan works."
    L.record(con, term=T, assertion=assertion, verdict=UNKNOWN,
             production="poison", cause="no_independent_source")
    hit = L.lookup(con, term=T, assertion=assertion)
    assert hit["verdict"] == UNKNOWN and hit["cause"] == "no_independent_source"

    L.record(con, term=T, assertion=assertion, verdict=GREEN,
             production="eur-lex", basis="primary",
             citation_url="https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32012L0028",
             quoted_terms="certain permitted uses of orphan works")
    hit2 = L.lookup(con, term=T, assertion=assertion)
    assert hit2["verdict"] == GREEN, hit2
    assert "eur-lex" in (hit2.get("citation_url") or "")
    assert L.stats(con)["n"] == 1, "upgrade must not duplicate the row"


def t_green_is_not_downgraded_by_later_refuse():
    con = L.connect(":memory:")
    T = "Directive 2012/28/EU"
    assertion = f"{T} is EU primary law."
    L.record(con, term=T, assertion=assertion, verdict=GREEN,
             production="A", basis="primary", citation_url="u", quoted_terms="q")
    L.record(con, term=T, assertion=assertion, verdict=UNKNOWN,
             production="B", cause="no_independent_source")
    hit = L.lookup(con, term=T, assertion=assertion)
    assert hit["verdict"] == GREEN


def t_week_tally_counts_cleared_and_caught():
    con = L.connect(":memory:")
    L.record(con, term="A", assertion="A is true in 2012", verdict=GREEN,
             production="p", basis="primary", citation_url="u", quoted_terms="q")
    L.record(con, term="B", assertion="B never happened", verdict=UNKNOWN,
             production="p", cause="search_found_no_admissible_source")
    w = L.week_tally(con, days=7)
    assert w["cleared"] == 1 and w["caught"] == 1 and w["n"] == 2


if __name__ == "__main__":
    failed = 0
    for name, fn in list(globals().items()):
        if name.startswith("t_") and callable(fn):
            try:
                fn()
                print(f"  PASS  {name}")
            except Exception as e:
                failed += 1
                print(f"  FAIL  {name}: {e}")
    print(f"\n{failed} failed" if failed else "\nall passed")
    raise SystemExit(failed)
