"""The verifier — a proposed passage is not evidence until it is proved.

This is the half of "the model may only LOCATE evidence, never ASSERT it" that needs
no model. Any proposer — a string matcher today, Gemini tomorrow, a human paralegal —
hands a candidate passage here, and it becomes admissible only if it survives.

Every check is STRUCTURAL. There is deliberately no list of site-specific navigation
strings in this file, and a control test greps this module to keep it that way: a guard
that depends on recognising the chrome of the particular websites we happened to fetch
is overfitted to them, and it fails open on the third site. Those strings belong to one
locator implementation, never to the guard.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

MIN_WORDS = 7
MAX_CHARS = 400


@dataclass(frozen=True)
class Refusal:
    code: str
    detail: str


def verify(passage: Optional[str], *, document: str, must_contain: str) -> Optional[Refusal]:
    """None if the passage is admissible evidence, else why it is refused."""
    if passage is None or not passage.strip():
        return Refusal("no_passage", "the locator proposed nothing")

    p = passage.strip()

    # 1. THE ONE THAT MATTERS. A proposer can produce fluent, plausible, correct-sounding
    #    text that is not in the document. It is evidence only if the document contains
    #    it, character for character. This also catches a real passage lifted from the
    #    WRONG document, which is the substitution defect arriving from a new direction.
    if p not in document:
        return Refusal("not_in_document",
                       f"the proposed passage does not occur in the fetched document "
                       f"({len(document):,} characters); first 60 proposed: {p[:60]!r}")

    # 2. The passage must actually carry the claim's terms, not merely be near them.
    if must_contain not in p:
        return Refusal("does_not_carry_the_claim",
                       f"the passage occurs in the document but does not contain "
                       f"{must_contain!r}")

    # 3. Structural readability. A slice that starts mid-word, or a run of link labels,
    #    reads as evidence and is not.
    if not (p[0].isalnum() or p[0] in "\"'("):
        return Refusal("not_a_statement", f"starts mid-word or on punctuation: {p[:40]!r}")
    if p.count(" ") < MIN_WORDS:
        return Refusal("not_a_statement",
                       f"{p.count(' ') + 1} words — a run of labels, not a statement")
    if len(p) > MAX_CHARS:
        return Refusal("not_a_statement", f"{len(p)} characters — a page, not a passage")

    return None
