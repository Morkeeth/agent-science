"""Gemini as a LOCATOR. It proposes a passage; it never authors a verdict.

This is the seam where a model genuinely earns its place. Locating the passage in a
document that carries a claim is a language problem, and the previous implementation
solved it with `str.find` plus a hand-scraped list of navigation strings from two
websites — which produced a false UNKNOWN and would have failed on the third site.

THE CONTRACT, unchanged since before any model existed here:
    the model may only LOCATE evidence, never ASSERT it.
Its output goes to `clearance.verify`, which refuses anything not verbatim in the
fetched document. A hallucinated passage degrades to `source_does_not_state_it`.
`Verdict.__post_init__` does not move.

The key is read at runtime from a 0600 file outside the tree. Never copied in, never
logged, never included in an error message.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Optional

MODEL = "gemini-3.5-flash"
ENDPOINT = ("https://generativelanguage.googleapis.com/v1beta/models/"
            "{model}:generateContent")
KEY_PATH = Path.home() / ".config" / "keys" / "gemini.key"
MAX_DOC = 120_000   # characters of document sent; flash handles far more


class NoKey(RuntimeError):
    """Raised when the Gemini key is absent. Never stubbed around."""


def load_key() -> str:
    env = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if env:
        return env.strip()
    if KEY_PATH.exists():
        key = KEY_PATH.read_text().strip()
        if key:
            return key
    raise NoKey(
        f"no Gemini API key: set GEMINI_API_KEY or place it at {KEY_PATH}. "
        "Not stubbing — a fabricated passage is fabricated evidence."
    )


_INSTRUCTION = """You locate evidence. You never judge it.

Given a DOCUMENT and a CLAIM, return the single shortest contiguous passage from the
DOCUMENT that states the claim.

Rules, all of them hard:
- The passage must be copied EXACTLY from the DOCUMENT, character for character.
  Do not rephrase, summarise, correct, translate, or join separated fragments.
- If no passage in the DOCUMENT states the claim, return null. Returning null is a
  correct and expected answer. Do not return a passage that is merely related,
  topical, or nearly right.
- Do not return navigation text, menus, language pickers, link labels or headers.
  Return prose that reads as a statement.
- Never use knowledge from outside the DOCUMENT.
- The passage MUST contain the REQUIRED TERMS given below, verbatim. A passage that
  states the claim in other words will be rejected downstream, so it is not useful.
- A title, heading or citation line that states the claim counts as a statement.

Reply with JSON only: {"passage": "<exact text>"} or {"passage": null}"""


class GeminiLocator:
    """Proposes a passage. Untrusted, like every locator."""

    name = "gemini-3.5-flash"

    def __init__(self, model: str = MODEL, timeout: int = 60):
        self.model, self.timeout = model, timeout
        self.name = model

    def propose(self, *, claim: str, must_contain: str,
                document: str) -> Optional[str]:
        body = json.dumps({
            "systemInstruction": {"parts": [{"text": _INSTRUCTION}]},
            # must_contain was NOT sent in the first version. The verifier rejects any
            # passage lacking these terms, so the model was being graded on a criterion
            # it had never been told — and it answered null on documents that plainly
            # stated the claim. The stub knew the constraint; the model did not.
            "contents": [{"role": "user", "parts": [{"text":
                f"CLAIM:\n{claim}\n\nREQUIRED TERMS (must appear in the passage, "
                f"verbatim):\n{must_contain}\n\nDOCUMENT:\n{document[:MAX_DOC]}"}]}],
            "generationConfig": {"temperature": 0, "responseMimeType": "application/json"},
        }).encode()
        req = urllib.request.Request(
            ENDPOINT.format(model=self.model), data=body, method="POST",
            headers={"Content-Type": "application/json",
                     "x-goog-api-key": load_key()})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                payload = json.load(r)
        except urllib.error.HTTPError as e:
            # Status and reason only. A key must never ride out in an exception.
            raise RuntimeError(f"Gemini call failed: HTTP {e.code} {e.reason}") from None

        try:
            text = payload["candidates"][0]["content"]["parts"][0]["text"]
            passage = json.loads(text).get("passage")
        except (KeyError, IndexError, ValueError, TypeError):
            return None
        if not passage or not isinstance(passage, str):
            return None
        return passage.strip()
