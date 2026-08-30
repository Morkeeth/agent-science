#!/usr/bin/env python3
"""Qwen eval gate — holdout frozen before first tuning pass.

Verifies fixtures/refusal-correctness/set.json still matches the sealed SHA256.
Eval scripts must call this (or import check_holdout) before scoring.

Run: python3 scripts/eval_holdout_freeze.py
Exit 0 when holdout intact; exit 1 if set.json drifted since freeze.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FREEZE = ROOT / "fixtures/refusal-correctness/HOLDOUT-FREEZE.json"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_holdout() -> tuple[bool, str]:
    if not FREEZE.exists():
        return False, f"MISSING {FREEZE.relative_to(ROOT)}"
    meta = json.loads(FREEZE.read_text())
    set_path = ROOT / meta["set_path"]
    if not set_path.exists():
        return False, f"MISSING {meta['set_path']}"
    measured = sha256_file(set_path)
    expected = meta["sha256"]
    if measured != expected:
        return False, (
            f"HOLDOUT DRIFT — {meta['set_path']} changed after freeze "
            f"(expected {expected[:12]}… measured {measured[:12]}…)"
        )
    return True, (
        f"holdout OK · frozen {meta['frozen_at']} · "
        f"{meta['set_path']} sha256={measured[:12]}…"
    )


def main() -> int:
    ok, msg = check_holdout()
    print(msg)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
