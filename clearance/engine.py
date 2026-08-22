"""The clearance engine.

Input : a subject (an asset, later a fact) + the use being asked about.
Output: a Verdict that either cites an instrument verbatim, or says UNKNOWN.

There is no third path. The engine cannot guess.
"""
from __future__ import annotations

import re
from typing import Optional

from . import instruments
from .verdict import (Verdict, GREEN, RED, UNKNOWN, ASSET,
                      NO_INSTRUMENT, UNRULED, UNREAD_TERMS, NOT_EVALUATED)

# The uses a production actually needs cleared.
AI_TRAINING = "ai_training"
COMMERCIAL = "commercial_license"
BROADCAST = "broadcast"
USES = (AI_TRAINING, COMMERCIAL, BROADCAST)

# Instrument URI -> per-use ruling.
#   value = (verdict, reason, interpretive?)
# `interpretive=True` marks a reading that is OURS, not the instrument's plain words.
# Printing that distinction is the difference between evidence and an opinion.
_FREE = (GREEN, "no rights reserved that block this use", False)

_RULES: dict[str, dict[str, tuple]] = {
    "http://rightsstatements.org/vocab/InC/1.0/": {
        AI_TRAINING: (RED, "in copyright — permission required from the rights-holder", False),
        COMMERCIAL: (RED, "in copyright — permission required from the rights-holder", False),
        BROADCAST: (RED, "in copyright — permission required from the rights-holder", False),
    },
    "http://rightsstatements.org/vocab/InC-EDU/1.0/": {
        AI_TRAINING: (RED, "educational use only — commercial AI training not covered", False),
        COMMERCIAL: (RED, "educational use only", False),
        BROADCAST: (RED, "educational use only", False),
    },
    "http://creativecommons.org/publicdomain/mark/1.0/": {
        AI_TRAINING: _FREE, COMMERCIAL: _FREE, BROADCAST: _FREE,
    },
    "http://creativecommons.org/publicdomain/zero/1.0/": {
        AI_TRAINING: _FREE, COMMERCIAL: _FREE, BROADCAST: _FREE,
    },
    "http://creativecommons.org/licenses/by/4.0/": {
        AI_TRAINING: (GREEN, "permitted with attribution", False),
        COMMERCIAL: (GREEN, "permitted with attribution", False),
        BROADCAST: (GREEN, "permitted with attribution", False),
    },
    "http://creativecommons.org/licenses/by-nd/4.0/": {
        AI_TRAINING: (RED, "NoDerivatives — training produces a derivative", True),
        COMMERCIAL: (GREEN, "commercial use permitted if distributed unmodified", False),
        BROADCAST: (GREEN, "permitted if distributed unmodified, with attribution", False),
    },
    "http://creativecommons.org/licenses/by-nc/4.0/": {
        AI_TRAINING: (RED, "NonCommercial — commercial training not permitted", False),
        COMMERCIAL: (RED, "NonCommercial", False),
        BROADCAST: (RED, "NonCommercial", False),
    },
    "http://creativecommons.org/licenses/by-nc-sa/4.0/": {
        AI_TRAINING: (RED, "NonCommercial + ShareAlike", False),
        COMMERCIAL: (RED, "NonCommercial", False),
        BROADCAST: (RED, "NonCommercial", False),
    },
}

# Versioned / jurisdictional CC URLs (…/by-nc-nd/3.0/es/) carry the same operative
# terms as their 4.0 sibling. We resolve by licence CODE and still cite the exact
# URL the archive published. Normalising was not cosmetic: 3.0/es alone was 35 real
# items being reported as "we cannot read this", which was false.
_CC_ALIAS = {
    "by": "http://creativecommons.org/licenses/by/4.0/",
    "by-sa": "http://creativecommons.org/licenses/by/4.0/",
    "by-nd": "http://creativecommons.org/licenses/by-nd/4.0/",
    "by-nc": "http://creativecommons.org/licenses/by-nc/4.0/",
    "by-nc-sa": "http://creativecommons.org/licenses/by-nc-sa/4.0/",
    "by-nc-nd": "http://creativecommons.org/licenses/by-nc-nd/4.0/",
}

# In copyright, EU orphan work: the rights-holder cannot be located. Legally RED and
# commercially the single most interesting row in an archive — it is the one a
# clearance desk cannot resolve at any price without a diligent-search record.
_RULES["http://creativecommons.org/licenses/by-nc-nd/4.0/"] = {
    AI_TRAINING: (RED, "NonCommercial + NoDerivatives", False),
    COMMERCIAL: (RED, "NonCommercial", False),
    BROADCAST: (RED, "NonCommercial", False),
}

_RULES["http://rightsstatements.org/vocab/InC-OW-EU/1.0/"] = {
    AI_TRAINING: (RED, "EU orphan work — in copyright, rights-holder not locatable", False),
    COMMERCIAL: (RED, "EU orphan work — in copyright, rights-holder not locatable", False),
    BROADCAST: (RED, "EU orphan work — in copyright, rights-holder not locatable", False),
}

# "Copyright Not Evaluated": the holder is telling us they never assessed it.
# That is evidence of an absence, not an absence of evidence — so it is UNKNOWN
# WITH a citation, and it belongs to the archive's backlog, not ours.
CNE = "http://rightsstatements.org/vocab/CNE/1.0/"


def _resolve(uri: str) -> str | None:
    """Map a published instrument URI onto the rule set. None = genuinely unruled."""
    if uri in _RULES:
        return uri
    m = re.match(r"https?://creativecommons\.org/licenses/([a-z-]+)/", uri or "")
    if m:
        return _CC_ALIAS.get(m.group(1))
    return None


def known_instruments() -> tuple[str, ...]:
    return tuple(_RULES)


def judge(
    *,
    subject_id: str,
    subject_title: str,
    instrument_uri: Optional[str],
    use: str,
    holder: Optional[str] = None,
    noun: str = ASSET,
) -> Verdict:
    if use not in USES:
        raise ValueError(f"unknown use {use!r}; expected one of {USES}")

    def unknown(reason: str, cause: str, **kw) -> Verdict:
        return Verdict(
            subject_id=subject_id, subject_title=subject_title, noun=noun, use=use,
            verdict=UNKNOWN, reason=reason, holder=holder, cause=cause, **kw,
        )

    if not instrument_uri:
        return unknown("the holder published no rights instrument", NO_INSTRUMENT)

    if instrument_uri == CNE:
        quoted = instruments.terms(CNE)
        return unknown(
            "the holder states copyright was never evaluated for this item",
            NOT_EVALUATED,
            **({"citation_url": CNE, "quoted_terms": quoted} if quoted else {}),
        )

    resolved = _resolve(instrument_uri)
    if resolved is None:
        return unknown(
            f"we have not ruled this instrument yet: {instrument_uri}", UNRULED)

    ruling = _RULES[resolved]
    # Prefer the terms of the exact URL the archive published; fall back to the
    # resolved sibling and SAY SO rather than passing it off as the same document.
    quoted = instruments.terms(instrument_uri)
    read_from = instrument_uri
    if not quoted:
        quoted = instruments.terms(resolved)
        read_from = resolved
    if not quoted:
        # We have a rule but have never read the instrument. Refuse to assert.
        return unknown(
            f"instrument {instrument_uri} has never been fetched — "
            "no verbatim terms on file to cite", UNREAD_TERMS)

    verdict, reason, interpretive = ruling[use]
    return Verdict(
        subject_id=subject_id, subject_title=subject_title, noun=noun, use=use,
        verdict=verdict, reason=reason, citation_url=read_from,
        quoted_terms=quoted, holder=holder, interpretive=interpretive,
        published_instrument=instrument_uri,
    )
