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

from . import semantic as _semantic

MIN_WORDS = 7
MIN_SENTENCE_WORDS = 4   # a short passage that ENDS as a sentence is still a statement
MAX_CHARS = 400


@dataclass(frozen=True)
class Refusal:
    code: str
    detail: str


def verify(passage: Optional[str], *, document: str, must_contain: str,
           claim: Optional[str] = None,
           semantic: Optional[bool] = None) -> Optional[Refusal]:
    """None if the passage is admissible evidence, else why it is refused.

    `claim` is the assertion the passage is offered in support of. It is OPTIONAL and it
    defaults to None because for most of this build it did not exist here at all — and
    that absence, not a missing cleverness, is why a verbatim span whose own sentence
    disowned the claim was cleared GREEN for eight days. A guard cannot read a claim it
    is never given. Passing it opens the semantic guard (`clearance.semantic`), which may
    only ever DEMOTE: every structural refusal above still fires first and unchanged.
    """
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
    # The word floor exists to reject runs of link labels. It was rejecting SHORT
    # COMPLETE SENTENCES too — "Done at Strasbourg, 25 October 2012." is six words, is
    # the decisive line of an EU directive, and was refused as decor. That is the
    # false-refusal direction this product is most likely to drift in, caught on the
    # first real contradiction the engine ever found.
    #
    # A run of labels has no terminal punctuation. A sentence does. So: long enough,
    # OR short but visibly a sentence.
    words = p.count(" ") + 1
    ends_as_sentence = p.rstrip().endswith((".", "!", "?", '."', ".'"))
    if words < MIN_WORDS and not (ends_as_sentence and words >= MIN_SENTENCE_WORDS):
        return Refusal("not_a_statement",
                       f"{words} words and no sentence ending — a run of labels")
    if len(p) > MAX_CHARS:
        return Refusal("not_a_statement", f"{len(p)} characters — a page, not a passage")

    # 4. THE SEMANTIC GUARD. Everything above proves the passage is REAL and MENTIONS the
    #    claim's distinctive term. None of it can prove the passage ASSERTS the claim,
    #    and no amount of structure ever will: that is a relation between two texts, and
    #    until this parameter existed only one of them was in the room.
    use_guard = _semantic.enabled() if semantic is None else semantic
    if claim and use_guard:
        finding = _semantic.inspect(p, claim=claim, must_contain=must_contain)
        if finding is not None:
            return Refusal(finding.code, finding.detail)

    return None
