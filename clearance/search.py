"""Parallel Search — the missing first step of the pipeline.

Uses the official `parallel-web` SDK when installed (Parallel track requirement);
falls back to the same REST endpoint via urllib. Every live call records a
`search_id` when the API returns one — PeriodCheck-style evidence lineage.

THE KEY IS NEVER IN THIS REPO. It is read at runtime from env or a 0600 file
outside the tree. It is not logged, not echoed, and not included in error messages.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

ENDPOINT = "https://api.parallel.ai/v1/search"
KEY_PATH = Path.home() / ".config" / "keys" / "parallel.key"
CACHE = Path(__file__).resolve().parent.parent / "cache" / "searches.json"
RECEIPTS = Path(__file__).resolve().parent.parent / "cache" / "search_receipts.jsonl"

LIVE_CALLS = 0
LAST_SEARCH_ID: Optional[str] = None


def calls() -> int:
    return LIVE_CALLS


def last_search_id() -> Optional[str]:
    return LAST_SEARCH_ID


def reset_calls() -> None:
    global LIVE_CALLS, LAST_SEARCH_ID
    LIVE_CALLS = 0
    LAST_SEARCH_ID = None


class NoKey(RuntimeError):
    """Raised when the Parallel key is absent. Never stubbed around."""


@dataclass(frozen=True)
class Candidate:
    url: str
    title: str
    excerpt: str


def sdk_available() -> bool:
    try:
        import parallel  # noqa: F401
        return True
    except ImportError:
        return False


def sdk_version() -> Optional[str]:
    if not sdk_available():
        return None
    try:
        from importlib.metadata import version
        return version("parallel-web")
    except Exception:
        return None


def integration_info() -> dict:
    """Runtime shape for /health and /partners — how Parallel is wired."""
    return {
        "partner": "parallel",
        "track_requirement": "Search API at runtime via parallel-web SDK or REST",
        "sdk_package": "parallel-web",
        "sdk_installed": sdk_available(),
        "sdk_version": sdk_version(),
        "transport": "parallel-web" if sdk_available() else "urllib-rest",
        "endpoint": ENDPOINT,
        "live_calls": LIVE_CALLS,
        "last_search_id": LAST_SEARCH_ID,
        "receipts_log": str(RECEIPTS),
    }


def load_key() -> str:
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


def _candidates_from_payload(payload: dict) -> list[Candidate]:
    out: list[Candidate] = []
    for x in payload.get("results") or []:
        url = x.get("url") if isinstance(x, dict) else getattr(x, "url", None)
        if not url:
            continue
        title = (x.get("title") if isinstance(x, dict) else getattr(x, "title", None)) or "(untitled)"
        excerpts = x.get("excerpts") if isinstance(x, dict) else getattr(x, "excerpts", None)
        excerpt = ""
        if excerpts:
            excerpt = (excerpts[0] if isinstance(excerpts, list) else str(excerpts))[:400]
        out.append(Candidate(url=url, title=title, excerpt=excerpt))
    return out


def log_receipt(*, source: str, objective: str, queries: list[str],
                candidates: list[Candidate], cache_hit: bool = False,
                search_id: Optional[str] = None) -> None:
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
        "search_id": search_id,
    }
    with RECEIPTS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def _live_search_urllib(objective: str, queries: list[str], *, mode: str) -> tuple[dict, str | None]:
    body = json.dumps({"objective": objective, "search_queries": queries,
                       "mode": mode}).encode()
    req = urllib.request.Request(
        ENDPOINT, data=body, method="POST",
        headers={"Content-Type": "application/json", "x-api-key": load_key()})
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            payload = json.load(r)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Parallel search failed: HTTP {e.code} {e.reason}") from None
    return payload, payload.get("search_id")


def _live_search_sdk(objective: str, queries: list[str], *, mode: str) -> tuple[dict, str | None]:
    from parallel import Parallel

    client = Parallel(api_key=load_key())
    search = client.search(objective=objective, search_queries=queries, mode=mode)
    sid = getattr(search, "search_id", None)
    results = []
    for r in search.results or []:
        results.append({
            "url": getattr(r, "url", None),
            "title": getattr(r, "title", None),
            "excerpts": list(getattr(r, "excerpts", None) or []),
        })
    return {"search_id": sid, "results": results}, sid


def _live_search(objective: str, queries: list[str], *, mode: str) -> tuple[dict, str | None]:
    global LIVE_CALLS, LAST_SEARCH_ID
    LIVE_CALLS += 1
    if sdk_available():
        payload, sid = _live_search_sdk(objective, queries, mode=mode)
    else:
        payload, sid = _live_search_urllib(objective, queries, mode=mode)
    LAST_SEARCH_ID = sid
    return payload, sid


def find_sources(objective: str, queries: list[str], *, mode: str = "advanced",
                 live: bool = False, max_results: int = 6,
                 term: str = "") -> Optional[list[Candidate]]:
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

    payload, sid = _live_search(objective, queries, mode=mode)
    out = _candidates_from_payload(payload)
    cache[ck] = [c.__dict__ for c in out]
    if term_key:
        cache[term_key] = cache[ck]
    _cache_save(cache)
    log_receipt(source="parallel", objective=objective, queries=queries,
                candidates=out[:max_results], cache_hit=False, search_id=sid)
    return out[:max_results]
