#!/usr/bin/env python3
"""RED control for artifact-claims eval — a planted stale pack must fail shipping.

Watches the gate go red before trusting green: write a temp pack that claims
watch_it_go_red 26/13 (impossible), point the eval at it, expect exit 1.
"""
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVAL = ROOT / "scripts" / "eval_artifact_claims.py"
PACK = ROOT / "docs" / "SUBMISSION-PACK-2026-08-29.md"


def _run(env_pack: Path | None = None, offline: bool = True) -> tuple[int, str]:
    env = dict(**{k: v for k, v in __import__("os").environ.items()})
    cmd = [sys.executable, str(EVAL)]
    if offline:
        cmd.append("--offline")
    # Monkey via env var the eval will honour
    if env_pack is not None:
        env["ARTIFACT_CLAIMS_PACK"] = str(env_pack)
    proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, env=env)
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def test_planted_stale_26_13_goes_red() -> None:
    """Control: pack claiming watch_it_go_red 26/13 must make shipping fail."""
    text = PACK.read_text()
    poisoned = re.sub(
        r"(watch_it_go_red\s*\|[^|]*\|\s*)\*\*\d+/\d+\*\*",
        r"\1**26/13**",
        text,
        count=1,
    )
    assert "**26/13**" in poisoned, "plant failed — regex did not rewrite count"
    with tempfile.TemporaryDirectory() as td:
        fake = Path(td) / "SUBMISSION-PACK-poisoned.md"
        fake.write_text(poisoned)
        # Patch eval to read ARTIFACT_CLAIMS_PACK — if unsupported, import and call
        code = fake.read_text()
        # Direct unit: invoke measure path by temporarily swapping PACK via env
        # The eval script must honour ARTIFACT_CLAIMS_PACK.
        rc, out = _run(env_pack=fake, offline=True)
    assert rc != 0, f"expected RED on planted 26/13, got exit 0\n{out[-800:]}"
    assert "26/13" in out or "STALE" in out or "stale" in out.lower(), out[-800:]
    print("PASS  test_planted_stale_26_13_goes_red")


def test_eval_script_exists() -> None:
    assert EVAL.is_file()
    print("PASS  test_eval_script_exists")


def main() -> int:
    test_eval_script_exists()
    test_planted_stale_26_13_goes_red()
    print()
    print("2/2 passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
