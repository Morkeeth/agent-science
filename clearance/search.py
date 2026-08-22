"""Parallel Search — the missing first step of the pipeline.

Until now a Claim arrived with `source_url` already filled in BY HAND. That was the
largest piece of hand-waving left in the product: every demo claim had a human-chosen
source, so the hard part — finding the document that might carry an assertion — was
done off-camera by a person.

This module fills that field. It proposes candidate documents and nothing more; every
candidate still goes through fetch -> locate -> verify, so a search result can no more
become a verdict than a model can.

THE KEY IS NEVER IN THIS REPO. It is read at runtime from a 0600 file outside the tree,
captured once and never copied. It is not logged, not echoed, not put in a cache file,
and not included in any error message.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

ENDPOINT = "https://api.parallel.ai/v1/search"
KEY_PATH = Path.home() / ".config" / "keys" / "parallel.key"
CACHE = Path(__file__).resolve().parent.parent / "cache" / "searches.json"


class NoKey(RuntimeError):
    """Raised when the Parallel key is absent. Never stubbed around."""


@dataclass(frozen=True)
class Candidate:
    url: str
    title: str
    excerpt: str


def load_key() -> str:
    """The one place the key is read. Env var wins so CI can inject it."""
    env = os.environ.get("PARALLEL_API_KEY")
    if env:
        return env.strip()
    if KEY_PATH.exists():
        key = KEY_PATH.read_text().strip()
        if key:
            return key
    raise NoKey(
        f"no Parallel API key: set PARALLEL_API_KEY or place it at {KEY_PATH}. "
        "Not stubbing — a fake search result is fabricated evidence."
    )


def _cache_load() -> dict:
    return json.loads(CACHE.read_text()) if CACHE.exists() else {}


def _cache_save(d: dict) -> None:
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(d, indent=2))


def find_sources(objective: str, queries: list[str], *, mode: str = "advanced",
                 live: bool = False, max_results: int = 6) -> Optional[list[Candidate]]:
    """Candidate documents that MIGHT carry the claim. Never evidence by itself.

    Returns [] when a search RAN and came back empty.
    Returns None when NO SEARCH WAS PERFORMED — cache miss with live=False.

    The distinction is not pedantry. Collapsing them let the engine report
    "searched and found nothing" about a search it never ran, which is a false claim
    about a probe: the exact class this product exists to catch, committed by the
    product, one layer up from the string-matching version of it.
    """
    ck = json.dumps({"o": objective, "q": sorted(queries), "m": mode}, sort_keys=True)
    cache = _cache_load()
    if ck in cache:
        return [Candidate(**c) for c in cache[ck][:max_results]]
    if not live:
        return None

    body = json.dumps({"objective": objective, "search_queries": queries,
                       "mode": mode}).encode()
    req = urllib.request.Request(
        ENDPOINT, data=body, method="POST",
        headers={"Content-Type": "application/json", "x-api-key": load_key()})
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            payload = json.load(r)
    except urllib.error.HTTPError as e:
        # Never let a key reach a log line. Status and reason only.
        raise RuntimeError(f"Parallel search failed: HTTP {e.code} {e.reason}") from None

    out = [Candidate(url=x.get("url", ""), title=x.get("title", "") or "(untitled)",
                     excerpt=(x.get("excerpts") or [""])[0][:400])
           for x in payload.get("results", []) if x.get("url")]
    cache[ck] = [c.__dict__ for c in out]
    _cache_save(cache)
    return out[:max_results]
