#!/usr/bin/env python3
"""Holdout frozen gate — set.json hash must match FROZEN manifest before eval tuning.

Qwen PRIOR LOSS gate: holdout frozen before the first tuning pass.

Run: python3 scripts/eval_holdout_frozen.py
Exit 0 when fixtures/refusal-correctness/set.json matches FROZEN.json.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SET = ROOT / "fixtures/refusal-correctness/set.json"
FROZEN = ROOT / "fixtures/refusal-correctness/FROZEN.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    if not SET.exists():
        print(f"FAIL  missing {SET}")
        return 1
    if not FROZEN.exists():
        print(f"FAIL  missing {FROZEN} — holdout not frozen")
        return 1

    manifest = json.loads(FROZEN.read_text())
    data = json.loads(SET.read_text())
    digest = _sha256(SET)

    errors: list[str] = []
    if digest != manifest.get("set_sha256"):
        errors.append(f"set.json sha256 mismatch: manifest={manifest.get('set_sha256')} actual={digest}")
    if data.get("labelled_at") != manifest.get("labelled_at"):
        errors.append(
            f"labelled_at drift: manifest={manifest.get('labelled_at')} set={data.get('labelled_at')}"
        )
    if len(data.get("items", [])) != manifest.get("item_count"):
        errors.append(
            f"item_count drift: manifest={manifest.get('item_count')} actual={len(data.get('items', []))}"
        )
    if not data.get("labelled_by"):
        errors.append("set.json missing labelled_by")

    print("HOLDOUT FROZEN GATE — refusal-correctness/set.json")
    print(f"  sha256:     {digest}")
    print(f"  labelled:   {data.get('labelled_at')} by {data.get('labelled_by')}")
    print(f"  items:      {len(data.get('items', []))}")
    print(f"  frozen_at:  {manifest.get('frozen_at')}")
    print()

    if errors:
        print("FAIL — holdout not frozen (tuning must stop until manifest updated deliberately):")
        for e in errors:
            print(f"  · {e}")
        return 1

    print("PASS — holdout matches FROZEN manifest; safe to score eval arms.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
