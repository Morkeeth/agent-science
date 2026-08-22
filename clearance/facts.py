"""The FACT leg — same engine, same guard, same report, different noun.

A factual claim is cleared exactly the way an asset is: you name the document, you
fetch it, you quote the passage, or you print that you could not.

The predicate is deliberately dumb and deliberately stated: SOURCED means "this
document contains this passage, and that passage carries the claim's terms". It does
NOT mean the claim is true. A clearance desk needs a citable source, not a verdict on
reality, and pretending otherwise is how a fact-checker becomes an oracle nobody can
audit.

Two layers, and the split is the whole design:
    a LOCATOR proposes a passage      — untrusted, swappable, may be a model
    the VERIFIER proves it            — structural, provider-independent, never moves
A locator that hallucinates degrades to a refusal. That is what makes it safe to put
a model behind this interface the day credentials arrive.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from . import instruments, search as _search
from .locate import DEFAULT, Locator
from .independence import assess as assess_independence
from .verify import verify
from .verdict import (Verdict, GREEN, UNKNOWN, FACT,
                      NO_SOURCE, SOURCE_UNREAD, SOURCE_SILENT, SEARCH_FOUND_NOTHING,
                      NO_INDEPENDENT_SOURCE)

SOURCING = "sourcing"  # the "use" a fact is judged for


@dataclass(frozen=True)
class Claim:
    claim_id: str
    text: str                 # the assertion as it appears in the script
    source_url: Optional[str] # the document offered in support
    must_contain: str         # the terms that document must carry


def judge_claim(claim: Claim, *, fetch: bool = False,
                locator: Locator = DEFAULT, live_search: bool = False,
                search_candidates: int = 5) -> Verdict:
    def unknown(reason: str, cause: str, **kw) -> Verdict:
        return Verdict(subject_id=claim.claim_id, subject_title=claim.text,
                       noun=FACT, use=SOURCING, verdict=UNKNOWN,
                       reason=reason, cause=cause, **kw)

    if not claim.source_url:
        # THE STEP THAT USED TO BE DONE BY A HUMAN OFF-CAMERA. Parallel proposes
        # candidate documents; each one still has to survive fetch -> locate -> verify.
        # A search result is a lead, never evidence.
        queries = [claim.text, claim.must_contain]
        cands = _search.find_sources(
            objective=f"Find a primary source that states verbatim: {claim.text}",
            queries=queries, live=live_search, max_results=search_candidates)
        if cands is None:
            return unknown(
                "no source offered for this claim, and no search was performed "
                "(pass live_search=True to look for one)", NO_SOURCE)
        if not cands:
            return unknown(
                f"searched and the search returned nothing: probe was {queries!r}",
                SEARCH_FOUND_NOTHING)
        # GATHER THE WHOLE SET before judging any of it. Returning on the first
        # candidate that verifies made independence unknowable by construction: you
        # cannot assess a set you never assembled, and one citation always looked
        # like enough.
        read, verified = 0, []
        for c in cands:
            body = instruments.document(c.url, fetch=fetch)
            if body is None:
                continue
            read += 1
            proposed = locator.propose(claim=claim.text,
                                       must_contain=claim.must_contain, document=body)
            if verify(proposed, document=body, must_contain=claim.must_contain) is None:
                verified.append((c.url, proposed))

        # ESCALATION. A researcher who finds only blogs does not stop; they go looking
        # for the statute, the register, the official publication. The first version of
        # this refused instead, and cleared 0 of 10 on a real script - which is not
        # rigour, it is the refuse-everything failure this repo has a control against.
        #
        # The allowlist stays strict. The EFFORT goes up.
        if verified and not assess_independence([u for u, _ in verified])[
                "has_independent_support"]:
            more = _search.find_sources(
                objective=(f"Find the PRIMARY source that states verbatim: {claim.text}. "
                           "Prefer the official publisher: legislation, an official "
                           "register, a government or institutional publication, a court "
                           "record. Not encyclopaedias, blogs or aggregators."),
                queries=[f"{claim.must_contain} official text",
                         f"{claim.must_contain} legislation register"],
                live=live_search, max_results=search_candidates)
            for c in (more or []):
                if any(c.url == u for u, _ in verified):
                    continue
                body = instruments.document(c.url, fetch=fetch)
                if body is None:
                    continue
                read += 1
                proposed = locator.propose(claim=claim.text,
                                           must_contain=claim.must_contain,
                                           document=body)
                if verify(proposed, document=body,
                          must_contain=claim.must_contain) is None:
                    verified.append((c.url, proposed))

        if verified:
            ind = assess_independence([u for u, _ in verified])
            if not ind["has_independent_support"]:
                # Documents were found, read and VERIFIED - and every one of them
                # traces to the same origin, or to a derived one. Three citations to
                # one source is one citation. This DEMOTES a row that would otherwise
                # have read SOURCED, which is the whole point of the check.
                origins = ", ".join(sorted(ind["groups"]))
                return unknown(
                    f"{len(verified)} document(s) verified but they collapse to "
                    f"{ind['origins']} non-independent origin(s) [{origins}]; "
                    "derived or unclassified sources are not independent support",
                    NO_INDEPENDENT_SOURCE)
            url, proposed = next((u, p) for u, p in verified
                                 if u.split("/")[2:3] and
                                 assess_independence([u])["has_independent_support"])
            return Verdict(
                subject_id=claim.claim_id, subject_title=claim.text, noun=FACT,
                use=SOURCING, verdict=GREEN,
                reason=(f"source found by search, passage verified verbatim, "
                        f"{len(ind['independent'])} independent origin(s) "
                        f"of {ind['origins']} (locator: {locator.name})"),
                citation_url=url, quoted_terms=proposed.strip())

        return unknown(
            f"searched, read {read} of {len(cands)} candidate document(s), "
            f"none states this claim; probe was {queries!r}",
            SEARCH_FOUND_NOTHING)

    body = instruments.document(claim.source_url, fetch=fetch)
    if body is None:
        return unknown(
            f"source {claim.source_url} has never been fetched — "
            "no text on file to quote", SOURCE_UNREAD)

    proposed = locator.propose(claim=claim.text, must_contain=claim.must_contain,
                               document=body)
    refusal = verify(proposed, document=body, must_contain=claim.must_contain)
    if refusal is not None:
        # The quotation for a non-finding is a stated, checkable fact ABOUT the
        # document — never an arbitrary slice OF it, which reads as evidence and
        # is not. The locator's name is printed so a wrong refusal is traceable to
        # the implementation that caused it (see docs/FINDING-refusal-correctness).
        return unknown(
            f"no admissible passage found by locator '{locator.name}': {refusal.code}",
            SOURCE_SILENT, citation_url=claim.source_url,
            quoted_terms=(f"document opened, {len(body):,} characters read; "
                          f"{refusal.detail}"))

    return Verdict(
        subject_id=claim.claim_id, subject_title=claim.text, noun=FACT,
        use=SOURCING, verdict=GREEN,
        reason=f"the named source states this, passage verified verbatim "
               f"(locator: {locator.name})",
        citation_url=claim.source_url, quoted_terms=proposed.strip(),
    )
