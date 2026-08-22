"""The gap report — what CANNOT be cleared, and why. Printed, never inferred.

The denominator is always visible. "72%" with no M underneath it is a deck slide;
"36 of 50" is a measurement.
"""
from __future__ import annotations

from collections import Counter
from typing import Sequence

from .verdict import (Verdict, GREEN, RED, UNKNOWN,
                      NO_INSTRUMENT, UNRULED, UNREAD_TERMS, NOT_EVALUATED)


# The number was always right and the SENTENCE was generic. "Not sellable as-is" is a
# stock-library phrase; the question actually asked is which use is blocked, and for
# ai_training the answer is the one that matters commercially right now - a licence to
# put a clip in a film is not permission to put it in a model, and that distinction is
# months old in the industry and unautomated.
_HEADLINE = {
    "ai_training": "of this library CANNOT LEGALLY BE USED TO TRAIN A MODEL.",
    "commercial_license": "of this library cannot be commercially licensed as-is.",
    "broadcast": "of this library cannot be broadcast or reused as-is.",
    "noncommercial_reuse": "of this library is closed even to non-commercial reuse.",
}


def _headline(use: str) -> str:
    return _HEADLINE.get(use, "of this library is not clearable as-is.")


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
        f"| UNKNOWN — did not resolve | {unknown} | {unknown / m:.0%} |",
        "",
        f"> **{blocked} of {m} ({blocked / m:.0%}) {_headline(use)}**",
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
        # Splitting this was a real fix. Rendered as one blob it read "no rights
        # instrument we can read", which billed OUR unruled backlog to the archive.
        # Three different facts, three different owners, three different next actions.
        by_cause = {c: [v for v in verdicts if v.verdict == UNKNOWN and v.cause == c]
                    for c in (NO_INSTRUMENT, NOT_EVALUATED, UNRULED, UNREAD_TERMS)}
        out += ["## Unknown — the honest column", "",
                f"{unknown} of {m} items did not resolve. They are printed UNKNOWN and never "
                "assumed cleared. They are not one problem:", "",
                "| n | What is actually true | Whose move |", "|---:|---|---|"]
        labels = {
            NO_INSTRUMENT: ("the holder published no rights instrument at all",
                            "the archive"),
            NOT_EVALUATED: ("the holder states copyright was **never evaluated**",
                            "the archive"),
            UNRULED: ("the holder published an instrument **we have not ruled yet**",
                      "**ours**"),
            UNREAD_TERMS: ("we hold a rule but have **never read** the instrument",
                           "**ours**"),
        }
        for c, group in by_cause.items():
            if group:
                what, whose = labels[c]
                out.append(f"| {len(group)} | {what} | {whose} |")
        out.append("")

        ours = len(by_cause[UNRULED]) + len(by_cause[UNREAD_TERMS])
        theirs = len(by_cause[NO_INSTRUMENT]) + len(by_cause[NOT_EVALUATED])
        parts = []
        if theirs:
            parts.append(
                f"**{theirs} are the archive's gap** — each is a question for the "
                "rights-holder, and together they are page one of the clearance backlog.")
        if ours:
            parts.append(
                f"**{ours} are ours** — coverage we close by ruling the instrument. "
                "Reporting our own backlog as the archive's silence would be a lie the "
                "reader cannot detect, so it is split out here.")
        else:
            parts.append("**None are ours**: every instrument these items published has "
                         "been ruled and read.")
        out += [" ".join(parts), ""]
        if by_cause[UNRULED]:
            seen = Counter(v.reason.split(": ", 1)[-1] for v in by_cause[UNRULED])
            out += ["Instruments we owe a ruling on:", ""]
            out += [f"- `{u}` — {n} item(s)" for u, n in seen.most_common()]
            out.append("")
        if by_cause[NOT_EVALUATED]:
            ex = by_cause[NOT_EVALUATED][0]
            if ex.citation_url:
                out += ["The 'never evaluated' statement is itself cited, not assumed:", "",
                        f"- instrument: {ex.citation_url}",
                        f'- terms: "{(ex.quoted_terms or "")[:200]}…"', ""]

    subs = [v for v in verdicts if v.substituted]
    if subs:
        out += ["## Terms read from a sibling document", "",
                f"{len(subs)} verdict(s) quote a different URL than the archive published "
                "(same licence, different version or language). Named here because quoting "
                "one document while citing another is the exact substitution this product "
                "exists to catch.", ""]
        for v in subs[:5]:
            out.append(f"- published `{v.published_instrument}` → read `{v.citation_url}`")
        out.append("")

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


def mixed(verdicts, *, production: str) -> str:
    """Facts and assets in ONE report, out of one engine.

    Rendered together deliberately. If the two legs need two reports, they are two
    products with a shared README, and the 'same record, different noun' claim is
    marketing.
    """
    from .verdict import FACT, ASSET

    facts = [v for v in verdicts if v.noun == FACT]
    assets = [v for v in verdicts if v.noun == ASSET]
    n = len(verdicts)
    blocked = [v for v in verdicts if v.verdict != GREEN]

    out = [f"# CLEARANCE REPORT — {production}", "",
           f"{len(facts)} factual claim(s) and {len(assets)} asset(s), judged by one "
           "engine against one rule: cite the document or print that you could not.", "",
           "| | Cleared | Not cleared |", "|---|---:|---:|",
           f"| Facts | {sum(1 for v in facts if v.verdict == GREEN)} | "
           f"{sum(1 for v in facts if v.verdict != GREEN)} |",
           f"| Assets | {sum(1 for v in assets if v.verdict == GREEN)} | "
           f"{sum(1 for v in assets if v.verdict != GREEN)} |", "",
           f"> **{len(blocked)} of {n} items block this production.**", "",
           "## Every item that blocks, with the document that decides it", "",
           "| Noun | Item | Verdict | Why | Document |",
           "|---|---|---|---|---|"]
    for v in blocked:
        doc = f"`{v.citation_url}`" if v.citation_url else "—"
        out.append(f"| {v.noun} | {v.subject_title[:46]} | **{v.verdict}** | "
                   f"{v.reason[:64]} | {doc} |")
    out += ["", "## The evidence, verbatim", ""]
    for v in verdicts:
        if v.quoted_terms:
            out += [f"**{v.subject_id} · {v.noun} · {v.verdict}** — {v.citation_url}",
                    f'> "{v.quoted_terms[:200]}…"', ""]
    return "\n".join(out)
