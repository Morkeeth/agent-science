#!/usr/bin/env python3
"""Offline controls for partner honesty classify — no network, no keys.

Watches the sealed-vs-soft distinction go RED when Parallel is flat.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

SPEC = importlib.util.spec_from_file_location(
    "partner_honesty_exhibit",
    ROOT / "scripts" / "partner_honesty_exhibit.py",
)
mod = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(mod)
classify = mod._classify


def main() -> int:
    cases = [
        # ap, bp, bh, expected
        (2, 1, 1, "STRICT_DROP"),
        (1, 0, 1, "STRICT_DROP"),
        (1, 1, 1, "SOFT_PASS_FLAT"),
        (2, 2, 1, "SOFT_PASS_FLAT"),
        (1, 2, 1, "PARALLEL_INCREASE"),
        (0, 0, 1, "NO_PARALLEL_ON_A"),
        (2, 1, 0, "NO_CORPUS_HIT"),
    ]
    failed = 0
    for ap, bp, bh, expected in cases:
        got = classify(ap, bp, bh)
        ok = got == expected
        print(f"{'PASS' if ok else 'FAIL'}  classify({ap},{bp},{bh}) -> {got} (want {expected})")
        if not ok:
            failed += 1

    # Control: soft-pass must not be labeled STRICT_DROP (the greenwash we catch).
    if classify(1, 1, 1) == "STRICT_DROP":
        print("FAIL  soft flat must not classify as STRICT_DROP")
        failed += 1
    else:
        print("PASS  soft flat is not STRICT_DROP")

    print(f"\n{len(cases) + 1 - failed}/{len(cases) + 1} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
