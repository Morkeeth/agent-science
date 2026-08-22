"""Rights instruments — real, dereferenceable, and quoted from the source.

Nothing in this file invents licence text. Terms are fetched from the instrument's
own URL and cached to disk. If an instrument has never been fetched, the engine
cannot emit GREEN or RED for it; it emits UNKNOWN. That is deliberate.
"""
from __future__ import annotations

import html
import json
import re
import urllib.request
from pathlib import Path
from typing import Optional

CACHE = Path(__file__).resolve().parent.parent / "cache" / "instruments.json"
UA = "CLEARED-probe/0.1 (hackathon; contact omorke@gmail.com)"

# Sentences we look for in each instrument family, to quote the operative clause
# rather than the page furniture. Purely a locator — the text quoted is the page's.
_ANCHORS = (
    # Most specific first. Ordering is load-bearing: "You are free to" appears in the
    # boilerplate of several rightsstatements pages, so a looser anchor placed above a
    # tighter one quotes the wrong clause from the right document — which is worse than
    # no quote, because it looks cited.
    "The copyright and related rights status of this Item has not been evaluated",
    "The organization that has made the Item available believes that the Item is in the Public Domain",
    "has dedicated the work to the public domain",
    "This work has been identified as being free of known restrictions",
    "This Item is protected by copyright",
    "This Item is in copyright",
    "No known copyright",
    "This work has been identified",
    "You are free to",
    "NonCommercial",
    "NoDerivatives",
    "Usted es libre de",      # es
    "Vous êtes autorisé à",   # fr
    "Sie dürfen",             # de
)


def _load() -> dict:
    if CACHE.exists():
        return json.loads(CACHE.read_text())
    return {}


def _save(d: dict) -> None:
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(d, indent=2, sort_keys=True))


def _visible_text(raw: str) -> str:
    raw = re.sub(r"<(script|style).*?</\1>", " ", raw, flags=re.S | re.I)
    txt = html.unescape(re.sub(r"<[^>]+>", " ", raw))
    return re.sub(r"\s+", " ", txt).strip()


def fetch(uri: str, timeout: int = 25) -> Optional[str]:
    """Fetch an instrument and cache the operative clause, VERBATIM. None on failure."""
    req = urllib.request.Request(uri, headers={"User-Agent": UA, "Accept": "text/html"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read().decode("utf-8", errors="ignore")
            final = r.geturl()
    except Exception as exc:  # network, 403, 404 — all mean "not evidenced"
        return None

    txt = _visible_text(body)
    clause = None
    for a in _ANCHORS:
        i = txt.find(a)
        if i >= 0:
            clause = txt[i : i + 320].strip()
            break
    if not clause:
        return None

    cache = _load()
    cache[uri] = {"fetched_from": final, "terms": clause}
    _save(cache)
    return clause


def terms(uri: str) -> Optional[str]:
    """The cached verbatim terms for an instrument, or None if never fetched."""
    entry = _load().get(uri)
    return entry["terms"] if entry else None


def cached() -> dict:
    return _load()
