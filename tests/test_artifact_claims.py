"""Artifact-claims gate — object probes must match gold; RED control watched."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SET = ROOT / "fixtures/artifact-claims/set.json"


def test_artifact_claims_object_arm_matches_gold():
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts/eval_artifact_claims.py")],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    out = proc.stdout + proc.stderr
    assert proc.returncode == 0, out
    assert "OBJECT:" in out
    assert "AC10" in out
    assert "CONTROL FAIL" not in out


def test_planted_red_control_is_labelled_not_held():
    data = json.loads(SET.read_text())
    planted = next(i for i in data["items"] if i["id"] == "AC10")
    assert planted["expected"] == "NOT_HELD"
    assert planted["probe_args"]["key"] == "__planted_red_control__"


def test_artifact_claims_gate_goes_red_when_probe_lies():
    """Watch RED: if object arm reports HELD for AC10, eval must exit nonzero."""
    proc = subprocess.run(
        [
            sys.executable,
            "-c",
            """
import scripts.eval_artifact_claims as m
real = m.probe

def lie(item, host):
    if item['id'] == 'AC10':
        return m.HELD, 'planted lie'
    return real(item, host)

m.probe = lie
raise SystemExit(m.main())
""",
        ],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    out = proc.stdout + proc.stderr
    assert proc.returncode != 0, out
    assert "CONTROL FAIL" in out or "OBJECT arm" in out


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
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
