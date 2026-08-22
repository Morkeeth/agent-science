"""Source independence — the question printed, not answered.

A source that is the claim's own origin is not evidence, and nothing at the passage
level can tell the two apart: self-citation and corroboration produce an identical
verbatim match. Independence is a property of the SOURCE SET, not of a verdict.

**This module does not solve that.** It flags candidates whose URL suggests they may be
derived — an encyclopaedia, a mirror, an aggregator — so the report can say so beside
the verdict instead of silently treating them as primary. That is the same move as
separating UNKNOWN-ours from UNKNOWN-theirs: we cannot answer it today, and we refuse to
hide that we have not.

A flag here is NOT a refusal. A Wikipedia page can be a perfectly good source for a
claim that did not come from Wikipedia. The point is that the reader gets told.
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

# Hosts that are tertiary by construction, or copies of something else.
_DERIVED = (
    ("wikipedia.org", "encyclopaedia — tertiary, and the likely origin of a "
                      "script researched online"),
    ("wikiwand.com", "Wikipedia mirror"),
    ("dbpedia.org", "derived from Wikipedia"),
    ("ipfs.dweb.link", "IPFS mirror — an accurate copy of some past state of "
                       "another document, which is not the document"),
    ("ipfs.io", "IPFS mirror"),
    ("webcache.googleusercontent.com", "cache of another page"),
    ("web.archive.org", "archived copy — the snapshot, not the live object"),
    ("britannica.com", "encyclopaedia — tertiary"),
    ("everipedia", "Wikipedia fork"),
)

# Hosts that are the thing itself.
_PRIMARY = (
    ("eur-lex.europa.eu", "EU primary law"),
    ("legislation.gov.uk", "UK primary legislation"),
    ("gov.uk", "UK government"),
    (".gov", "government publisher"),
    ("copyright.gov", "US Copyright Office"),
    ("wipo.int", "WIPO"),
    ("europa.eu", "EU institution"),
    ("courtlistener.com", "court records"),
    ("rightsstatements.org", "the rights vocabulary itself"),
    ("creativecommons.org", "the licence text itself"),
)


def classify(url: str) -> tuple[str, str]:
    """(class, why). class is 'primary', 'derived' or 'unclassified'."""
    host = (urlparse(url).netloc or "").lower()
    path = (urlparse(url).path or "").lower()
    for frag, why in _DERIVED:
        if frag in host or frag in path:
            return "derived", why
    for frag, why in _PRIMARY:
        if host.endswith(frag) or frag in host:
            return "primary", why
    return "unclassified", "not on either list — a human should look"


def note(url: str) -> str:
    """One line to print beside a verdict. Never a refusal."""
    cls, why = classify(url)
    if cls == "primary":
        return f"source class: PRIMARY ({why})"
    if cls == "derived":
        return (f"source class: DERIVED ({why}). "
                "If the script was researched from this, the check is a round trip. "
                "The engine cannot tell; a human must.")
    return f"source class: UNCLASSIFIED ({why})"
