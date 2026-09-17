#!/usr/bin/env python3
"""Second-buyer shift — re-derive the 247/600 pack claim at its object.

The pitch and SUBMISSION-PACK say ai_training → noncommercial_reuse flips **247 of 600**.
`compare_questions.py` historically compared ai_training → **broadcast** (9 of 600).
Both are real; only one is the pack claim. This script measures BOTH arms so a nearer
proxy cannot silently answer the wrong question.

Population: fixtures/europeana-broad.json (n from file, not carried).
Engine: clearance.engine.judge — offline, no network.

Run: python3 scripts/eval_second_buyer_shift.py
Exit 1 if the noncommercial item-level flip count disagrees with the pack fixture line.
"""
from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from clearance import engine  # noqa: E402
from clearance.gap_report import render as gap_render  # noqa: E402
from clearance.shift import render as shift_render  # noqa: E402
from clearance.sources import europeana  # noqa: E402
from clearance.verdict import GREEN, RED, UNKNOWN  # noqa: E402

FIXTURE = "europeana-broad.json"
PACK_SHIFT = ROOT / "fixtures/shift-ai-training-vs-noncommercial.md"
PACK_GAP = ROOT / "fixtures/gap-report-600.md"


def _judge_all(items, use: str):
    return [
        engine.judge(
            subject_id=i["subject_id"],
            subject_title=i["subject_title"],
            instrument_uri=i["instrument_uri"],
            use=use,
            holder=i["holder"],
        )
        for i in items
    ]


def _tally(vs):
    c = Counter(v.verdict for v in vs)
    return c[GREEN], c[RED], c[UNKNOWN]


def _item_flips(a, b) -> int:
    return sum(1 for x, y in zip(a, b) if x.verdict != y.verdict)


def _fixture_claimed_flips(path: Path) -> int | None:
    text = path.read_text()
    m = re.search(r"\*\*(\d+) of (\d+) items", text)
    if not m:
        return None
    return int(m.group(1))


def _fixture_claimed_blocked(path: Path) -> tuple[int, int] | None:
    text = path.read_text()
    m = re.search(r"\*\*(\d+) of (\d+) \(\d+%\)", text)
    if not m:
        return None
    return int(m.group(1)), int(m.group(2))


def main() -> int:
    items = europeana.load_fixture(FIXTURE)
    n = len(items)
    print("SECOND-BUYER SHIFT EVAL — europeana-broad at object")
    print(f"Population: {FIXTURE} n={n}")
    print()

    ai = _judge_all(items, engine.AI_TRAINING)
    nc = _judge_all(items, engine.NONCOMMERCIAL_REUSE)
    bc = _judge_all(items, engine.BROADCAST)

    g, r, u = _tally(ai)
    blocked = r + u
    print("ARM A — ai_training (gap report population)")
    print(f"  GREEN={g}  RED={r}  UNKNOWN={u}  blocked={blocked}/{n} ({blocked/n:.0%})")

    flips_nc = _item_flips(ai, nc)
    flips_bc = _item_flips(ai, bc)
    print()
    print("SECOND-QUESTION ARMS (item-level verdict flips vs ai_training)")
    print(f"  {'arm':<22} {'flips':>6}  {'share':>6}  note")
    print(
        f"  {'NONCOMMERCIAL_REUSE':<22} {flips_nc:>6}  {flips_nc/n:>5.0%}  "
        f"pack / pitch claim"
    )
    print(
        f"  {'BROADCAST':<22} {flips_bc:>6}  {flips_bc/n:>5.0%}  "
        f"former compare_questions.py default (nearer proxy)"
    )
    print()

    # Instrument-level render for pack arm (shift.py sums flipped instruments)
    report_nc = shift_render(ai, nc, library="Europeana · 600 moving-image items")
    for line in report_nc.splitlines():
        if "change verdict" in line or line.startswith("| CLEARED"):
            print(f"  shift.py: {line}")

    claimed_flips = _fixture_claimed_flips(PACK_SHIFT)
    claimed_gap = _fixture_claimed_blocked(PACK_GAP)
    print()
    print("FIXTURE CROSS-CHECK")
    print(f"  {PACK_SHIFT.name} claims flips={claimed_flips}")
    print(f"  measured NONCOMMERCIAL flips={flips_nc}")
    if claimed_gap:
        print(f"  {PACK_GAP.name} claims blocked={claimed_gap[0]}/{claimed_gap[1]}")
        print(f"  measured ai_training blocked={blocked}/{n}")

    findings = []
    if flips_bc < flips_nc:
        findings.append(
            f"NEARER-PROXY TRAP: BROADCAST flips only {flips_bc}/{n} ({flips_bc/n:.0%}) "
            f"while NONCOMMERCIAL flips {flips_nc}/{n} ({flips_nc/n:.0%}). "
            f"compare_questions.py historically defaulted to broadcast — fixed 2026-09-17 "
            f"to default noncommercial_reuse; pass `broadcast` for the old arm."
        )
    if claimed_flips is not None and claimed_flips != flips_nc:
        findings.append(
            f"STALE FIXTURE: {PACK_SHIFT.name} says {claimed_flips}, engine says {flips_nc}"
        )
    if claimed_gap and (claimed_gap[0] != blocked or claimed_gap[1] != n):
        findings.append(
            f"STALE GAP: {PACK_GAP.name} says {claimed_gap}, engine says {blocked}/{n}"
        )
    if not findings:
        findings.append(
            f"Pack claims hold at object: blocked {blocked}/{n}; "
            f"noncommercial flips {flips_nc}/{n}."
        )

    print()
    print("FINDING:")
    for f in findings:
        print(f"  - {f}")

    # Write a machine receipt next to other eval outputs (not into frozen corpus).
    out = ROOT / "docs/RECEIPT-second-buyer-shift-2026-09-17.md"
    out.write_text(
        "\n".join(
            [
                "# RECEIPT — second-buyer shift re-measure · 2026-09-17",
                "",
                f"Population: `{FIXTURE}` n={n}",
                "",
                f"| Use | GREEN | RED | UNKNOWN | blocked |",
                f"|---|---:|---:|---:|---:|",
                f"| ai_training | {g} | {r} | {u} | {blocked} |",
                f"| noncommercial_reuse | {_tally(nc)[0]} | {_tally(nc)[1]} | {_tally(nc)[2]} | {_tally(nc)[1]+_tally(nc)[2]} |",
                f"| broadcast | {_tally(bc)[0]} | {_tally(bc)[1]} | {_tally(bc)[2]} | {_tally(bc)[1]+_tally(bc)[2]} |",
                "",
                f"Item-level flips vs ai_training: **noncommercial={flips_nc}** · **broadcast={flips_bc}**",
                "",
                "Command: `python3 scripts/eval_second_buyer_shift.py`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(f"\nWrote {out.relative_to(ROOT)}")

    if claimed_flips is not None and claimed_flips != flips_nc:
        return 1
    if claimed_gap and (claimed_gap[0] != blocked or claimed_gap[1] != n):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
