"""Deterministic source routing — skip discovery when the primary URL is known.

Parallel proposes candidates; routing CONSTRUCTS them from claim shape. A CELEX number,
a rights-statement vocab code, or an arXiv id is enough to fetch the official document
without spending a search API call. Routing never skips fetch → locate → verify.
"""
from __future__ import annotations

import re
from typing import Optional

from . import search as _search

# Ordered: most specific patterns first. Each returns Candidate(url, title, excerpt).
_EU_ACT = re.compile(
    r"\b(?:Directive|Regulation|Decision)?\s*(?:\(?EU\)?\s*)?"
    r"(\d{4})\s*/\s*(\d+)\s*/\s*EU\b",
    re.I,
)
_EU_ACT_BARE = re.compile(r"\b(\d{4})\s*/\s*(\d+)\s*/\s*EU\b", re.I)
_CELEX_IN_TEXT = re.compile(r"CELEX[:\s]*([34]\d{4}[A-Z]\d{4,5})", re.I)
_RIGHTS_VOCAB = re.compile(
    r"rightsstatements\.org/vocab/([A-Za-z0-9-]+)/([\d.]+)", re.I)
_RIGHTS_CODE = re.compile(
    r"\b(InC|NoC(?:-US|-OK)?|CNE|NKC|UND|NoC-NC|NoC-ND|InC-EDU|InC-EU|NoC-CR|other)\b")
_ARXIV = re.compile(
    r"\b(?:arxiv[:\s]*)?(\d{4}\.\d{4,5})(?:v\d+)?\b", re.I)
_ARXIV_URL = re.compile(r"arxiv\.org/(?:abs|pdf)/(\d{4}\.\d{4,5})", re.I)
_UK_ACT = re.compile(
    r"\b(?:UK|U\.K\.)\s+([^,\s]+(?:\s+Act)?\s+\d{4})\b", re.I)
_UKSI = re.compile(r"\bS\.I\.\s*(\d{4})/(\d+)\b", re.I)


def _eur_lex(celex: str) -> str:
    return (f"https://eur-lex.europa.eu/legal-content/EN/TXT/"
            f"?uri=CELEX:{celex}")


def _celex_kind(blob: str) -> str:
    low = blob.lower()
    if "regulation" in low:
        return "R"
    if "decision" in low:
        return "D"
    return "L"


def _eu_urls(blob: str) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for m in _CELEX_IN_TEXT.finditer(blob):
        celex = m.group(1).upper()
        if celex not in seen:
            seen.add(celex)
            out.append(_eur_lex(celex))
    for pat in (_EU_ACT, _EU_ACT_BARE):
        for m in pat.finditer(blob):
            year, num = m.group(1), int(m.group(2))
            kind = _celex_kind(blob[max(0, m.start() - 40): m.end() + 40])
            celex = f"3{year}{kind}{num:04d}"
            if celex not in seen:
                seen.add(celex)
                out.append(_eur_lex(celex))
    return out


def _rights_urls(blob: str) -> list[str]:
    out: list[str] = []
    for m in _RIGHTS_VOCAB.finditer(blob):
        out.append(f"https://rightsstatements.org/vocab/{m.group(1)}/{m.group(2)}/")
    if out:
        return out
    for m in _RIGHTS_CODE.finditer(blob):
        code = m.group(1)
        out.append(f"https://rightsstatements.org/vocab/{code}/1.0/")
    return out


def _arxiv_urls(blob: str) -> list[str]:
    out: list[str] = []
    for m in _ARXIV_URL.finditer(blob):
        out.append(f"https://arxiv.org/abs/{m.group(1)}")
    for m in _ARXIV.finditer(blob):
        aid = m.group(1)
        u = f"https://arxiv.org/abs/{aid}"
        if u not in out:
            out.append(u)
    return out


def _uk_urls(blob: str) -> list[str]:
    out: list[str] = []
    m = _UKSI.search(blob)
    if m:
        out.append(
            f"https://www.legislation.gov.uk/uksi/{m.group(1)}/{m.group(2)}/made")
    return out


def candidates_for(*, text: str, must_contain: str = "") -> list[_search.Candidate]:
    """Primary URLs implied by claim shape. Empty when nothing is constructible."""
    blob = f"{text} {must_contain}".strip()
    if len(blob) < 4:
        return []
    urls: list[str] = []
    for fn in (_eu_urls, _rights_urls, _arxiv_urls, _uk_urls):
        urls.extend(fn(blob))
    # De-dupe preserving order.
    seen: set[str] = set()
    ordered: list[str] = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            ordered.append(u)
    return [_search.Candidate(url=u, title="routed primary", excerpt="")
            for u in ordered]


def routed_probe(text: str, must_contain: str = "") -> Optional[str]:
    """Short label for receipts: what shape triggered routing."""
    cands = candidates_for(text=text, must_contain=must_contain)
    if not cands:
        return None
    u = cands[0].url
    if "eur-lex" in u:
        return "route:celex"
    if "rightsstatements" in u:
        return "route:rights_vocab"
    if "arxiv" in u:
        return "route:arxiv"
    if "legislation.gov.uk" in u:
        return "route:uk_legislation"
    return "route:primary"
