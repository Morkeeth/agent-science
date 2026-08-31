"""The compounding curve — a CITED EXHIBIT, and never confused with the live registry.

This module exists to make one mistake impossible. The curve below was measured on 56
claims across four scripts on one subject. The registry the desk renders beside it is a
DIFFERENT population, seeded from a corpus backfill, and its live reuse counter reads
zero. Printing "reuse compounds 0 → 20 → 39 → 46%" next to a counter that says 0 would be
a sentence the page's own data contradicts — two correct numbers side by side asserting a
relationship neither of them supports.

So the numbers are not literals in a template. They are here, each carrying the
measurement they came from, and `PROVENANCE` travels with them: a control asserts the
curve cannot render on any surface without it.
"""
from __future__ import annotations

from dataclasses import dataclass

SOURCE = "fixtures/compounding/CURVE.md"
POPULATION = "56 claims across 4 independently written scripts on one subject"
MEASURED = "August 2026"
PROVENANCE = (f"Measured on {POPULATION}, run in sequence into one corpus "
              f"({MEASURED}). Source: {SOURCE}. This is NOT the registry below — a "
              f"different population, measured once, not a live counter.")


@dataclass(frozen=True)
class Leg:
    n: int
    script: str
    claims: int
    from_memory: int
    searches: int
    seconds: int
    cost_per_claim: float

    @property
    def reuse(self) -> float:
        return self.from_memory / self.claims if self.claims else 0.0


LEGS = (
    Leg(1, "powered-A-law.txt", 15, 0, 11, 273, 0.00377),
    Leg(2, "documentary-orphan-works.txt", 10, 2, 6, 153, 0.00309),
    Leg(3, "powered-B-archive.txt", 18, 7, 14, 254, 0.00396),
    Leg(4, "documentary-orphan-works-B.txt", 13, 6, 9, 198, 0.00352),
)

CUMULATIVE = (sum(l.from_memory for l in LEGS), sum(l.claims for l in LEGS))

# The finding that is worth more than the curve, and the reason the product is an
# instrument rather than a discount: reuse rises and the per-claim bill does not.
WHAT_IS_TRUE = ("Reuse compounds, monotonically: "
                + " → ".join(f"{l.reuse:.0%}" for l in LEGS)
                + f". Cumulative {CUMULATIVE[0]} of {CUMULATIVE[1]} "
                + f"= {CUMULATIVE[0] / CUMULATIVE[1]:.0%}.")

WHAT_IS_NOT_TRUE = (
    f"Cost per claim does NOT fall: ${LEGS[0].cost_per_claim:.5f} → "
    f"${LEGS[-1].cost_per_claim:.5f}, flat. Searches per claim is flat too "
    f"({LEGS[0].searches / LEGS[0].claims:.2f} → "
    f"{LEGS[-1].searches / LEGS[-1].claims:.2f}).")

WHY = ("Reuse rises and cost does not, because the corpus removes the EASY claims "
       "first. What is left after reuse is a residue of hard ones — the claims that "
       "need escalation to a primary source. Each production therefore checks a higher "
       "proportion of difficult claims than the one before, and the per-claim spend "
       "holds while the hit rate climbs. The saving is in claims nobody has to chase by "
       "hand, not in the API bill.")
