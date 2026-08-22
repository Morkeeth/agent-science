"""Claim extraction — the front of the pipeline, and the second place a model earns it.

Until now a `Claim` arrived already written by a human: someone read the script, decided
what was check-worthy, and phrased the assertion and its key terms. Real input is a
script. Deciding which sentences in prose are checkable factual assertions — and which
are dialogue, stage direction, opinion or scene-setting — is a language problem no regex
touches.

The extractor proposes claims. It does not judge them. Every claim it produces still has
to survive search -> fetch -> locate -> verify, so an over-eager extractor costs UNSOURCED
rows, never false evidence.
"""
from __future__ import annotations

import json
from typing import Optional

from .facts import Claim
from .gemini import MAX_DOC, call

_INSTRUCTION = """You extract check-worthy factual assertions from a documentary script.

Extract ONLY assertions the FILM ITSELF makes as fact, and that a fact-checker could
verify against a document: dates, named attributions, quantities, titles of laws or
works, causal claims about real events.

Do NOT extract:
- dialogue or quoted speech — a person saying something is not the film asserting it
- stage direction, camera direction, scene-setting, description of imagery
- opinion, prediction, rhetorical questions, or value judgements
- vague assertions with nothing checkable in them

Returning an EMPTY list is a correct and expected answer for a passage that contains no
checkable factual assertions. Do not manufacture claims to fill the list.

For each claim give:
  "text"         the assertion, as a standalone sentence a checker can look up
  "must_contain" the shortest distinctive phrase that MUST appear verbatim in any
                 document that supports it — a name, a number, a title, a date. Never a
                 whole sentence, never a common word.
  "kind"         one of: date, attribution, quantity, title, causal

Reply with JSON only: {"claims": [ ... ]}"""


class GeminiExtractor:
    name = "gemini-extractor"

    def __init__(self, model: str = "gemini-3.5-flash", timeout: int = 90):
        self.model, self.timeout = model, timeout

    def extract(self, script: str, *, chunk: bool = True) -> list[Claim]:
        """Extract claims, by default one PASSAGE at a time.

        MEASURED, not assumed: the same 388-word script yields 9 claims in one call and
        19 when its six paragraphs are extracted separately. The ceiling is PER-CALL -
        attention across a long input, not a document or token limit - so a 90-minute
        documentary carrying 200 assertions would have had 10 of them checked, and the
        product would have looked thorough while silently dropping 95% of the film.

        Chunking is therefore not an optimisation. It is the difference between checking
        a script and sampling it.
        """
        if not chunk:
            return self._extract_one(script)
        passages = [p for p in script.split("\n\n") if len(p.strip()) > 60]
        if len(passages) < 2:
            return self._extract_one(script)
        seen, out = set(), []
        for p in passages:
            for c in self._extract_one(p):
                # A claim can appear in two passages; the distinctive term identifies it.
                key = (c.must_contain or "").strip().lower()
                if key and key in seen:
                    continue
                seen.add(key)
                out.append(c)
        return [Claim(claim_id=f"X{i}", text=c.text, source_url=None,
                      must_contain=c.must_contain) for i, c in enumerate(out, 1)]

    def _extract_one(self, script: str) -> list[Claim]:
        payload, answered = call(self.model, _INSTRUCTION,
                                 f"SCRIPT:\n{script[:MAX_DOC]}", self.timeout)
        self.name = answered

        try:
            raw = json.loads(payload["candidates"][0]["content"]["parts"][0]["text"])
        except (KeyError, IndexError, ValueError, TypeError):
            return []
        out = []
        for i, c in enumerate(raw.get("claims", []), 1):
            text, must = (c.get("text") or "").strip(), (c.get("must_contain") or "").strip()
            if not text or not must:
                continue          # a claim with no checkable phrase is not extractable
            out.append(Claim(claim_id=f"X{i}", text=text, source_url=None,
                             must_contain=must))
        return out
