"""The semantic guard — a span is evidence only if it ASSERTS the claim.

WHAT THIS CLOSES. `clearance.verify` proves a passage is REAL (verbatim in the fetched
document) and that it MENTIONS the claim's distinctive term. Neither fact can establish
that the passage states the claim. RC5 in the held-out set is the proof, and it sat in
the product as a documented false GREEN from 2026-08-22:

    claim  "This Item is free of known copyright restrictions worldwide."
    span   "Some collections elsewhere are free of known copyright restrictions;
            this Item is not one of them until evaluated."

Verbatim. Carries the terms. Says the opposite.

WHY THE STRUCTURAL VERIFIER COULD NOT SEE IT, stated precisely, because the wrong
diagnosis was available and attractive: it is not that the check was too weak. It is
that `verify(passage, document=, must_contain=)` **never received the claim**. Support is
a relation between two texts and only one of them was ever in the room. The fix is a
parameter first and an algorithm second.

WHAT THIS IS NOT. It is not a reader, it does not "understand" anything, and it cannot
be sold as comprehension. It is three narrow, separately-attributable checks over a
closed class of ENGLISH FUNCTION WORDS — negation, and the binding of a predicate to its
subject. That distinction is load-bearing and is the same law the verifier keeps: a guard
built out of the chrome of the websites we happened to fetch fails open on the third
site; a guard built out of negation cues holds wherever English does. There is a control
(`t_guard_carries_no_site_specific_chrome`) that greps this file to keep it that way.

DIRECTION OF ERROR. Every check can only DEMOTE — turn a GREEN into a named refusal.
None can rescue a span the structural verifier refused, and a control pins that. A false
UNKNOWN costs a re-run; a false GREEN costs a lawsuit. But "refuse more" is not free
either, and the refuse-everything failure is the one this repo has lost a day to before:
so the guard ships with its true-GREEN cost MEASURED and printed, never asserted.
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Optional, Sequence

# EVERY mechanism that can be measured.
CHECKS = ("polarity", "binding", "coverage")

# The mechanisms that may REFUSE. Only one, and the shortlist was cut by measurement,
# not by design taste — see docs/FINDING-semantic-guard-2026-08-31.md:
#
#   binding  and  coverage  both refuse this product's own canonical claim.
#     claim  "An 'In Copyright' item requires permission"
#     span   "For other uses you need to obtain permission from the rights-holder(s)."
#   That span is the operative clause of the instrument and the claim is a fair
#   paraphrase of it. The claim's subject sits in the PREVIOUS sentence, because that is
#   how English works: topic continuity, not repetition. A gate that demands every clause
#   restate its own subject refuses ordinary prose, and "refuse everything" is a failure
#   this repo has already lost a day to.
#
# So they are not gates. They are kept, exported and measured — and `coverage` is used
# where it is actually sound: to PREFER one admissible span over another. Choosing the
# better of two legitimate spans costs nothing; refusing a legitimate span costs a claim.
DEFAULT_CHECKS = ("polarity",)

# One code per mechanism. "the guard fired" is not a finding — a registry row has to say
# WHICH reading of the span refused it, or nobody can audit the refusal.
CONTRADICTED = "claim_contradicted_in_span"
UNDER_NEGATION = "terms_appear_under_negation"
NOT_BOUND = "subject_not_bound"
NOT_CARRIED = "claim_content_not_carried"
CODES = (CONTRADICTED, UNDER_NEGATION, NOT_BOUND, NOT_CARRIED)

# Chosen by MEASUREMENT, not by taste — see docs/FINDING-semantic-guard-2026-08-31.md
# for the sweep over 0.30/0.40/0.50/0.60 on the 177-row registry replay.
DEFAULT_MIN_COVERAGE = 0.40

ENV_FLAG = "CLEARANCE_SEMANTIC_GUARD"

# A CLOSED CLASS OF ENGLISH. Not a heuristic list that grows every time a page defeats
# it — if this list ever needs a domain word added to it, the guard is being overfitted
# and the addition is the bug.
_NEGATORS_RAW = frozenset("""
not no never none nor cannot neither without unlike except excluding
""".split())
# REMOVED 2026-08-31, by measurement: lacks / lacked / lacking / fails / failed /
# nothing / nowhere / unable. Those are LEXICAL VERBS, not function words, and the file
# above claims a closed class of function words — so the list contradicted its own stated
# principle and nobody noticed until it fired. It refused a real span because the
# marketing copy in it ended "then fails." A product whose subject matter is failure will
# say "fails" in every true sentence it publishes.

_STOP_RAW = frozenset("""
a an the this that these those of in on at to for from by with as is are was were be
been being it its their his her our your my and or if then than so such also may might
must can could would should shall will do does did has have had there here about into
over under between per each any all some one two more most other others them they we
you he she i but however although though whereas unless until while when where which who
whom whose what how why said says say
""".split()) | _NEGATORS_RAW

# Clause boundaries. Sentence enders, semicolons and colons, plus the contrastive
# conjunctions that flip what a sentence is asserting. This is the minimum needed to
# tell "X is Y" from "X is Y; Z is not".
_CLAUSE = re.compile(
    r"(?:[.;:!?]+\s+)"
    r"|(?:\s+(?:but|however|although|though|whereas|unless|until|except|while|"
    r"rather\s+than|instead\s+of|other\s+than)\s+)",
    re.IGNORECASE)

# A CORRECTING boundary. After a negation, `but` does not extend the denial across it —
# it replaces the denied element with the affirmed one. "These files are not static
# documentation BUT artifacts that evolve like configuration code" AFFIRMS the second
# half. Measured as a false refusal on exactly that sentence; the clause split was right
# and the polarity check was reading a denial where the grammar marks a correction.
_CONTRAST = re.compile(r"\b(?:but|however|although|though|whereas|rather\s+than|"
                       r"instead\s+of)\b", re.IGNORECASE)

_WORD = re.compile(r"[^\W_]+", re.UNICODE)


def _expand(words) -> frozenset:
    """Close a word list under `_norm`, because tokens are compared AFTER normalising.

    Caught by reading the guard's own output, not by a test: `this` normalised to `thi`,
    which was not in the stop list, so a determiner was being counted as one of the
    claim's subject terms. A stop list written in surface forms and applied to normalised
    tokens is two vocabularies pretending to be one — the wrong-object defect, inside the
    guard built to catch it.
    """
    w = frozenset(words)
    return w | frozenset(_norm(x) for x in w)


def enabled() -> bool:
    """Process default for the guard. Flag exists so the old behaviour is recoverable.

    `CLEARANCE_SEMANTIC_GUARD=0` restores, exactly, the engine that shipped on
    2026-08-30 — including its documented false GREEN on RC5.
    """
    return os.environ.get(ENV_FLAG, "1").strip().lower() not in ("0", "false", "no", "off")


@dataclass(frozen=True)
class Finding:
    code: str
    detail: str


def _norm(tok: str) -> str:
    """Crudest possible morphology: one plural rule, applied to BOTH sides.

    Deliberately not a stemmer. A stemmer would be a second unmeasured component inside
    a guard whose entire selling point is that its every refusal is attributable.
    """
    t = tok.lower()
    return t[:-1] if len(t) > 3 and t.endswith("s") and not t.endswith("ss") else t


_NEGATORS = _expand(_NEGATORS_RAW)
_STOP = _expand(_STOP_RAW)


def tokens(text: str) -> list[str]:
    return [_norm(w) for w in _WORD.findall(text or "")]


def content(text: str) -> set:
    return {t for t in tokens(text) if t not in _STOP and len(t) > 1}


def negators(text: str) -> set:
    toks = set(tokens(text))
    hits = toks & _NEGATORS
    if re.search(r"n['’]t\b", (text or "").lower()):
        hits = hits | {"n't"}
    return hits


def clause_spans(passage: str) -> list[tuple]:
    """(offset, text, separator-that-introduced-it) per clause.

    The separator is kept because `;` and `but` are not the same boundary: one coordinates
    two independent statements, the other corrects the first with the second.
    """
    text, out, pos, sep = passage or "", [], 0, ""
    for m in _CLAUSE.finditer(text):
        if text[pos:m.start()].strip():
            out.append((pos, text[pos:m.start()], sep))
        pos, sep = m.end(), m.group(0)
    if text[pos:].strip():
        out.append((pos, text[pos:], sep))
    return out or [(0, text, "")]


def clauses(passage: str) -> list[str]:
    return [t.strip() for _, t, _sep in clause_spans(passage)]


def _carrier(passage: str, must_contain: str) -> str:
    """The clause that actually carries the claim's distinctive term.

    Support is asserted by ONE clause. Judging the whole passage lets a neighbouring
    sentence lend its subject to a clause that never mentioned it — which is exactly how
    RC5 reads as evidence.
    """
    needle = (must_contain or "").strip().lower()
    if not needle:
        return passage
    # BY OFFSET, not by substring search inside each clause. Searching the clause TEXT
    # failed whenever the term ended on the punctuation the splitter had just consumed:
    # `must_contain` was "…small additions." and every clause had lost its full stop, so
    # no clause matched, the whole passage became the carrier, and a "not" from a
    # NEIGHBOURING clause was read as negating this one. Measured as a false refusal on
    # "these files are not static documentation but … evolve like configuration code" —
    # a contrastive negation that AFFIRMS the claim. The clause boundary was right; the
    # lookup was searching for a string the split had already changed.
    low = passage.lower()
    at = low.find(needle)
    if at < 0:
        at = low.find(needle.rstrip(".,;:!?"))
    if at < 0:
        return passage
    for start, text, _sep in clause_spans(passage):
        if start <= at < start + len(text):
            return text.strip()
    return passage


def _corrected_between(spans: list, i: int, j: int) -> bool:
    """Is a correcting boundary crossed on the way from clause i to clause j?"""
    lo, hi = sorted((i, j))
    return any(_CONTRAST.search(spans[k][2] or "") for k in range(lo + 1, hi + 1))


def _detail(code: str, text: str) -> Finding:
    return Finding(code, f"{code}: {text}")


# --------------------------------------------------------------------- the checks

def check_polarity(passage: str, *, claim: str, must_contain: str) -> Optional[Finding]:
    """Does the span negate what the claim asserts?

    Two directions, because they are different failures:
      (a) the carrier clause itself carries a negation the claim does not;
      (b) a NEIGHBOURING clause names the claim's subject and denies it — the RC5 shape,
          where the true sentence and the denial share one span.

    A negation inside `must_contain` is the CLAIM'S OWN negation and is never a flip.
    "The status of this Item has not been evaluated" is the most common true verdict this
    engine emits; a guard that refused it would have destroyed the product.
    """
    carrier = _carrier(passage, must_contain)
    claim_neg = negators(claim)
    own = negators(must_contain)
    carrier_neg = negators(carrier) - own

    extra = carrier_neg - claim_neg
    if extra:
        return _detail(UNDER_NEGATION,
                       f"the clause carrying {must_contain!r} is negated by "
                       f"{sorted(extra)} and the claim is not; clause: "
                       f"{carrier[:160]!r}")

    subject = content(claim) - content(must_contain)
    if subject:
        spans = clause_spans(passage)
        here = next((i for i, (_, t, _s) in enumerate(spans)
                     if t.strip() == carrier.strip()), None)
        for i, (_start, text, _sep) in enumerate(spans):
            if i == here:
                continue
            c = text.strip()
            neg = negators(c) - own
            if not (neg and (content(c) & subject)):
                continue
            if here is not None and _corrected_between(spans, i, here):
                # "not A but B": the denial stops at the correction.
                continue
            return _detail(
                CONTRADICTED,
                f"a neighbouring clause names the claim's subject "
                f"{sorted(content(c) & subject)} and denies it with {sorted(neg)}: "
                f"{c[:160]!r}")
    return None


def check_binding(passage: str, *, claim: str, must_contain: str) -> Optional[Finding]:
    """Is the claim's SUBJECT the thing the carrier clause is talking about?

    RC5's carrier clause is about "Some collections elsewhere". The claim is about "this
    Item". The words matched; the subject never did. A substring proves a document
    mentions the terms; only the subject binding proves it mentions them ABOUT the thing.
    """
    subject = content(claim) - content(must_contain)
    if not subject:
        return None  # the claim IS the term — nothing left to bind
    carrier = _carrier(passage, must_contain)
    if content(carrier) & subject:
        return None
    return _detail(NOT_BOUND,
                   f"the clause carrying {must_contain!r} shares none of the claim's "
                   f"subject terms {sorted(subject)[:8]}; clause: {carrier[:160]!r}")


def check_coverage(passage: str, *, claim: str, must_contain: str,
                   min_coverage: float = DEFAULT_MIN_COVERAGE) -> Optional[Finding]:
    """Does the span carry the CLAIM, or only its keyword?

    `must_contain` is one distinctive term. A span can contain it and carry almost none
    of what the claim actually says — page furniture around a matching title is the
    common real case. This is the blunt check and it is the one with a number in it, so
    the number is measured and printed, never chosen.
    """
    want = content(claim)
    if not want:
        return None
    got = content(passage)
    ratio = len(want & got) / len(want)
    if ratio < min_coverage:
        missing = sorted(want - got)[:10]
        return _detail(NOT_CARRIED,
                       f"the span carries {len(want & got)}/{len(want)} "
                       f"({ratio:.0%}) of the claim's content terms, below "
                       f"{min_coverage:.0%}; missing {missing}")
    return None


_BY_NAME = {"polarity": check_polarity, "binding": check_binding,
            "coverage": check_coverage}


def coverage(passage: str, claim: str) -> float:
    """Fraction of the claim's content terms the span carries. A RANKING signal.

    Not a gate (see DEFAULT_CHECKS). As a preference between candidate spans that have
    all already passed the verifier and the guard, it is exactly right: when a term
    occurs in a `<nav>` link and again in the operative sentence, both are verbatim, both
    carry the term, and only one is the evidence.
    """
    want = content(claim)
    if not want:
        return 1.0
    return len(want & content(passage)) / len(want)


def inspect(passage: Optional[str], *, claim: str, must_contain: str,
            checks: Sequence[str] = DEFAULT_CHECKS,
            min_coverage: float = DEFAULT_MIN_COVERAGE) -> Optional[Finding]:
    """None if the span may stand as evidence for the claim, else the first finding.

    Runs in the order given so a caller measuring one mechanism can pass `checks=("x",)`
    and get that mechanism's contribution alone.
    """
    if not passage or not (claim or "").strip():
        return None
    for name in checks:
        fn = _BY_NAME[name]
        kw = {"min_coverage": min_coverage} if name == "coverage" else {}
        found = fn(passage, claim=claim, must_contain=must_contain, **kw)
        if found is not None:
            return found
    return None
