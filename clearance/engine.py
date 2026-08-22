"""The clearance engine.

Input : a subject (an asset, later a fact) + the use being asked about.
Output: a Verdict that either cites an instrument verbatim, or says UNKNOWN.

There is no third path. The engine cannot guess.
"""
from __future__ import annotations

from typing import Optional

from . import instruments
from .verdict import Verdict, GREEN, RED, UNKNOWN, ASSET

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

    def unknown(reason: str) -> Verdict:
        return Verdict(
            subject_id=subject_id, subject_title=subject_title, noun=noun, use=use,
            verdict=UNKNOWN, reason=reason, holder=holder,
        )

    if not instrument_uri:
        return unknown("no rights instrument published for this item")

    ruling = _RULES.get(instrument_uri)
    if ruling is None:
        return unknown(f"rights instrument not in the ruled set: {instrument_uri}")

    quoted = instruments.terms(instrument_uri)
    if not quoted:
        # We have a rule but have never read the instrument. Refuse to assert.
        return unknown(
            f"instrument {instrument_uri} has never been fetched — "
            "no verbatim terms on file to cite"
        )

    verdict, reason, interpretive = ruling[use]
    return Verdict(
        subject_id=subject_id, subject_title=subject_title, noun=noun, use=use,
        verdict=verdict, reason=reason, citation_url=instrument_uri,
        quoted_terms=quoted, holder=holder, interpretive=interpretive,
    )
