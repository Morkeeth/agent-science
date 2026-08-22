"""DISPUTED — a fetched document says the opposite.

The fourth verdict, and the last one to exist, because for most of this build the
engine had no state behind the word. A vocabulary must not be able to say more than
the engine can prove.

**The rule does not bend here.** The model still only LOCATES: it proposes a passage it
believes conflicts with the claim, and the VALUE in that passage occupying the same slot
as the claim's required terms. `verify` then proves the passage is verbatim in the
fetched document. Two structural facts must both hold before DISPUTED is emitted:

    1. the claim's own required terms are ABSENT from the document, and
    2. a verbatim passage in that document carries a conflicting value in the same slot

If either fails, this is not a dispute — it is an UNSOURCED, and it says so.

The contradiction READING is ours, not the document's, so every DISPUTED is flagged
`interpretive`. A lawyer can overrule it; a judge can see we did not hide it.
"""
from __future__ import annotations

import json
from typing import Optional

from .gemini import MAX_DOC, call
from .verdict import Verdict, DISPUTED, FACT
from .verify import verify

_INSTRUCTION = """You look for CONTRADICTION. You never decide truth.

Given a DOCUMENT, a CLAIM and the claim's REQUIRED TERMS, find the single shortest
contiguous passage from the DOCUMENT that states something INCOMPATIBLE with the claim
in the same slot — a different date where the claim gives a date, a different quantity
where it gives a quantity, a different actor where it names one.

Rules, all hard:
- The passage must be copied EXACTLY from the DOCUMENT, character for character.
- Also return `conflicting_value`: the exact substring of that passage which occupies
  the same slot as the claim's required terms. It must appear verbatim in the passage.
- A passage that is merely about the same topic is NOT a contradiction. Return null.
- A passage that is silent on the point is NOT a contradiction. Return null.
- Returning null is correct and expected.

Reply with JSON only:
{"passage": "<exact text>", "conflicting_value": "<exact substring>"} or {"passage": null}
"""


def find_contradiction(*, claim: str, must_contain: str, document: str,
                       source_url: str, model: str = "gemini-3.5-flash-lite",
                       claim_id: str = "?") -> Optional[Verdict]:
    """A DISPUTED verdict, or None if the document does not contradict the claim."""
    # STRUCTURAL PRECONDITION. If the document DOES carry the claim's own terms, it
    # supports the claim; asking a model whether it also contradicts it invites a
    # confident wrong answer on a claim we can already resolve.
    if must_contain in document:
        return None

    user = (f"CLAIM:\n{claim}\n\nREQUIRED TERMS (absent from the document):\n"
            f"{must_contain}\n\nDOCUMENT:\n{document[:MAX_DOC]}")
    payload, answered = call(model, _INSTRUCTION, user)
    try:
        raw = json.loads(payload["candidates"][0]["content"]["parts"][0]["text"])
        passage, value = raw.get("passage"), raw.get("conflicting_value")
    except (KeyError, IndexError, ValueError, TypeError):
        return None
    if not passage or not value:
        return None

    # The passage must be real. Same verifier, no exception, no softer path.
    if verify(passage, document=document, must_contain=value) is not None:
        return None
    return Verdict(
        subject_id=claim_id, subject_title=claim, noun=FACT, use="sourcing",
        verdict=DISPUTED,
        reason=(f"a fetched document states {value!r} where the claim requires "
                f"{must_contain!r} (locator: {answered})"),
        citation_url=source_url, quoted_terms=passage.strip(), interpretive=True,
    )
