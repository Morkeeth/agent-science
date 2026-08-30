#!/usr/bin/env python3
"""Shared statistics for refusal-correctness eval arms (n<100 gate).

Wilson score interval for binomial proportion; McNemar exact test for paired
binary outcomes. No scipy dependency — stdlib math only.

Run via eval_refusal_baseline.py / eval_refusal_ablation.py (imported).
"""
from __future__ import annotations

import math
from typing import Sequence


def wilson_ci(correct: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """95% Wilson score interval for proportion correct."""
    if n == 0:
        return 0.0, 0.0
    p = correct / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    margin = z * math.sqrt((p * (1 - p) + z * z / (4 * n)) / n) / denom
    return max(0.0, centre - margin), min(1.0, centre + margin)


def mcnemar_exact(b_win: int, c: int) -> tuple[float, str]:
    """McNemar exact test on discordant pairs.

    b_win = count where arm1 correct and arm2 wrong
    c     = count where arm1 wrong and arm2 correct
    Returns (two-sided p-value, interpretation string).
    """
    n_disc = b_win + c
    if n_disc == 0:
        return 1.0, "no discordant pairs — arms identical on every item"
    # Two-sided exact: 2 * min(P(X<=min(b,c)), P(X>=max(b,c))) with X~Binom(n_disc, 0.5)
    k = min(b_win, c)

    def binom_pmf(i: int) -> float:
        return math.comb(n_disc, i) * (0.5 ** n_disc)

    p_lower = sum(binom_pmf(i) for i in range(0, k + 1))
    p_upper = sum(binom_pmf(i) for i in range(n_disc - k, n_disc + 1))
    p = min(1.0, 2 * min(p_lower, p_upper))
    return p, f"b={b_win} c={c} discordant"


def format_ci(correct: int, n: int) -> str:
    lo, hi = wilson_ci(correct, n)
    return f"{correct}/{n} = {correct/n:.3f}  95% CI [{lo:.3f}, {hi:.3f}]"
