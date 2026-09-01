"""Pins Qwen holdout-frozen + scorer-symmetry gates — must stay runnable offline."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _run(script: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(ROOT / "scripts" / script)],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )


def test_holdout_labels_match_frozen_manifest():
    proc = _run("eval_holdout_frozen.py")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "PASS  scoring labels match frozen manifest" in proc.stdout


def test_scorer_symmetry_runs_on_delivered_output():
    subprocess.run(
        [sys.executable, str(ROOT / "scripts/seed_document_cache.py")],
        cwd=str(ROOT),
        check=True,
        capture_output=True,
    )
    proc = _run("eval_scorer_symmetry.py")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "Delivered schema:" in proc.stdout
    assert "RC5" in proc.stdout


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
