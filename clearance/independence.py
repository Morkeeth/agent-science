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


# ---------------------------------------------------------------------------
# INDEPENDENCE IS A PROPERTY OF THE SOURCE SET, NOT OF A VERDICT.
#
# A claim with three sources that all trace to one origin is LESS independent than a
# claim with one primary source, even though it has more citations. "More sources =
# more confidence" is the trap this section exists to refuse.
# ---------------------------------------------------------------------------

_ORIGIN_FAMILIES = (
    (("wikipedia.org", "wikiwand.com", "dbpedia.org", "everipedia",
      "ipfs.dweb.link", "ipfs.io", "/wiki/"), "wikipedia"),
    (("web.archive.org", "webcache.googleusercontent.com"), "cache"),
)


def origin_key(url: str) -> str:
    """A stable id for where a document ultimately comes FROM.

    Two URLs sharing an origin_key are ONE source, not two. Every Wikipedia mirror is
    Wikipedia; every cache is the page it cached.
    """
    u = (url or "").lower()
    for frags, family in _ORIGIN_FAMILIES:
        if any(f in u for f in frags):
            return family
    host = (urlparse(url).netloc or "").lower().split(":")[0]
    parts = [p for p in host.split(".") if p]
    if len(parts) >= 3 and parts[-2] in ("co", "gov", "ac", "org", "com", "net"):
        return ".".join(parts[-3:])
    return ".".join(parts[-2:]) if len(parts) >= 2 else host


# Two independent origins is the newsroom standard, and it is the standard here.
CORROBORATION = 2


def assess(urls) -> dict:
    """Independence of a SET of candidate sources for one claim.

    THE MODELLING ERROR THIS FIXES. The first version counted only PRIMARY origins as
    independent support, which conflated two different properties:

        PRIMARY     the document IS the thing - the statute, the register, the ruling
        INDEPENDENT several origins that do not derive from one another

    Four unrelated outlets reporting a court ruling are INDEPENDENT without any of them
    being PRIMARY. Conflating the two demoted a claim carried by the LA Times, Columbia
    University and two other separate origins as "no independent source", and it is why
    a real script cleared 0 of 10. That is not strictness, it is a category error.

    So: one primary origin clears on best evidence. Two or more distinct non-derived
    origins clear on corroboration. A single unclassified origin still does not clear -
    the asymmetry that made strictness right is untouched, because one blog is still one
    blog.
    """
    groups = {}
    for u in urls:
        groups.setdefault(origin_key(u), []).append(u)

    independent, derived, unclassified = [], [], []
    for key, members in groups.items():
        cls = classify(members[0])[0]
        (independent if cls == "primary"
         else derived if cls == "derived"
         else unclassified).append(key)

    corroborating = independent + unclassified   # everything that is not a copy
    return {
        "groups": groups,
        "origins": len(groups),
        "independent": independent,
        "derived": derived,
        "unclassified": unclassified,
        "corroborating": corroborating,
        # best evidence, or corroboration by genuinely separate origins
        "has_independent_support": bool(independent) or len(corroborating) >= CORROBORATION,
        "basis": ("primary" if independent
                  else "corroborated" if len(corroborating) >= CORROBORATION
                  else "insufficient"),
    }
