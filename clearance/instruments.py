"""Rights instruments — real, dereferenceable, and quoted from the source.

Nothing in this file invents licence text. Terms are fetched from the instrument's
own URL and cached to disk. If an instrument has never been fetched, the engine
cannot emit GREEN or RED for it; it emits UNKNOWN. That is deliberate.
"""
from __future__ import annotations

import html
import json
import re
import hashlib
import os
import tempfile
import threading
import subprocess
import sys
from datetime import datetime, timezone

from clearance.safe_fetch import fetch_public, validate_url
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


def canonical(url: str) -> str:
    """One key per DOCUMENT, not per URL spelling.

    Measured, not assumed: the fact leg fetched `https://rightsstatements.org/vocab/
    InC/1.0/` and the asset leg fetched `http://.../InC/1.0/` — the SAME document,
    fetched twice, cached under two keys, in a system whose entire thesis is that a
    document is the unit of evidence. Two caches disagreeing about what one document is
    called is the wrong-object failure inside the store itself.

    Deliberately conservative on structure: scheme + trailing slash + percent-decoding
    of path/query. Query *values* still select which EUR-Lex act is cited (`32012L0028`
    ≠ `32019L0790`); only encoding variants of the same characters collapse
    (`CELEX%3A…` vs `CELEX:…`). Fragments never identify the body we quote.
    """
    from urllib.parse import unquote, urlsplit, urlunsplit

    u = (url or "").strip()
    if u.startswith("https://"):
        u = "http://" + u[len("https://"):]
    if u.endswith("/") and "?" not in u:
        u = u[:-1]
    parts = urlsplit(u)
    return urlunsplit(
        (parts.scheme, parts.netloc, unquote(parts.path), unquote(parts.query), "")
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
    try:
        raw, final = fetch_public(uri, timeout=timeout, user_agent=UA)
        body = raw.decode("utf-8", errors="replace")
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
    cache[canonical(uri)] = {"fetched_from": final, "terms": clause,
                             "fetched_at": datetime.now(timezone.utc).isoformat(),
                             "sha256": hashlib.sha256(txt.encode("utf-8")).hexdigest()}
    _save(cache)
    return clause


def terms(uri: str) -> Optional[str]:
    """The cached verbatim terms for an instrument, or None if never fetched."""
    cache = _load()
    entry = cache.get(uri) or cache.get(canonical(uri))
    return entry["terms"] if entry else None


def cached() -> dict:
    return _load()


# ---------------------------------------------------------------------------
# The FACT leg reads documents through the SAME cache and the SAME fetch path.
# A rights instrument and a documentary source are both "a document you either
# opened or did not", which is the entire point of the shared verdict object.
# ---------------------------------------------------------------------------

DOCS = Path(__file__).resolve().parent.parent / "cache" / "documents.json"


def _load_docs() -> dict:
    """Load document cache, collapsing encoding-variant keys onto canonical().

    Legacy rows may sit under CELEX%3A… while routing asks for CELEX:… — same document.
    """
    if not DOCS.exists():
        return {}
    raw = json.loads(DOCS.read_text())
    out: dict = {}
    for key, entry in raw.items():
        want = canonical(key)
        prior = out.get(want)
        if prior is None:
            out[want] = entry
            continue
        # Prefer the entry that still has text; keep richer fetched_at when tied.
        if not prior.get("text") and entry.get("text"):
            out[want] = entry
        elif prior.get("text") and entry.get("text"):
            if (entry.get("fetched_at") or "") > (prior.get("fetched_at") or ""):
                out[want] = entry
    return out


def _doc_hit(docs: dict, url: str) -> Optional[dict]:
    return docs.get(url) or docs.get(canonical(url))


_DOC_LOCK = threading.RLock()


def _write_docs(docs: dict) -> None:
    """Atomic replacement prevents readers from seeing a partial cache file."""
    DOCS.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=".documents-", dir=DOCS.parent)
    try:
        with os.fdopen(fd, "w") as stream:
            json.dump(docs, stream)
        os.replace(name, DOCS)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def document_snapshot(url: str, refresh: bool = False, *, timeout: int = 30,
                      fetch: bool = True):
    """A versioned visible-text snapshot, or None on a fetch failure.

    Cached snapshots are historical evidence, not a freshness claim. Legacy entries
    retain fetched_at=None. refresh=True must fetch successfully; it never falls
    back to the prior snapshot. sha256 hashes the returned UTF-8 visible text.
    """
    try:
        validate_url(url)
    except ValueError:
        return None
    with _DOC_LOCK:
        docs = _load_docs()
        hit = _doc_hit(docs, url)
    # Legacy caches may contain PDF bytes decoded as UTF-8. They are not text evidence.
    if hit and hit.get("text", "").lstrip().startswith("%PDF-"):
        hit = None
    if hit and not refresh:
        text = hit["text"]
        return {"url": url, "text": text,
                "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                "fetched_at": hit.get("fetched_at"),
                "final_url": hit.get("final_url") or hit.get("fetched_from") or url,
                "cache_hit": True}
    if not fetch and not refresh:
        return None
    try:
        body, final = fetch_public(url, timeout=timeout, user_agent=UA)
        if body.lstrip().startswith(b'%PDF-'):
            result=subprocess.run([sys.executable,str(Path(__file__).with_name('pdf_source.py'))],
                input=body,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,timeout=30,check=True)
            text=result.stdout.decode('utf-8')
        else:
            text = _visible_text(body.decode("utf-8", errors="replace"))
    except Exception:
        return None
    snapshot = {"url": url, "text": text,
                "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "final_url": final, "cache_hit": False}
    with _DOC_LOCK:
        docs = _load_docs()
        # Keep versions addressable by content hash for later evidence comparisons.
        previous = _doc_hit(docs, url) or {}
        versions = dict(previous.get("versions", {}))
        if previous.get("text") is not None:
            old_hash = hashlib.sha256(previous["text"].encode("utf-8")).hexdigest()
            versions[old_hash] = {k: v for k, v in previous.items() if k != "versions"}
        entry = {k: v for k, v in snapshot.items() if k != "cache_hit"}
        versions[snapshot["sha256"]] = dict(entry)
        entry["versions"] = versions
        docs.pop(url, None)
        docs.pop(canonical(url), None)
        docs[canonical(url)] = entry
        _write_docs(docs)
    return snapshot


def document(url: str, *, fetch: bool = False, timeout: int = 30,
             refresh: bool = False):
    """Backward-compatible text API. Explicit refresh bypasses the cache."""
    snapshot = document_snapshot(url, refresh=refresh, timeout=timeout, fetch=fetch)
    return snapshot["text"] if snapshot else None
