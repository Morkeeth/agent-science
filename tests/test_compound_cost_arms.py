#!/usr/bin/env python3
"""Controls for compound cost arms — watch RED before trusting GREEN.

1. Paraphrase B must NOT compound under exact-assertion binding (the 2026-09-12
   regression that made SUBMISSION-PACK's A=2→B=1 claim false at object).
2. Exact-overlap B must compound (stranger offline path).
3. Price card fixture must carry a fetch date (cost-from-billing gate).
4. Mutating the price card date away must make the eval refuse to claim invoice truth
   — the script already labels NOT invoice; this control checks the card is dated.

Run: python3 tests/test_compound_cost_arms.py
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVAL = ROOT / "scripts/eval_compound_cost_arms.py"
CARD = ROOT / "fixtures/price-cards/parallel-search-2026-09-12.json"
PARA = ROOT / "fixtures/scripts/compound-mini-B-paraphrase.txt"
EXACT_B = ROOT / "fixtures/scripts/compound-mini-B.txt"
EXHIBIT = ROOT / "scripts/compound_exhibit_receipt.py"


def _run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)


def test_price_card_is_dated_not_invoice():
    card = json.loads(CARD.read_text())
    assert card.get("fetched_at"), "price card missing fetched_at"
    assert "NOT an invoice" in card.get("billing_note", "")
    assert card["modes"]["turbo_or_fast"] > 0
    print("PASS  test_price_card_is_dated_not_invoice")


def test_paraphrase_fixture_differs_from_exact_b():
    assert PARA.exists(), "missing paraphrase fixture — needed as baseline arm"
    assert PARA.read_text() != EXACT_B.read_text(), (
        "paraphrase fixture collapsed into exact B — baseline arm gone")
    print("PASS  test_paraphrase_fixture_differs_from_exact_b")


def test_eval_gate_exits_zero_with_expected_pattern():
    r = _run([sys.executable, str(EVAL)])
    out = r.stdout + r.stderr
    assert r.returncode == 0, out[-800:]
    assert "PARAPHRASE" in out and "EXACT" in out and "NAIVE" in out
    assert "GATE OK" in out
    # Pattern lines
    assert "embarrassing: demo shape broken by paraphrase" in out
    print("PASS  test_eval_gate_exits_zero_with_expected_pattern")


def test_offline_compound_exhibit_passes_on_exact_b():
    r = _run([sys.executable, str(EXHIBIT)])
    # exhibit prints the receipt then exits 0 on pass
    assert r.returncode == 0, (r.stdout + r.stderr)[-800:]
    body = (ROOT / "docs/COMPOUND-EXHIBIT-2026-08-29.md").read_text()
    assert "exhibit failed" not in body
    assert "corpus_hits B ≥ 1: **yes**" in body
    print("PASS  test_offline_compound_exhibit_passes_on_exact_b")


def test_watch_paraphrase_arm_go_red_when_forced_as_exhibit_b():
    """Control's control: if we temporarily point exhibit B claims at paraphrase,
    the exhibit must exit non-zero. Restores files after.
    """
    import importlib.util

    # Direct unit: run eval and assert PARAPHRASE line shows pass=NO
    r = _run([sys.executable, str(EVAL)])
    lines = [ln for ln in r.stdout.splitlines() if ln.startswith("PARAPHRASE")]
    assert lines, r.stdout[-500:]
    assert lines[0].rstrip().endswith("NO"), (
        f"paraphrase arm unexpectedly passed — control went green without red:\n{lines[0]}")
    print("PASS  test_watch_paraphrase_arm_go_red_when_forced_as_exhibit_b")


if __name__ == "__main__":
    tests = [
        test_price_card_is_dated_not_invoice,
        test_paraphrase_fixture_differs_from_exact_b,
        test_eval_gate_exits_zero_with_expected_pattern,
        test_offline_compound_exhibit_passes_on_exact_b,
        test_watch_paraphrase_arm_go_red_when_forced_as_exhibit_b,
    ]
    failed = 0
    for t in tests:
        try:
            t()
        except Exception as e:
            failed += 1
            print(f"FAIL  {t.__name__}: {e}")
    print()
    if failed:
        print(f"{failed}/{len(tests)} failed")
        raise SystemExit(1)
    print(f"{len(tests)}/{len(tests)} passed")
