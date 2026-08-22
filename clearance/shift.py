"""Two questions, one corpus — rendered side by side so the shift is visible.

The second use case is not "it produces another number". It is that a DIFFERENT
set of instruments does the blocking. If a reader cannot see that at a glance,
the claim is asserted rather than shown.
"""
from __future__ import annotations

from collections import Counter
from typing import Sequence

from .verdict import Verdict, GREEN, RED, UNKNOWN

_MARK = {GREEN: "CLEARED", RED: "BLOCKED", UNKNOWN: "UNKNOWN"}


def render(a: Sequence[Verdict], b: Sequence[Verdict], *, library: str) -> str:
    use_a, use_b = a[0].use, b[0].use
    m = len(a)
    by_id_b = {v.subject_id: v for v in b}

    def tally(vs):
        c = Counter(v.verdict for v in vs)
        return c[GREEN], c[RED], c[UNKNOWN]

    ga, ra, ua = tally(a)
    gb, rb, ub = tally(b)

    out = [
        f"# SAME LIBRARY, TWO QUESTIONS — {library}",
        "",
        f"{m} items, indexed once. No re-ingest between the two runs: the second "
        "question is answered against instruments already on file.",
        "",
        f"| | `{use_a}` | `{use_b}` |",
        "|---|---:|---:|",
        f"| CLEARED | {ga} | {gb} |",
        f"| BLOCKED | {ra} | {rb} |",
        f"| UNKNOWN | {ua} | {ub} |",
        "",
    ]

    # The point of the page: which instruments block WHICH question.
    inst = {}
    for v in a:
        if v.citation_url:
            inst.setdefault(v.citation_url, {"n": 0, "a": None, "b": None})
            inst[v.citation_url]["n"] += 1
            inst[v.citation_url]["a"] = v.verdict
    for v in b:
        if v.citation_url and v.citation_url in inst:
            inst[v.citation_url]["b"] = v.verdict

    flipped = {k: d for k, d in inst.items() if d["a"] != d["b"]}
    held = {k: d for k, d in inst.items() if d["a"] == d["b"]}

    out += ["## The instruments that change their answer", ""]
    if flipped:
        out += [f"| n | Instrument | `{use_a}` | `{use_b}` |", "|---:|---|---|---|"]
        for k, d in sorted(flipped.items(), key=lambda x: -x[1]["n"]):
            short = k.replace("http://creativecommons.org/licenses/", "CC ") \
                     .replace("http://rightsstatements.org/vocab/", "RS ") \
                     .replace("http://creativecommons.org/publicdomain/", "CC ")
            out.append(f"| {d['n']} | `{short}` | **{_MARK[d['a']]}** | **{_MARK[d['b']]}** |")
        moved = sum(d["n"] for d in flipped.values())
        out += ["", f"**{moved} of {m} items ({moved / m:.0%}) change verdict between the "
                    "two questions, and the change is driven by the instrument's own terms, "
                    "not by a different index.**", ""]
    else:
        out += ["None. Both questions are blocked by the same instruments — which would "
                "mean the second use case adds no new sellable inventory.", ""]

    out += ["## The instruments that hold", ""]
    out += [f"| n | Instrument | both |", "|---:|---|---|"]
    for k, d in sorted(held.items(), key=lambda x: -x[1]["n"]):
        short = k.replace("http://creativecommons.org/licenses/", "CC ") \
                 .replace("http://rightsstatements.org/vocab/", "RS ") \
                 .replace("http://creativecommons.org/publicdomain/", "CC ")
        out.append(f"| {d['n']} | `{short}` | {_MARK[d['a']]} |")
    out.append("")
    return "\n".join(out)
