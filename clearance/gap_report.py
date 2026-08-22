"""The gap report — what CANNOT be cleared, and why. Printed, never inferred.

The denominator is always visible. "72%" with no M underneath it is a deck slide;
"36 of 50" is a measurement.
"""
from __future__ import annotations

from collections import Counter
from typing import Sequence

from .verdict import Verdict, GREEN, RED, UNKNOWN


def render(verdicts: Sequence[Verdict], *, library: str, use: str) -> str:
    m = len(verdicts)
    if m == 0:
        return f"# GAP REPORT — {library}\n\nNo items judged.\n"

    counts = Counter(v.verdict for v in verdicts)
    green, red, unknown = counts[GREEN], counts[RED], counts[UNKNOWN]
    blocked = red + unknown

    out = [
        f"# GAP REPORT — {library}",
        "",
        f"**Question asked:** can these be cleared for `{use}`?",
        f"**Items judged:** {m}",
        "",
        "| Verdict | Count | Share |",
        "|---|---:|---:|",
        f"| CLEARED (GREEN) | {green} | {green / m:.0%} |",
        f"| BLOCKED (RED) | {red} | {red / m:.0%} |",
        f"| UNKNOWN — no instrument on file | {unknown} | {unknown / m:.0%} |",
        "",
        f"> **{blocked} of {m} ({blocked / m:.0%}) of this library is not sellable as-is.**",
        "",
    ]

    if red:
        out += ["## Blocked, with the instrument that blocks it", ""]
        by_instrument = Counter(
            (v.citation_url, v.reason) for v in verdicts if v.verdict == RED
        )
        out += ["| n | Reason | Instrument |", "|---:|---|---|"]
        for (url, reason), n in by_instrument.most_common():
            out.append(f"| {n} | {reason} | `{url}` |")
        out.append("")

    if unknown:
        out += [
            "## Unknown — the honest column",
            "",
            f"{unknown} item(s) carry no rights instrument we can read. These are printed "
            "UNKNOWN, never assumed cleared. Each one is a question for the rights-holder, "
            "and together they are the first page of the clearance backlog.",
            "",
        ]

    interp = [v for v in verdicts if v.interpretive]
    if interp:
        out += [
            "## Flagged as interpretation, not text",
            "",
            f"{len(interp)} verdict(s) rest on a legal reading rather than the instrument's "
            "plain words (e.g. whether training on a work creates a derivative). Marked so "
            "counsel can overrule them.",
            "",
        ]

    out += ["## Evidence", "", "Every non-UNKNOWN verdict above cites a dereferenceable "
            "instrument and quotes its operative clause verbatim. Sample:", ""]
    for v in verdicts:
        if v.verdict in (GREEN, RED):
            out += [
                f"- **{v.subject_title[:70]}** — {v.verdict}",
                f"  - instrument: {v.citation_url}",
                f'  - terms: "{(v.quoted_terms or "")[:180]}…"',
            ]
            break
    out.append("")
    return "\n".join(out)
