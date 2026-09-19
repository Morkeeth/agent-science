#!/usr/bin/env python3
"""Offline controls for partner honesty classify — no network, no keys.

Watches the sealed-vs-soft distinction go RED when Parallel is flat.
A soft flat (B == A Parallel with corpus hits) must never be labeled STRICT_DROP.
"""
from __future__ import annotations

import sys


def classify(ap: int, bp: int, bh: int) -> str:
    """Sealed prediction wants STRICT_DROP. Soft verify accepts NON_INCREASE."""
    if ap < 1:
        return "NO_PARALLEL_ON_A"
    if bh < 1:
        return "NO_CORPUS_HIT"
    if bp < ap:
        return "STRICT_DROP"
    if bp <= ap:
        return "SOFT_PASS_FLAT"  # B == A Parallel; hits only — sealed miss
    return "PARALLEL_INCREASE"


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

    if classify(1, 1, 1) == "STRICT_DROP":
        print("FAIL  soft flat must not classify as STRICT_DROP")
        failed += 1
    else:
        print("PASS  soft flat is not STRICT_DROP")

    total = len(cases) + 1
    print(f"\n{total - failed}/{total} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
