#!/usr/bin/env python3
"""Control: paraphrase compound must stay RED; identical overlap must compound.

Watched red first (2026-09-10): under exact-assertion reuse, paraphrased B
produced A=2→B=3 with corpus_hits=0. A green tick without that RED is not a
control — see docs/FINDING-compound-exact-assertion-2026-09-10.md.

Run: python3 tests/test_compound_exact_assertion.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import eval_cost_baseline as cost  # noqa: E402


def test_paraphrase_overlap_does_not_compound():
    """The old compound-mini-B shape — must spend like a cold run."""
    para = cost._run_pair(cost.B_PARAPHRASE)
    assert para["b_corpus_hits"] == 0, (
        f"paraphrase unexpectedly reused (hits={para['b_corpus_hits']}); "
        "exact-assertion binding regressed"
    )
    assert para["b_parallel"] >= para["a_parallel"], (
        f"paraphrase B_par={para['b_parallel']} < A_par={para['a_parallel']} — "
        "looked green without identical assertions"
    )
    print("PASS  test_paraphrase_overlap_does_not_compound "
          f"(A={para['a_parallel']} B={para['b_parallel']} hits={para['b_corpus_hits']})")


def test_identical_overlap_compounds():
    ship = cost._run_pair(cost.B_IDENTICAL)
    assert ship["b_corpus_hits"] >= 1, f"identical overlap missed corpus: {ship}"
    assert ship["b_parallel"] < ship["a_parallel"], (
        f"identical overlap failed Parallel drop: {ship}"
    )
    print("PASS  test_identical_overlap_compounds "
          f"(A={ship['a_parallel']} B={ship['b_parallel']} hits={ship['b_corpus_hits']})")


def test_naive_arm_spends_more_than_shipping():
    naive = cost._run_naive()
    ship = cost._run_pair(cost.B_IDENTICAL)
    assert naive["total_parallel"] > ship["total_parallel"], (
        f"naive {naive['total_parallel']} did not beat shipping {ship['total_parallel']}"
    )
    print("PASS  test_naive_arm_spends_more_than_shipping "
          f"(naive={naive['total_parallel']} shipping={ship['total_parallel']})")


if __name__ == "__main__":
    test_paraphrase_overlap_does_not_compound()
    test_identical_overlap_compounds()
    test_naive_arm_spends_more_than_shipping()
    print("3/3 passed")
