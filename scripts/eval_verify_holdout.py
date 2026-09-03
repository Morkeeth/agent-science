#!/usr/bin/env python3
"""Qwen eval gate — holdout frozen before first tuning pass.

Pins fixtures/refusal-correctness/set.json and its document fixtures via
MANIFEST.json. Any drift after labelling fails the gate — labels cannot move
underfoot while the engine is tuned.

Run: python3 scripts/eval_verify_holdout.py
Exit 0 when holdout matches manifest; 1 on drift (print diff).
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOLDOUT = ROOT / "fixtures/refusal-correctness"
MANIFEST = HOLDOUT / "MANIFEST.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _live_hashes() -> dict[str, str]:
    files = ["set.json"] + sorted(
        str(p.relative_to(HOLDOUT)).replace("\\", "/")
        for p in (HOLDOUT / "docs").glob("*")
        if p.is_file()
    )
    out: dict[str, str] = {}
    for rel in files:
        out[rel] = _sha256(HOLDOUT / rel)
    return out


def main() -> int:
    if not MANIFEST.exists():
        print(f"MISSING {MANIFEST} — run scripts/freeze_holdout.py after labelling")
        return 1

    pinned = json.loads(MANIFEST.read_text())
    expected = pinned.get("files") or {}
    live = _live_hashes()

    missing = sorted(set(expected) - set(live))
    extra = sorted(set(live) - set(expected))
    drift = sorted(k for k in expected if k in live and expected[k] != live[k])

    if not missing and not extra and not drift:
        print(f"HOLDOUT OK — {len(expected)} files match MANIFEST (frozen {pinned.get('frozen_at', '?')})")
        return 0

    print("HOLDOUT DRIFT — labels or fixtures moved after freeze")
    for k in missing:
        print(f"  missing: {k}")
    for k in extra:
        print(f"  extra:   {k}")
    for k in drift:
        print(f"  drift:   {k}")
        print(f"           pinned={expected[k][:16]}… live={live[k][:16]}…")
    print("Fix: revert holdout files or re-freeze with scripts/freeze_holdout.py after review.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
