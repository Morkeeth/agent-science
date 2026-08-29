#!/usr/bin/env python3
"""Eval gate smoke — baseline + ablation + shipping arms run offline."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "eval/refusal_correctness_gate.py"
RECEIPT = ROOT / "eval/RECEIPT-refusal-gate.md"
SET = ROOT / "fixtures/refusal-correctness/set.json"


def test_gate_runs_and_writes_receipt():
    r = subprocess.run(
        [sys.executable, str(GATE)],
        capture_output=True, text=True, cwd=ROOT,
    )
    assert r.returncode == 0, r.stdout + r.stderr
    body = RECEIPT.read_text()
    assert "BASELINE" in body and "ABLATION" in body and "SHIPPING" in body
    assert "RC5 engine_limit" in body


def test_external_anchor_exists():
    import json
    meta = json.loads(SET.read_text())
    assert len(meta["items"]) >= 5
    assert meta.get("labelled_at")


def test_ablation_arm_named_in_receipt():
    subprocess.run([sys.executable, str(GATE)], check=True, cwd=ROOT)
    body = RECEIPT.read_text()
    assert "ABLATION" in body
    assert "verify" in body.lower()


if __name__ == "__main__":
    fns = [v for k, v in globals().items() if k.startswith("test_") and callable(v)]
    bad = 0
    for fn in fns:
        try:
            fn()
            print(f"PASS  {fn.__name__}")
        except AssertionError as e:
            bad += 1
            print(f"FAIL  {fn.__name__}: {e}")
    print(f"\n{len(fns) - bad}/{len(fns)} passed")
    sys.exit(1 if bad else 0)
