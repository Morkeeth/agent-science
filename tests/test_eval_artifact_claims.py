"""Artifact-claims gate — RED when live pack drifts; planted stale must stay STALE.

Run: python3 tests/test_eval_artifact_claims.py
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_artifact_claims_gate_runs():
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts/eval_artifact_claims.py")],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    out = proc.stdout + proc.stderr
    assert "ARTIFACT-CLAIMS EVAL" in out
    assert "AC10" in out
    assert "STALE" in out
    assert proc.returncode == 0, out[-800:]


def test_planted_stale_is_never_fresh():
    """Watch the control: planted file must still claim an absurd number."""
    text = (ROOT / "fixtures/artifact-claims/planted-stale.md").read_text()
    assert "999999" in text


def test_null_arm_loses_when_stale_exists():
    """Always-silent null must not score 100% while AC10 is STALE."""
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts/eval_artifact_claims.py")],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    out = proc.stdout + proc.stderr
    m = re.search(r"Null:\s+(\d+)/(\d+)", out)
    assert m, out[-500:]
    null_ok, n = int(m.group(1)), int(m.group(2))
    assert null_ok < n, "null tied or beat perfect — planted STALE missing?"


def test_cost_billing_goes_red_without_export():
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts/eval_cost_billing.py")],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    out = proc.stdout + proc.stderr
    assert proc.returncode == 2, out
    assert "BLOCKED" in out
    assert "Price card date:" in out


if __name__ == "__main__":
    quiet = "-q" in sys.argv
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    bad = 0
    for fn in fns:
        try:
            fn()
            if not quiet:
                print(f"PASS  {fn.__name__}")
        except AssertionError as e:
            bad += 1
            print(f"FAIL  {fn.__name__}: {e}")
    print(f"\n{len(fns) - bad}/{len(fns)} passed")
    sys.exit(1 if bad else 0)
