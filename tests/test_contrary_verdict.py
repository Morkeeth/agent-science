"""Tests for CONTRARY_TO_RESEARCH verdict."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def t_contrary_constant():
    from clearance.verdict import CONTRARY_TO_RESEARCH, VERDICTS
    assert CONTRARY_TO_RESEARCH in VERDICTS


def t_unrelated_and_seed_queries_abstain_without_comparable_evidence():
    from clearance import contrary
    for query in ("fruit loop cereal nutrition", "best practice for tomato pruning",
                  "ralph loop agentic practice", "ralph loop agentic coding"):
        assert contrary.check(query) is None
        assert contrary.check(query, practices=[], field=[]) is None


def t_sourced_not_contrary():
    from clearance import contrary
    primary = {"label": "SOURCED", "verdict": "GREEN"}
    assert contrary.check("ralph loop", primary=primary) is None


if __name__ == "__main__":
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
