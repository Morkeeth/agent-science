"""Review-lane: presentation mapping table from build-lane ruling (CURSOR-LOG).

Does not import gap_report — checks the mapping logic is consistent with
check_pitch outcomes and engine causes. Read-only audit.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from check_pitch import CLAIMS
from clearance.facts import judge_claim

# Build-lane ruling in CURSOR-LOG 2026-08-22
def present(verdict: str, cause: str | None) -> str:
    if verdict == "GREEN":
        return "SOURCED"
    if verdict != "UNKNOWN":
        return verdict  # RED -> BLOCKED for assets; facts rarely RED
    if cause in ("no_source_offered", "search_found_no_admissible_source",
                 "source_does_not_state_it"):
        return "UNSOURCED"
    if cause in ("source_never_fetched", "unruled_instrument"):
        return "OURS (backlog)"
    if cause == "no_instrument":
        return "ARCHIVE GAP"
    if cause == "holder_states_not_evaluated":
        return "ARCHIVE GAP (cited)"
    return f"UNKNOWN/{cause}"


def main() -> None:
    print("=== Presentation map on live check_pitch claims ===\n")
    for c in CLAIMS:
        v = judge_claim(c)
        label = present(v.verdict, v.cause)
        print(f"{c.claim_id}  engine={v.verdict}/{v.cause}  ->  {label}")
        if c.claim_id == "C3" and v.verdict == "GREEN":
            print("      NOTE: claim text misattributes holder; quote is status sentence")
            print("      (semantic drift — pinned in t_the_verifier_cannot_read_meaning)")


if __name__ == "__main__":
    main()
