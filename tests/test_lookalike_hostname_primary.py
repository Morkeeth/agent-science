"""Lookalike hostnames must never classify as PRIMARY.

Fails on main's substring host matcher (example.gov.attacker.invalid → primary).
Passes after the PR2 hostname-boundary fix (exact/suffix domain match only).
"""
from clearance.independence import classify

LOOKALIKE = "https://example.gov.attacker.invalid/report"


def test_lookalike_never_primary():
    cls, why = classify(LOOKALIKE)
    assert cls != "primary", f"lookalike must not be PRIMARY, got {cls!r} ({why})"


if __name__ == "__main__":
    test_lookalike_never_primary()
    print("PASS")
