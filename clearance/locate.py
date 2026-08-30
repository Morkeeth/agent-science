"""Locators — things that PROPOSE a passage. None of them is trusted.

A locator's output is a candidate, never a verdict. Everything here is gated by
`clearance.verify`, so a bad locator degrades to a refusal rather than to a wrong
GREEN. That property is what makes it safe to swap the implementation for a model.

`StringLocator` is the FIRST implementation, not the product. Naming it as one
implementation among others is what stops it pretending to be one.
"""
from __future__ import annotations

import re
from typing import Iterable, Optional, Protocol


class Locator(Protocol):
    name: str

    def propose(self, *, claim: str, must_contain: str, document: str) -> Optional[str]:
        """A candidate passage from `document` that supports `claim`, or None."""

    def candidates(self, *, claim: str, must_contain: str,
                   document: str) -> Iterable[str]:
        """EVERY passage worth proposing, best first. Optional; `propose` is the first.

        A locator that can only hand over one guess forces the verifier into a false
        choice: accept this span or refuse the claim. Measured on the held-out set, that
        choice was being made wrongly in BOTH directions at once — RC1 and RC2 were
        cleared GREEN on a navigation link and on the wrong sentence, because the term
        occurs twice and the supporting sentence is the SECOND occurrence. They scored as
        correct because the labels record whether the claim is supported, never which
        span supported it. One guess is not a search.
        """


_ENDER = re.compile(r"[.!?][\s​]")
_MAX = 320
_WINDOW = 130

# Site-specific navigation text. This list is OVERFITTED — it was scraped off the two
# sites this run happened to fetch, and it will not know the third one. It lives here,
# inside one implementation, and deliberately NOT in the verifier, which must hold for
# any proposer on any document.
_CHROME = ("Skip to main content", "Log in", "table of contents",
           "consolidated versions", "Display Text", "Select ", "My EUR-Lex",
           "recent searches", "Languages, formats and link", "Hrvatski")


class StringLocator:
    """Exact substring matching plus hand-written prose heuristics.

    Three fixes and one false UNKNOWN went into this, which is the evidence that
    locating a passage is a language problem being solved with `find()`.
    """

    name = "string"

    def propose(self, *, claim: str, must_contain: str, document: str) -> Optional[str]:
        for cand in self.candidates(claim=claim, must_contain=must_contain,
                                    document=document):
            return cand
        return None

    def candidates(self, *, claim: str, must_contain: str, document: str):
        """Every occurrence of the term, in document order, deduplicated."""
        seen, probe = set(), document.find(must_contain)
        while probe >= 0:
            cand = self._at(document, probe, len(must_contain))
            if self._prose(cand) and cand not in seen:
                seen.add(cand)
                yield cand
            probe = document.find(must_contain, probe + 1)

    def _prose(self, passage: str) -> bool:
        if not passage:
            return False
        if not (passage[0].isalnum() or passage[0] in "\"'("):
            return False
        if passage.count(" ") < 6:
            return False
        return not any(c in passage for c in _CHROME)

    def _at(self, body: str, at: int, span: int) -> str:
        left, right = 0, len(body)
        for m in _ENDER.finditer(body, max(0, at - _MAX), at):
            left = m.end()
        m = _ENDER.search(body, at + span, at + span + _MAX)
        if m:
            right = m.end()
        if right - left > _MAX or left == 0:
            # Look back _MAX, not _WINDOW. Measured: at 130 characters the window began
            # inside the word "Member", so the only sentence start it could find was
            # "States", and an EU directive's operative provision was quoted from its
            # second word. The reach has to be at least as long as the sentence you are
            # trying to find the beginning of.
            left = max(0, at - _MAX)
            right = min(len(body), at + span + _WINDOW)
            while right < len(body) and not body[right].isspace():
                right -= 1
            cand = self._start_of_statement(body[left:right], at - left)
            if self._prose(cand):
                return cand
            left = max(0, at - _WINDOW)
            while left > 0 and not body[left - 1].isspace():
                left += 1
            return body[left:right].strip().strip("\u200b").strip()
        return body[left:right].strip().strip("​").strip()

    # Where a SENTENCE starts: a capitalised word after a sentence ender, or straight
    # after a closing tag — which is how a fetched HTML page marks the same thing. Not
    # merely "a capital letter", which matches every proper noun mid-sentence and let the
    # passage begin at "October".
    _SENTENCE_START = re.compile(
        r"(?:^|[.!?][\"'\)\]]?\s+|>\s*|\n\s*)([A-Z][A-Za-z])")

    def _start_of_statement(self, window: str, match_offset: int) -> str:
        """Where the statement begins — not where the whitespace happens to fall.

        The first version required a capitalised token followed by a LOWERCASE one, and
        scanned space-separated tokens. Both assumptions break on the same sentence:
        `Member States shall bring into force…` opens with two capitalised words, so the
        only start it could find was `States`, and the operative provision of an EU
        directive was quoted from its second word. A cited passage that begins mid-subject
        is still verbatim and still wrong — it is a different sentence than the one the
        document contains. Caught by a control that asserts WHICH span cleared the claim,
        not merely that one did.
        """
        # 1. A REAL boundary, if the page has any. Take the LAST one before the match:
        #    that is the sentence the term is actually in. Taking the first quoted from
        #    wherever the window happened to open.
        strict = [m.start(1) for m in self._SENTENCE_START.finditer(window)
                  if m.start(1) <= match_offset]
        for start in reversed(strict):
            cand = window[start:].strip().strip("​").strip()
            if self._prose(cand):
                return cand

        # 2. NO BOUNDARY IN THE PAGE. rightsstatements.org serves its language switcher
        #    and its operative sentence in one unpunctuated run — "…Dutch Polski Go
        #    Copyright Not Evaluated The copyright and related rights status of this Item
        #    has not been evaluated." There is no full stop to find, so the only signal
        #    left is a capitalised word followed by a lowercase one. That is the original
        #    heuristic and it is kept EXACTLY, in forward order, because on text with no
        #    punctuation the widest passage that still reads as prose is the right one —
        #    and because replacing it wholesale silently dropped this document's only
        #    quotable sentence, which is the product's most common real verdict.
        tokens, pos, loose = window.split(" "), 0, []
        for i, tok in enumerate(tokens[:-1]):
            if pos > match_offset:
                break
            if tok[:1].isupper() and tokens[i + 1][:1].islower():
                loose.append(pos)
            pos += len(tok) + 1
        for start in loose:
            cand = window[start:].strip().strip("​").strip()
            if self._prose(cand):
                return cand
        return window.strip().strip("​").strip()


DEFAULT = StringLocator()
