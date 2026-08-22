"""The verdict record — one shape for both legs of the product.

A fact with no source and an asset with no rights instrument are the SAME record
with a different noun. That is the whole reason this module exists.

The law enforced here, structurally rather than by convention:
    it is impossible to construct a GREEN or RED verdict without a citation.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from typing import Optional

GREEN = "GREEN"
RED = "RED"
UNKNOWN = "UNKNOWN"
VERDICTS = (GREEN, RED, UNKNOWN)

ASSET = "asset"
FACT = "fact"

# Why an UNKNOWN is unknown. Rendering these as one undifferentiated blob was a
# real defect: it billed OUR incompleteness to the archive. Kept as a closed set
# so the gap report can separate "their gap" from "our backlog".
NO_INSTRUMENT = "no_instrument"        # the holder published nothing
UNRULED = "unruled_instrument"         # they published; WE have not ruled it yet
UNREAD_TERMS = "terms_never_fetched"   # we have a rule but never read the instrument
NOT_EVALUATED = "holder_states_not_evaluated"
# ^ the instrument's OWN text states copyright was never assessed. This is the single
# UNKNOWN cause where a citation is REQUIRED, not merely allowed. A required citation
# on one narrow cause is a stronger rule than an optional citation on all of them:
# there is no discretionary path a later commit can widen "just for the demo".
# The FACT noun's causes. Deliberately NOT a parallel taxonomy: a fact with no source
# and an asset with no instrument are the same record, so they share this closed set
# and the same constructor.
NO_SOURCE = "no_source_offered"       # nothing was proposed to support the claim
SOURCE_UNREAD = "source_never_fetched"  # a source was named but never opened
SOURCE_SILENT = "source_does_not_state_it"  # we read it; it does not say this
CAUSES = (NO_INSTRUMENT, UNRULED, UNREAD_TERMS, NOT_EVALUATED,
          NO_SOURCE, SOURCE_UNREAD, SOURCE_SILENT)

# The causes where a citation is REQUIRED rather than forbidden. Both are the same
# fact about the world: we opened a document and it documented an absence. That is
# evidence of absence, and it must be produced. This set is closed and each member
# was added deliberately; it is not a general permission.
CITED_UNKNOWN_CAUSES = (NOT_EVALUATED, SOURCE_SILENT)


class UncitedVerdict(ValueError):
    """Raised when something tries to assert GREEN or RED without evidence."""


@dataclass(frozen=True)
class Verdict:
    subject_id: str            # stable id of the thing judged
    subject_title: str
    noun: str                  # ASSET | FACT
    use: str                   # the question asked, e.g. "ai_training"
    verdict: str               # GREEN | RED | UNKNOWN
    reason: str                # human sentence, always present
    citation_url: Optional[str] = None    # the instrument / the source
    quoted_terms: Optional[str] = None    # VERBATIM text from that citation
    holder: Optional[str] = None
    interpretive: bool = False # True = our legal reading, not the text's plain words
    cause: Optional[str] = None  # UNKNOWN only: which of CAUSES applies
    published_instrument: Optional[str] = None
    # What the archive actually published, when it differs from citation_url — e.g.
    # it published CC BY-NC-ND 3.0/es and we read the 4.0 text. Quoting one URL while
    # citing another is precisely the substitution this product exists to catch, so it
    # is a field, printed, not a silent equivalence.
    observed_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="seconds")
    )

    def __post_init__(self) -> None:
        if self.verdict == GREEN or self.verdict == RED:
            if self.cause is not None:
                raise ValueError("cause is for UNKNOWN only")
        if self.verdict not in VERDICTS:
            raise ValueError(f"verdict must be one of {VERDICTS}, got {self.verdict!r}")
        if self.noun not in (ASSET, FACT):
            raise ValueError(f"noun must be {ASSET!r} or {FACT!r}, got {self.noun!r}")
        if not self.reason.strip():
            raise ValueError("every verdict must carry a reason, including UNKNOWN")

        if self.verdict in (GREEN, RED):
            if not self.citation_url:
                raise UncitedVerdict(
                    f"{self.verdict} for {self.subject_id!r} has no citation_url. "
                    "A rights claim without the instrument cited is prose, not evidence."
                )
            if not (self.quoted_terms or "").strip():
                raise UncitedVerdict(
                    f"{self.verdict} for {self.subject_id!r} cites {self.citation_url} "
                    "but quotes no terms from it. Fetch the instrument before judging it."
                )
        else:  # UNKNOWN
            if self.cause not in CAUSES:
                raise ValueError(
                    f"UNKNOWN for {self.subject_id!r} must name a cause from {CAUSES}"
                )
            if self.cause in CITED_UNKNOWN_CAUSES:
                # Evidence of absence is still evidence, and it must be produced.
                if not self.citation_url or not (self.quoted_terms or "").strip():
                    raise UncitedVerdict(
                        f"UNKNOWN/{self.cause} for {self.subject_id!r} asserts something "
                        "about a document we opened. That is a claim about a document, so "
                        "the document must be cited and quoted."
                    )
            elif self.citation_url or self.quoted_terms:
                raise UncitedVerdict(
                    f"UNKNOWN/{self.cause} must not carry a citation — "
                    "if there is evidence, judge it."
                )

    def as_dict(self) -> dict:
        return asdict(self)

    @property
    def substituted(self) -> bool:
        return bool(self.published_instrument
                    and self.published_instrument != self.citation_url)

    def line(self) -> str:
        mark = {GREEN: "GREEN  ", RED: "RED    ", UNKNOWN: "UNKNOWN"}[self.verdict]
        flag = "  [interpretive]" if self.interpretive else ""
        return f"{mark} {self.subject_title[:58]:<58} {self.reason}{flag}"
