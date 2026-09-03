"""Holdout freeze gate — must fail if labelled set drifts."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_holdout_manifest_matches():
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts/eval_verify_holdout.py")],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "HOLDOUT OK" in proc.stdout


def test_holdout_gate_goes_red_on_drift():
    """Watch the control go RED — empty manifest must not pass."""
    proc = subprocess.run(
        [sys.executable, "-c", """
import json, sys, tempfile
from pathlib import Path
import scripts.eval_verify_holdout as h
ROOT = Path('.')
bad = {'files': {'set.json': '0' * 64}}
with tempfile.TemporaryDirectory() as d:
    m = Path(d) / 'MANIFEST.json'
    m.write_text(json.dumps(bad))
    old = h.MANIFEST
    h.MANIFEST = m
    try:
        sys.exit(h.main())
    finally:
        h.MANIFEST = old
"""],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    assert proc.returncode != 0, "drifted holdout must fail the gate"
