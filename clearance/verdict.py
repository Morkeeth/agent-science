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
    observed_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="seconds")
    )

    def __post_init__(self) -> None:
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
            if self.citation_url or self.quoted_terms:
                raise UncitedVerdict(
                    "UNKNOWN must not carry a citation — if there is evidence, judge it."
                )

    def as_dict(self) -> dict:
        return asdict(self)

    def line(self) -> str:
        mark = {GREEN: "GREEN  ", RED: "RED    ", UNKNOWN: "UNKNOWN"}[self.verdict]
        flag = "  [interpretive]" if self.interpretive else ""
        return f"{mark} {self.subject_title[:58]:<58} {self.reason}{flag}"
