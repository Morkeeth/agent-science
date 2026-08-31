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
RECEIPTS = Path(__file__).resolve().parent.parent / "cache" / "search_receipts.jsonl"


# Every live call to Parallel is counted HERE, at the only place one is made. The
# per-claim counter in agent_science.py missed escalation searches entirely, because
# those happen inside the engine below it - so the reported cost undercounted the real
# spend. A meter that only sees one of two call sites is not a meter.
LIVE_CALLS = 0


def calls() -> int:
    return LIVE_CALLS


def reset_calls() -> None:
    global LIVE_CALLS
    LIVE_CALLS = 0


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


def log_receipt(*, source: str, objective: str, queries: list[str],
                candidates: list[Candidate], cache_hit: bool = False) -> None:
    """Append query → result for optimization analytics. No API keys."""
    from datetime import datetime, timezone
    RECEIPTS.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "at": datetime.now(timezone.utc).isoformat(),
        "source": source,
        "objective": objective[:240],
        "queries": queries,
        "cache_hit": cache_hit,
        "n_candidates": len(candidates),
        "urls": [c.url for c in candidates[:8]],
    }
    with RECEIPTS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def find_sources(objective: str, queries: list[str], *, mode: str = "advanced",
                 live: bool = False, max_results: int = 6,
                 term: str = "") -> Optional[list[Candidate]]:
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
        out = [Candidate(**c) for c in cache[ck][:max_results]]
        log_receipt(source="parallel", objective=objective, queries=queries,
                    candidates=out, cache_hit=True)
        return out
    term_key = (term or "").strip().lower()
    if term_key and term_key in cache:
        out = [Candidate(**c) for c in cache[term_key][:max_results]]
        log_receipt(source="parallel", objective=objective, queries=queries,
                    candidates=out, cache_hit=True)
        return out[:max_results]
    if not live:
        return None

    body = json.dumps({"objective": objective, "search_queries": queries,
                       "mode": mode}).encode()
    req = urllib.request.Request(
        ENDPOINT, data=body, method="POST",
        headers={"Content-Type": "application/json", "x-api-key": load_key()})
    global LIVE_CALLS
    LIVE_CALLS += 1
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
    if term_key:
        cache[term_key] = cache[ck]
    _cache_save(cache)
    log_receipt(source="parallel", objective=objective, queries=queries,
                candidates=out[:max_results], cache_hit=False)
    return out[:max_results]
