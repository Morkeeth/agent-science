#!/usr/bin/env python3
"""RED-watched: compound receipt must not carry a hardcoded SOURCED count.

Watched 2026-09-17: scripts/compound_exhibit_receipt.py printed
`(29 SOURCED + proven-unprovable refusals)` while refusal_log.stats() said
cleared=25. A carried figure is not a measurement.

Run: python3 tests/test_compound_receipt_counts.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "scripts/compound_exhibit_receipt.py"


def test_no_hardcoded_sourced_parenthetical() -> None:
    text = SRC.read_text()
    # Forbidden: literal "(N SOURCED" with a digit baked into the template.
    bad = re.findall(r"\(\d+\s+SOURCED", text)
    assert not bad, (
        f"{SRC.name} still carries a hardcoded SOURCED count {bad}; "
        "re-derive from refusal_log.stats()['cleared']"
    )


def test_receipt_uses_stats_cleared() -> None:
    text = SRC.read_text()
    assert "backfill_stats" in text
    assert 'backfill_stats.get("cleared"' in text or "backfill_stats.get('cleared'" in text


def main() -> int:
    fails = 0
    tests = sorted(
        (n, f) for n, f in globals().items() if n.startswith("test_") and callable(f)
    )
    for name, fn in tests:
        try:
            fn()
            print(f"  PASS  {name}")
        except AssertionError as e:
            fails += 1
            print(f"  FAIL  {name}: {e}")
    total = len(tests)
    print(f"{total - fails}/{total} passed")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
