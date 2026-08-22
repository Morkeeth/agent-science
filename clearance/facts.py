"""The FACT leg — same engine, same guard, same report, different noun.

A factual claim is cleared exactly the way an asset is: you name the document,
you fetch it, you quote the sentence, or you print that you could not.

The predicate is deliberately dumb and deliberately stated: SOURCED means
"this document contains this string". It does NOT mean the claim is true. A
clearance desk needs a citable source, not a verdict on reality, and pretending
otherwise is how a fact-checker becomes an oracle nobody can audit.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from . import instruments
from .verdict import (Verdict, GREEN, UNKNOWN, FACT,
                      NO_SOURCE, SOURCE_UNREAD, SOURCE_SILENT)

SOURCING = "sourcing"  # the "use" a fact is judged for


@dataclass(frozen=True)
class Claim:
    claim_id: str
    text: str                 # the assertion as it appears in the script
    source_url: Optional[str] # the document offered in support
    must_contain: str         # the exact string that document must carry


def judge_claim(claim: Claim, *, fetch: bool = False) -> Verdict:
    def unknown(reason: str, cause: str, **kw) -> Verdict:
        return Verdict(subject_id=claim.claim_id, subject_title=claim.text,
                       noun=FACT, use=SOURCING, verdict=UNKNOWN,
                       reason=reason, cause=cause, **kw)

    if not claim.source_url:
        return unknown("no source offered for this claim", NO_SOURCE)

    body = instruments.document(claim.source_url, fetch=fetch)
    if body is None:
        return unknown(
            f"source {claim.source_url} has never been fetched — "
            "no text on file to quote", SOURCE_UNREAD)

    at = body.find(claim.must_contain)
    if at < 0:
        # We read the document and it does not say it. Evidence of absence, so the
        # document is cited — the same narrow rule the asset leg uses for CNE.
        # Quoting the first 240 characters here was a defect found on screen: it
        # printed navigation furniture under the heading "quote", which reads as
        # evidence and is not. The honest quotation for a non-finding is a stated,
        # checkable fact ABOUT the document, not an arbitrary slice OF it.
        return unknown(
            "the source was read and does not state this claim", SOURCE_SILENT,
            citation_url=claim.source_url,
            quoted_terms=(f"document opened, {len(body):,} characters read; "
                          f'the phrase "{claim.must_contain}" does not occur in it'))

    start = max(0, at - 90)
    return Verdict(
        subject_id=claim.claim_id, subject_title=claim.text, noun=FACT,
        use=SOURCING, verdict=GREEN,
        reason="the named source states this in these words",
        citation_url=claim.source_url,
        quoted_terms=body[start:at + len(claim.must_contain) + 90].strip(),
    )
