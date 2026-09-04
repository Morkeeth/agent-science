"""Ingest fleet research into the registry — markdown or single claim+url.

WHERE THIS WRITES, AND WHY IT IS NOT research-corpus/. Until 2026-08-31 this module
appended dated claim files into `research-corpus/`, the directory the evals replay as
their measurement population. Every ingest therefore moved the published denominator:
n=313 became n=314 mid-run, and a clean checkout read 312. The sink is now
`research-inbox/` — a live audit trail that no published number is computed over. The
frozen population and the rule are in `clearance/population.py`; the control that fails
if the two are ever the same directory is `tests/test_frozen_population.py`.
"""
from __future__ import annotations

import tempfile
import uuid
import re
from datetime import datetime, timezone
from pathlib import Path

from clearance import refusal_log
from clearance.safe_fetch import validate_url

_ROOT = Path(__file__).resolve().parent.parent
_INBOX = _ROOT / "research-inbox"   # LIVE sink. Never the eval population.
MAX_INPUT_BYTES = 64 * 1024
MAX_CLAIMS = 20
MAX_CLAIM_CHARS = 4000


def _validate_body(body: str) -> None:
    if not isinstance(body, str) or not body.strip():
        raise ValueError("ingestion text is required")
    if len(body.encode("utf-8")) > MAX_INPUT_BYTES:
        raise ValueError("ingestion text exceeds 64 KiB")
    if len(re.findall(r"(?im)^\s*\[CLAIM\]", body)) > MAX_CLAIMS:
        raise ValueError("ingestion exceeds 20 claims")


_URL = re.compile(r"https?://[^\s)\]]+")


def append_markdown(body: str, *, slug: str | None = None) -> Path:
    """Write [CLAIM]/[URL] markdown to research-inbox/ for audit trail.

    NOT research-corpus/: that is the frozen measurement population and writing into it
    would move every number this product publishes. See clearance/population.py.
    """
    _validate_body(body)
    _INBOX.mkdir(parents=True, exist_ok=True)
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    name = slug or f"ingest-{datetime.now(timezone.utc).strftime('%H%M%S')}"
    safe = re.sub(r"[^a-zA-Z0-9_-]+", "-", name).strip("-")[:48]
    path = _INBOX / f"{day}-{safe}-{uuid.uuid4().hex}.md"
    with path.open("x", encoding="utf-8") as stream:
        stream.write(body.rstrip() + "\n")
    return path


def ingest_markdown(body: str, *, slug: str | None = None,
                    production: str = "ingest", fetch: bool = True) -> dict:
    """Save markdown + backfill registry from parsed claims."""
    import clear_corpus
    _validate_body(body)
    # Parse and verify only this request, never replay the entire growing inbox.
    with tempfile.TemporaryDirectory(prefix="science-ingest-") as directory:
        staged = Path(directory) / "request.md"
        staged.write_text(body, encoding="utf-8")
        claims = clear_corpus.parse_corpus(directory)
        if not claims or len(claims) > MAX_CLAIMS:
            raise ValueError("ingestion needs between 1 and 20 claim/source pairs")
        for claim in claims:
            if len(claim.text) > MAX_CLAIM_CHARS:
                raise ValueError("claim exceeds 4000 characters")
            validate_url(claim.url)
        path = append_markdown(body, slug=slug)
        staged.rename(Path(directory) / path.name)
        res = clear_corpus.backfill_log(directory, fetch=fetch, production=production)
    return {"file": str(path), **res}


def ingest_claim(claim: str, url: str, *, production: str = "ingest",
                 fetch: bool = True) -> dict:
    """Single claim+URL — verify against named source, seed registry."""
    _validate_body(claim)
    if len(claim) > MAX_CLAIM_CHARS:
        raise ValueError("claim exceeds 4000 characters")
    validate_url(url)
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
    _validate_body(text)
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
