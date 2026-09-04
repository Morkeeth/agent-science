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

from . import instruments, routing, search as _search
from .locate import DEFAULT, Locator
from .independence import assess as assess_independence
from . import semantic as _semantic
from .verify import verify
from .verdict import (Verdict, GREEN, UNKNOWN, FACT,
                      NO_SOURCE, SOURCE_UNREAD, SOURCE_SILENT, SEARCH_FOUND_NOTHING,
                      NO_INDEPENDENT_SOURCE)

SOURCING = "sourcing"  # the "use" a fact is judged for

# A term can occur hundreds of times in a 95,000-character page. Every occurrence is a
# verify() call; this caps the work per document. Stated as a number so the ceiling is
# visible rather than discovered under load.
_MAX_CANDIDATE_SPANS = 24

# Fewer candidates on first pass — each one costs a fetch + locate. Escalation adds more.
_DEFAULT_CANDIDATES = int(__import__("os").environ.get("PARALLEL_MAX_CANDIDATES", "3"))


def _queries_for(claim: Claim) -> list[str]:
    """Minimal queries that still identify the fact.

    Sending the full sentence AND the distinctive term duplicates the search ask.
    When must_contain is substantial, it is the better probe — shorter, less noise.
    """
    term = (claim.must_contain or "").strip()
    if len(term) >= 6:
        return [term]
    text = claim.text.strip()
    return [text] if text else [term or claim.text]


def _green_from_verified(claim: Claim, verified: list[tuple[str, str]], locator: Locator) -> Verdict:
    ind = assess_independence([u for u, _ in verified])
    primary = [(u, p) for u, p in verified if assess_independence([u])["basis"] == "primary"]
    url, proposed = (primary or verified)[0]
    return Verdict(
        subject_id=claim.claim_id, subject_title=claim.text, noun=FACT,
        use=SOURCING, verdict=GREEN,
        reason=(f"passage verified verbatim; basis: {ind['basis'].upper()} "
                f"({len(ind['independent'])} primary, "
                f"{len(ind['corroborating'])} non-derived origin(s) "
                f"of {ind['origins']}) (locator: {locator.name})"),
        citation_url=url, quoted_terms=proposed.strip())


@dataclass(frozen=True)
class Claim:
    claim_id: str
    text: str                 # the assertion as it appears in the script
    source_url: Optional[str] # the document offered in support
    must_contain: str         # the terms that document must carry


def _trail_row(span: str, refusal, claim: Claim) -> dict:
    """One candidate the locator offered, and the exact reason it was or was not evidence.

    The span is stored WHOLE. Truncating here would put a quotation on an audit page that
    is not the text the engine judged — this product's own founding sin, committed by the
    surface that exists to expose it.
    """
    return {
        "span": span,
        "admissible": refusal is None,
        "code": None if refusal is None else refusal.code,
        "detail": None if refusal is None else refusal.detail,
        "coverage": _semantic.coverage(span or "", claim.text),
    }


def _admissible(locator: Locator, claim: Claim, body: str,
                semantic: Optional[bool],
                trail: Optional[list] = None) -> tuple[Optional[str], object]:
    """The first candidate span that survives the verifier — not the first span proposed.

    THE MEASUREMENT THAT FORCED THIS. Adding the semantic guard dropped the held-out set
    from 5/6 to 4/6: RC1 and RC2 flipped to refusals. Reading the spans rather than the
    score, both had been GREEN on a passage that does not support the claim (a `<nav>`
    link carrying the date; the wrong sentence carrying the other date), because
    `must_contain` occurs TWICE in that document and the locator returned occurrence one.
    They scored correct only because the labels say whether a claim is supported and
    never which span supported it.

    So the guard was not costing true GREENs. It was exposing two false GREENs the set
    could not see, and the fix is not a softer threshold — it is to let the locator keep
    looking. Guarded, this returns the RIGHT sentence for both.

    With the guard off exactly one candidate is considered, so the pre-guard engine is
    reproduced bit for bit.

    `trail`, when a list is passed, receives one row PER CANDIDATE CONSIDERED: the
    span, whether it was admissible, the refusal code and detail that killed it, and
    how much of the claim it carried. This loop is the only place in the engine that
    knows a candidate was ever looked at — everywhere downstream sees one verdict and
    one span, which is why 'why was this refused' has never had an answer beyond the
    winning refusal's code. Recording is free: every value here was already computed.
    """
    use_guard = _semantic.enabled() if semantic is None else semantic
    gen = getattr(locator, "candidates", None)
    if not use_guard or gen is None:
        proposed = locator.propose(claim=claim.text, must_contain=claim.must_contain,
                                   document=body)
        refusal = verify(proposed, document=body, must_contain=claim.must_contain,
                         claim=claim.text, semantic=semantic)
        if trail is not None and proposed:
            trail.append(_trail_row(proposed, refusal, claim))
        return proposed, refusal

    # Take the BEST admissible span, not the first. Both are verbatim, both carry the
    # term; only one is the evidence. Ranking by how much of the claim the span actually
    # carries is the half of the semantic reading that costs nothing — it never refuses
    # anything, it only chooses between spans that already passed every gate.
    first, first_refusal, best, best_score = None, None, None, -1.0
    for n, cand in enumerate(gen(claim=claim.text, must_contain=claim.must_contain,
                                 document=body)):
        if n >= _MAX_CANDIDATE_SPANS:
            break
        refusal = verify(cand, document=body, must_contain=claim.must_contain,
                         claim=claim.text, semantic=semantic)
        if trail is not None:
            trail.append(_trail_row(cand, refusal, claim))
        if refusal is None:
            score = _semantic.coverage(cand, claim.text)
            if score > best_score:
                best, best_score = cand, score
            if score >= 1.0:
                return cand, None
        elif first is None:
            first, first_refusal = cand, refusal
    if best is not None:
        return best, None
    if first is None:
        return None, verify(None, document=body, must_contain=claim.must_contain,
                            claim=claim.text, semantic=semantic)
    return first, first_refusal


def judge_claim(claim: Claim, *, fetch: bool = False,
                locator: Locator = DEFAULT, live_search: bool = False,
                search_candidates: int = _DEFAULT_CANDIDATES,
                semantic: Optional[bool] = None, refresh: bool = False) -> Verdict:
    """`semantic` forces the semantic guard on/off; None follows the process default.

    It is threaded to EVERY verify() call site below — the named-source path, the search
    loop and the escalation loop. Three doors into GREEN; a guard on one of them is a
    guard that tests green and ships two-thirds off.
    """
    # ONE trail per claim, across every door into GREEN. Three call sites verify
    # spans; a trail on one of them would be an audit page that quietly omits two
    # thirds of what the engine looked at, which is worse than no audit page.
    trail: list = []
    fresh = {"refresh": True} if refresh else {}

    def unknown(reason: str, cause: str, **kw) -> Verdict:
        kw.setdefault("trail", tuple(trail))
        return Verdict(subject_id=claim.claim_id, subject_title=claim.text,
                       noun=FACT, use=SOURCING, verdict=UNKNOWN,
                       reason=reason, cause=cause, **kw)

    if not claim.source_url:
        # THE STEP THAT USED TO BE DONE BY A HUMAN OFF-CAMERA. Routing constructs
        # known-primary URLs (CELEX, rights vocab, arXiv) without a search call;
        # Parallel proposes the rest. Each candidate still survives fetch -> locate
        # -> verify. A search result is a lead, never evidence.
        queries = _queries_for(claim)
        routed = routing.candidates_for(text=claim.text,
                                        must_contain=claim.must_contain)
        cands = routed or None
        probe_note = routing.routed_probe(claim.text, claim.must_contain)
        if not cands:
            cands = _search.find_sources(
                objective=f"Find a primary source that states verbatim: {claim.text}",
                queries=queries, live=live_search, max_results=search_candidates,
                term=(claim.must_contain or "").strip().lower()[:120], **fresh)
            probe_note = None
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
            body = instruments.document(c.url, fetch=fetch, **fresh)
            if body is None:
                continue
            read += 1
            proposed, refusal = _admissible(locator, claim, body, semantic, trail)
            if refusal is None:
                verified.append((c.url, proposed))
                # Best case: one PRIMARY source that verifies — stop reading and
                # do not escalate. Every extra fetch is spend with no verdict gain.
                if assess_independence([c.url])["basis"] == "primary":
                    return _green_from_verified(claim, verified, locator)

        # ESCALATION. A researcher who finds only blogs does not stop; they go looking
        # for the statute, the register, the official publication. The first version of
        # this refused instead, and cleared 0 of 10 on a real script - which is not
        # rigour, it is the refuse-everything failure this repo has a control against.
        #
        # The allowlist stays strict. The EFFORT goes up.
        if verified and not assess_independence([u for u, _ in verified])[
                "has_independent_support"]:
            term = (claim.must_contain or claim.text).strip()
            more = _search.find_sources(
                objective=(f"Find the PRIMARY source that states verbatim: {claim.text}. "
                           "Prefer the official publisher: legislation, an official "
                           "register, a government or institutional publication, a court "
                           "record. Not encyclopaedias, blogs or aggregators."),
                queries=[f"{term} official text", f"{term} legislation register"],
                live=live_search, max_results=search_candidates,
                term=(claim.must_contain or "").strip().lower()[:120] + ":escalation", **fresh)
            for c in (more or []):
                if any(c.url == u for u, _ in verified):
                    continue
                body = instruments.document(c.url, fetch=fetch, **fresh)
                if body is None:
                    continue
                read += 1
                proposed, refusal = _admissible(locator, claim, body, semantic, trail)
                if refusal is None:
                    verified.append((c.url, proposed))
                    if assess_independence([c.url])["basis"] == "primary":
                        return _green_from_verified(claim, verified, locator)

        # Routed primaries that did not verify — fall back to Parallel once before
        # reporting empty. CELEX construction can be right while fetch/locate fails.
        if not verified and routed and live_search:
            cands = _search.find_sources(
                objective=f"Find a primary source that states verbatim: {claim.text}",
                queries=queries, live=True, max_results=search_candidates,
                term=(claim.must_contain or "").strip().lower()[:120], **fresh)
            probe_note = None
            if cands:
                for c in cands:
                    if any(c.url == u for u, _ in verified):
                        continue
                    body = instruments.document(c.url, fetch=fetch, **fresh)
                    if body is None:
                        continue
                    read += 1
                    proposed, refusal = _admissible(locator, claim, body, semantic, trail)
                    if refusal is None:
                        verified.append((c.url, proposed))
                        if assess_independence([c.url])["basis"] == "primary":
                            return _green_from_verified(claim, verified, locator)

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
            return _green_from_verified(claim, verified, locator)

        probe = probe_note or queries
        return unknown(
            f"searched, read {read} of {len(cands or [])} candidate document(s), "
            f"none states this claim; probe was {probe!r}",
            SEARCH_FOUND_NOTHING)

    body = instruments.document(claim.source_url, fetch=fetch, **fresh)
    if body is None:
        return unknown(
            f"source {claim.source_url} has never been fetched — "
            "no text on file to quote", SOURCE_UNREAD)

    proposed, refusal = _admissible(locator, claim, body, semantic, trail)
    if refusal is not None:
        # The quotation for a non-finding is a stated, checkable fact ABOUT the
        # document — never an arbitrary slice OF it, which reads as evidence and
        # is not. The locator's name is printed so a wrong refusal is traceable to
        # the implementation that caused it (see docs/FINDING-refusal-correctness).
        return unknown(
            f"no admissible passage found by locator '{locator.name}': {refusal.code}",
            SOURCE_SILENT, citation_url=claim.source_url,
            refusal_code=refusal.code,
            quoted_terms=(f"document opened, {len(body):,} characters read; "
                          f"{refusal.detail}"))

    return Verdict(
        subject_id=claim.claim_id, subject_title=claim.text, noun=FACT,
        use=SOURCING, verdict=GREEN,
        reason=f"the named source states this, passage verified verbatim "
               f"(locator: {locator.name})",
        citation_url=claim.source_url, quoted_terms=proposed.strip(),
        trail=tuple(trail),
    )
