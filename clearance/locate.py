"""Locators — things that PROPOSE a passage. None of them is trusted.

A locator's output is a candidate, never a verdict. Everything here is gated by
`clearance.verify`, so a bad locator degrades to a refusal rather than to a wrong
GREEN. That property is what makes it safe to swap the implementation for a model.

`StringLocator` is the FIRST implementation, not the product. Naming it as one
implementation among others is what stops it pretending to be one.
"""
from __future__ import annotations

import re
from typing import Optional, Protocol


class Locator(Protocol):
    name: str

    def propose(self, *, claim: str, must_contain: str, document: str) -> Optional[str]:
        """A candidate passage from `document` that supports `claim`, or None."""


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
        occurrences, probe = [], document.find(must_contain)
        while probe >= 0:
            occurrences.append(probe)
            probe = document.find(must_contain, probe + 1)
        for at in occurrences:
            cand = self._at(document, at, len(must_contain))
            if self._prose(cand):
                return cand
        return None

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
            left = max(0, at - _WINDOW)
            right = min(len(body), at + span + _WINDOW)
            while left > 0 and not body[left - 1].isspace():
                left += 1
            while right < len(body) and not body[right].isspace():
                right -= 1
            return self._start_of_statement(body[left:right], at - left)
        return body[left:right].strip().strip("​").strip()

    def _start_of_statement(self, window: str, match_offset: int) -> str:
        tokens, pos, starts = window.split(" "), 0, []
        for i, tok in enumerate(tokens[:-1]):
            if pos > match_offset:
                break
            if tok[:1].isupper() and tokens[i + 1][:1].islower():
                starts.append(pos)
            pos += len(tok) + 1
        for start in starts:
            cand = window[start:].strip().strip("​").strip()
            if self._prose(cand):
                return cand
        return window.strip().strip("​").strip()


DEFAULT = StringLocator()
