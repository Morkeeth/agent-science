"""Ingest fleet research into the registry — markdown or single claim+url."""
from __future__ import annotations

import os
import re
from datetime import datetime, timezone
from pathlib import Path

from clearance import refusal_log

_ROOT = Path(__file__).resolve().parent.parent
_CORPUS = _ROOT / "research-corpus"
_URL = re.compile(r"https?://[^\s)\]]+")


def append_markdown(body: str, *, slug: str | None = None) -> Path:
    """Write [CLAIM]/[URL] markdown to research-corpus/ for audit trail."""
    _CORPUS.mkdir(parents=True, exist_ok=True)
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    name = slug or f"ingest-{datetime.now(timezone.utc).strftime('%H%M%S')}"
    safe = re.sub(r"[^a-zA-Z0-9_-]+", "-", name).strip("-")[:48]
    path = _CORPUS / f"{day}-{safe}.md"
    path.write_text(body.rstrip() + "\n", encoding="utf-8")
    return path


def ingest_markdown(body: str, *, slug: str | None = None,
                    production: str = "ingest", fetch: bool = True) -> dict:
    """Save markdown + backfill registry from parsed claims."""
    import clear_corpus
    path = append_markdown(body, slug=slug)
    res = clear_corpus.backfill_log(str(path.parent), fetch=fetch,
                                    production=production)
    # Re-read only claims from this file — approximate via log delta
    return {"file": str(path), **res}


def ingest_claim(claim: str, url: str, *, production: str = "ingest",
                 fetch: bool = True) -> dict:
    """Single claim+URL — verify against named source, seed registry."""
    from clearance.facts import Claim, judge_claim
    from clearance.locate import DEFAULT
    import clear_corpus

    mc = clear_corpus._must_contain(claim)
    c = Claim("I1", claim.strip(), url.strip(), mc)
    v = judge_claim(c, locator=DEFAULT, live_search=False, fetch=fetch)
    con = refusal_log.connect()
    term = mc if len(mc) >= 6 else claim.strip()
    refusal_log.record(
        con,
        term=term,
        assertion=claim.strip(),
        verdict=v.verdict,
        production=production,
        basis="primary" if v.verdict == "GREEN" else None,
        cause=v.cause,
        citation_url=v.citation_url,
        quoted_terms=v.quoted_terms,
    )
    path = append_markdown(f"[CLAIM] {claim.strip()}\n[URL] {url.strip()}\n",
                           slug="claim")
    label = refusal_log.surface_label(verdict=v.verdict, cause=v.cause)
    return {
        "file": str(path),
        "label": label,
        "verdict": v.verdict,
        "cause": v.cause,
        "citation_url": v.citation_url,
        "quoted_terms": v.quoted_terms,
        "log_size": refusal_log.stats(con)["n"],
    }


def ingest_text(text: str, *, production: str = "ingest") -> dict:
    """Auto-detect: full markdown with [CLAIM] tags, or 'claim\\nurl' pair."""
    text = text.strip()
    if "[CLAIM]" in text.upper():
        return ingest_markdown(text, production=production)
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    url_line = next((ln for ln in lines if _URL.search(ln)), None)
    if url_line and len(lines) >= 2:
        claim = lines[0] if lines[0] != url_line else lines[1]
        url = _URL.search(url_line).group(0)
        return ingest_claim(claim, url, production=production)
    raise ValueError("need [CLAIM] markdown or two lines (claim + http url)")
