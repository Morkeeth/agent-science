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

import hashlib
import json
import re
import os
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Optional

MODEL = "gemini-3.5-flash"
# The free tier caps GenerateRequestsPerDayPerProjectPerModel at TWENTY PER DAY, PER
# MODEL. Measured, not guessed: the 429 body names quotaId
# GenerateRequestsPerDayPerProjectPerModel-FreeTier, quotaValue 20.
#
# Because the cap is per MODEL, a ladder of sibling models multiplies the daily budget.
# Every model here is Gemini 3.5 or later, so the submission requirement is satisfied
# whichever one answers.
LADDER = ("gemini-3.5-flash", "gemini-3.5-flash-lite", "gemini-3.6-flash",
          "gemini-3.7-flash")
ENDPOINT = ("https://generativelanguage.googleapis.com/v1beta/models/"
            "{model}:generateContent")
KEY_PATH = Path.home() / ".config" / "keys" / "gemini.key"
MAX_DOC = 120_000   # characters of document sent; flash handles far more
CACHE = Path(__file__).resolve().parent.parent / "cache" / "gemini.json"

# The free tier returns HTTP 429 after roughly two to four consecutive calls. That is an
# operational fact about the demo, not a code problem: a script with N claims WILL
# rate-limit on camera. Backoff makes a batch finish; it does not make it fast.
RETRIES = 5
BACKOFF = (5, 15, 30, 45, 60)


def _cache_key(model: str, claim: str, must: str, document: str) -> str:
    h = hashlib.sha256()
    for part in (model, claim, must, document[:MAX_DOC]):
        h.update(part.encode()); h.update(b"\x00")
    return h.hexdigest()


def _cache_load() -> dict:
    return json.loads(CACHE.read_text()) if CACHE.exists() else {}


def _cache_put(k: str, v) -> None:
    d = _cache_load(); d[k] = v
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(d))


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


def call(model: str, system: str, user: str, timeout: int = 90) -> tuple[dict, str]:
    """THE single place this codebase talks to Gemini.

    Both callers - the locator and the claim extractor - go through here. The first
    version of the backoff lived inside GeminiLocator.propose() and the extractor,
    in another module, had none: it died on the first 429. A retry policy that
    protects one of two call sites is not a retry policy.

    Returns (payload, model_that_answered). The second element is NOT bookkeeping: on
    a per-day quota exhaustion this advances down LADDER to a sibling model, and the
    verdict's reason records the locator that actually answered. A record naming the
    model we ASKED for rather than the one that ANSWERED would be a citation lying
    about its own provenance - the same class as quoting one document while citing
    another.
    """
    body = json.dumps({
        "systemInstruction": {"parts": [{"text": system}]},
        "contents": [{"role": "user", "parts": [{"text": user}]}],
        "generationConfig": {"temperature": 0, "responseMimeType": "application/json"},
    }).encode()
    tried, chain = [], [model] + [m for m in LADDER if m != model]
    for candidate in chain:
        req = urllib.request.Request(
            ENDPOINT.format(model=candidate), data=body, method="POST",
            headers={"Content-Type": "application/json", "x-goog-api-key": load_key()})
        for attempt in range(RETRIES):
            try:
                with urllib.request.urlopen(req, timeout=timeout) as r:
                    return json.load(r), candidate
            except urllib.error.HTTPError as e:
                raw = e.read().decode("utf-8", "ignore") if e.code == 429 else ""
                daily = "PerDay" in (re.search(r'"quotaId"\s*:\s*"([^"]+)', raw) or
                                     type("", (), {"group": lambda *_: ""})).group(1)
                if e.code == 429 and daily:
                    tried.append(candidate)
                    break            # today's budget for THIS model is gone; next model
                if e.code == 429 and attempt < RETRIES - 1:
                    wait = e.headers.get("Retry-After")
                    time.sleep(int(wait) if (wait or "").isdigit() else BACKOFF[attempt])
                    continue
                # Status and reason only. A key must never ride out in an exception.
                raise RuntimeError(
                    f"Gemini call failed: HTTP {e.code} {e.reason}") from None
    raise RuntimeError(
        "Gemini daily free-tier quota (20/model) exhausted on every model in the "
        f"ladder: {tried}. This is a quota wall, not a code failure - it needs "
        "billing enabled or a new day.")


class GeminiLocator:
    """Proposes a passage. Untrusted, like every locator."""

    name = "gemini-3.5-flash"

    def __init__(self, model: str = MODEL, timeout: int = 60, cache: bool = False):
        """cache=True replays a previous identical call instead of making a new one.

        OFF by default. A cached run is not a live call, and this product's whole
        argument is that the model is actually called — so the cache is for repeated
        test runs and for pacing around the free tier, never the default path.
        """
        self.model, self.timeout, self.cache = model, timeout, cache
        self.name = model

    def propose(self, *, claim: str, must_contain: str,
                document: str) -> Optional[str]:
        # must_contain was NOT sent in the first version. The verifier rejects any
        # passage lacking these terms, so the model was being graded on a criterion it
        # had never been told, and answered null on documents that plainly stated the
        # claim. The stub knew the constraint; the model did not.
        user = (f"CLAIM:\n{claim}\n\nREQUIRED TERMS (must appear in the passage, "
                f"verbatim):\n{must_contain}\n\nDOCUMENT:\n{document[:MAX_DOC]}")
        ck = _cache_key(self.model, claim, must_contain, document)
        if self.cache:
            hit = _cache_load().get(ck)
            if hit is not None:
                return hit or None

        payload, answered = call(self.model, _INSTRUCTION, user, self.timeout)
        self.name = answered   # the record names the model that ANSWERED

        try:
            text = payload["candidates"][0]["content"]["parts"][0]["text"]
            passage = json.loads(text).get("passage")
        except (KeyError, IndexError, ValueError, TypeError):
            return None
        result = passage.strip() if (passage and isinstance(passage, str)) else None
        if self.cache:
            _cache_put(ck, result)
        return result
