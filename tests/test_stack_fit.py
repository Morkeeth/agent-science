"""Tests for stack-fit magnet eval."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def t_detect_stack_this_repo():
    from clearance import stack_fit
    det = stack_fit.detect_stack(ROOT)
    assert "python" in det["stack"]
    assert det["has_agents_md"] is True


def t_score_fits_agents():
    from clearance import stack_fit
    res = stack_fit.score("science_lookup MCP fleet websearch", root=ROOT)
    assert res["fit"] == "fits"
    assert res.get("improvement")


def t_cli_stack_fit():
    import subprocess
    proc = subprocess.run(
        [sys.executable, "-m", "clearance.stack_cli", "stack-fit", "ralph loop context"],
        capture_output=True, text=True, cwd=str(ROOT),
    )
    assert proc.returncode == 0
    assert "fit=" in proc.stdout


def t_truth_skill_fit():
    import subprocess
    proc = subprocess.run(
        [sys.executable, "-m", "clearance.stack_cli", "truth", "skill", "--fit", "registry compound"],
        capture_output=True, text=True, cwd=str(ROOT),
    )
    assert proc.returncode == 0
    assert "fit=" in proc.stdout


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
