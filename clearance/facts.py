"""The FACT leg — same engine, same guard, same report, different noun.

A factual claim is cleared exactly the way an asset is: you name the document,
you fetch it, you quote the sentence, or you print that you could not.

The predicate is deliberately dumb and deliberately stated: SOURCED means
"this document contains this string". It does NOT mean the claim is true. A
clearance desk needs a citable source, not a verdict on reality, and pretending
otherwise is how a fact-checker becomes an oracle nobody can audit.
"""
from __future__ import annotations

import re
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

    # Every occurrence, not just the first. Checking only body.find() produced a
    # FALSE UNKNOWN on EUR-Lex: the phrase's first appearance is a navigation label,
    # and the real titling sentence is further down the same page. A wrong refusal
    # is not "the safe direction" - it is the same defect facing the other way.
    occurrences = []
    probe = at
    while probe >= 0:
        occurrences.append(probe)
        probe = body.find(claim.must_contain, probe + 1)
    passage = _passage(body, occurrences, len(claim.must_contain))
    if passage is None:
        # The string occurs, but no readable passage carries it — it is sitting in
        # navigation, a table of contents, or a link label. A GREEN whose evidence
        # does not read as a statement is the substitution defect in its last
        # costume: a real document, a real quote, and no relationship between the
        # quote and the claim. Refuse the GREEN.
        return unknown(
            "the string occurs in the source but not inside a readable statement",
            SOURCE_SILENT, citation_url=claim.source_url,
            quoted_terms=(f"document opened, {len(body):,} characters read; "
                          f'"{claim.must_contain}" occurs only outside prose '
                          "(navigation, index or link text)"))
    return Verdict(
        subject_id=claim.claim_id, subject_title=claim.text, noun=FACT,
        use=SOURCING, verdict=GREEN,
        reason="the named source states this in these words",
        citation_url=claim.source_url, quoted_terms=passage,
    )


# Locating the passage that CARRIES a claim.
#
# Two failures shaped this, both found on screen rather than in source:
#   1. an arbitrary character window slices mid-word and drags page chrome in with
#      it, which then prints under the heading "evidence";
#   2. requiring a sentence boundary produced a FALSE UNKNOWN on EUR-Lex, whose
#      headers contain almost no full stops. A wrong refusal is not the safe
#      direction, it is the same defect facing the other way.
_ENDER = re.compile(r"[.!?][\s\u200b]")
_MAX = 320
_WINDOW = 130

# Navigation text that appears verbatim on the pages we read. Quoting it under
# "evidence" is what defect 3 looked like in its last costume. Explainable to a
# lawyer, which a cleverer filter would not be.
_CHROME = ("Skip to main content", "Log in", "table of contents",
           "consolidated versions", "Display Text", "Select ", "My EUR-Lex",
           "recent searches", "Languages, formats and link")


def _prose(passage: str) -> bool:
    if not passage:
        return False
    if not (passage[0].isalnum() or passage[0] in "\"'("):
        return False          # starts mid-word or on punctuation: a slice
    if passage.count(" ") < 6:
        return False          # a run of link labels, not a statement
    return not any(c in passage for c in _CHROME)


def _at(body: str, at: int, span: int) -> Optional[str]:
    """One candidate passage for one occurrence: sentence if there is one, else a
    word-snapped window. Never a mid-word slice."""
    left, right = 0, len(body)
    for m in _ENDER.finditer(body, max(0, at - _MAX), at):
        left = m.end()
    m = _ENDER.search(body, at + span, at + span + _MAX)
    if m:
        right = m.end()

    if right - left > _MAX or left == 0:
        # No usable sentence. Take a window and snap both ends to word boundaries,
        # so the quote can never begin or end inside a word.
        left = max(0, at - _WINDOW)
        right = min(len(body), at + span + _WINDOW)
        while left > 0 and not body[left - 1].isspace():
            left += 1
        while right < len(body) and not body[right].isspace():
            right -= 1
        return _start_of_statement(body[left:right], at - left)
    return body[left:right].strip().strip("\u200b").strip()


def _start_of_statement(window: str, match_offset: int) -> str:
    """Trim a window forward to where the text starts reading like a sentence.

    Needed because pages without full stops (EUR-Lex headers, the language picker
    on rightsstatements.org) give no boundary to anchor on, and a raw window then
    opens with "हिन्दी Hrvatski Italiana Lietuva Dutch Polski Go" printed under the
    word "evidence". The rule is deliberately one a lawyer can check: begin at the
    LAST point, before the match, where a capitalised token is followed by a
    lower-case one — i.e. where prose resumes after a run of labels.
    """
    tokens, pos, starts = window.split(" "), 0, []
    for i, tok in enumerate(tokens[:-1]):
        if pos > match_offset:
            break
        if tok[:1].isupper() and tokens[i + 1][:1].islower():
            starts.append(pos)
        pos += len(tok) + 1
    # EARLIEST viable start, not the latest: taking the last one trimmed
    # "The copyright and related rights status of this Item has not been evaluated"
    # down to "Item has not been evaluated", cutting the subject off its own verb.
    for start in starts:
        cand = window[start:].strip().strip("\u200b").strip()
        if _prose(cand):
            return cand
    return window.strip().strip("\u200b").strip()


def _passage(body: str, occurrences, span: int) -> Optional[str]:
    """The first occurrence that yields a readable, chrome-free statement."""
    for at in occurrences:
        cand = _at(body, at, span)
        if _prose(cand):
            return cand
    return None
