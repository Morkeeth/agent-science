#!/usr/bin/env python3
"""Agent Science — the clearance desk for factual production.

    script in  ->  claims out, each with the document that supports it,
                   and the ones that cannot be sourced printed with the reason.

THIS IS THE ENTRY POINT A JUDGE RUNS, and it calls both partner services LIVE by
default. Pipeline: Gemini extract -> Parallel search -> fetch -> Gemini locate ->
verifier -> gap report. Corpus remembers verdicts per subject so a second script
on the same topic skips Parallel when a claim was already cleared.

Usage:
    python3 agent_science.py fixtures/scripts/split-sentence.txt
    python3 agent_science.py <file> [--subject dust-bowl] [--offline]
"""
from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Optional

from clearance import corpus
from clearance.extract import GeminiExtractor
from clearance.facts import Claim, judge_claim
from clearance.gemini import GeminiLocator
from clearance.independence import (classify as independence_classify,
                                    note as independence_note)
from clearance.verdict import GREEN, Verdict

# "Nothing states this" and "documents state it, but every one traces to a derived or
# unclassified origin" are DIFFERENT FACTS, and collapsing them to one label is the same
# flattening refused for causes. A production can act on the second - a researcher spends
# two minutes on a flagged source - and cannot act on the first. Neither is CLEARED.
LABEL = {
    "no_independent_source": "UNVERIFIED INDEPENDENCE",
    "no_source_offered": "UNSOURCED",
    "search_found_no_admissible_source": "UNSOURCED",
    "source_does_not_state_it": "UNSOURCED",
    "source_never_fetched": "UNSOURCED",
}
WHY = {
    "no_independent_source": ("documents state this, and every one traces to a derived "
                              "or unclassified origin — a human must judge whether that "
                              "is independent support"),
    "no_source_offered": "no source was offered and none was sought",
    "search_found_no_admissible_source": "we searched and no document we read states it",
    "source_does_not_state_it": "we read the named source; it does not say this",
    "source_never_fetched": "OURS — the source was named but never fetched",
}


def _claim_key(text: str, subject: str, must_contain: str = "") -> str:
    """What makes two claims THE SAME claim.

    Keying on full claim text meant the corpus could only ever compound when the
    identical sentence recurred - i.e. when the SAME script was re-run. Two productions
    about the same event phrase the same fact differently, so the hit rate against a
    genuinely different script was zero by construction, and the pitch's "the second
    production costs a fraction of the first" was measuring a re-run, not a second
    production.

    The distinctive term is what identifies the fact: "Directive 2012/28/EU" is the
    same fact whether the sentence around it says adopted, passed or came into force.
    Fall back to the full text when a claim has no distinctive term, because keying
    everything to an empty string would collide unrelated claims - a false cache hit,
    which is worse than a miss.
    """
    ident = (must_contain or "").strip().lower()
    basis = ident if len(ident) >= 6 else text.strip().lower()
    h = hashlib.sha256(f"{subject}\0{basis}".encode()).hexdigest()
    return h[:20]


def _use(subject: str) -> str:
    return f"sourcing:{subject}"


def _present(v: Verdict) -> str:
    if v.verdict == GREEN:
        return "SOURCED"
    return LABEL.get(v.cause or "", "UNSOURCED")


def _row(v: Verdict, *, corpus_hit: bool = False, asked_as: str = "") -> dict:
    # A corpus hit keyed on the distinctive term is LOOSER than one keyed on the whole
    # sentence: two different assertions sharing a term - "2012/28/EU was passed in
    # 2012" and "2012/28/EU was known as the Orphan Works Directive" - can key the same.
    # We cannot decide structurally whether that is the same fact, so the substitution
    # is PRINTED. The reader sees which claim the reused evidence was originally about.
    reused_from = (v.subject_title if corpus_hit and asked_as
                   and asked_as.strip().lower() != v.subject_title.strip().lower()
                   else None)
    return {
        "reused_from": reused_from,
        "claim_id": v.subject_id,
        "text": v.subject_title,
        "label": _present(v),
        "engine_verdict": v.verdict,
        "cause": v.cause,
        "reason": v.reason,
        "why": WHY.get(v.cause or "", v.reason),
        "citation_url": v.citation_url,
        "quoted_terms": v.quoted_terms,
        # The independence question, carried on the ROW so every surface prints it:
        # markdown report, HTTP JSON, and the paste UI. It was dropped in a rewrite
        # while the import survived - the seam existing is not the seam being called,
        # happening to this repo's own work.
        "source_class": (independence_classify(v.citation_url)[0]
                         if v.citation_url else None),
        "source_note": independence_note(v.citation_url) if v.citation_url else None,
        "corpus_hit": corpus_hit,
        "probe": "corpus_hit" if corpus_hit else v.reason.split("locator:")[-1].strip()
        if "locator:" in v.reason else ("parallel:web_search" if not corpus_hit else "corpus_hit"),
    }


def clear_script(
    script: str,
    *,
    subject: str = "default",
    model: str = "gemini-3.5-flash-lite",
    corpus_db: Optional[Path] = None,
    offline: bool = False,
) -> dict:
    """Run the full pipeline; return JSON-serializable gap report."""
    if offline:
        return {"ok": False, "error": "offline mode is for controls only", "subject": subject}

    db = corpus_db or corpus.DB
    con = corpus.connect(db)
    extractor = GeminiExtractor(model=model)
    claims_raw = extractor.extract(script)
    claims = [
        Claim(f"C{i}", c.text, c.source_url, c.must_contain)
        for i, c in enumerate(claims_raw, 1)
    ]
    locator = GeminiLocator(model=model)
    rows: list[dict] = []
    parallel_calls = 0
    corpus_hits = 0

    for c in claims:
        key = _claim_key(c.text, subject, c.must_contain)
        use = _use(subject)
        hit = corpus.recall(con, key, use)
        if hit:
            corpus_hits += 1
            reason = f"corpus_hit — {hit.reason}"
            v = Verdict(
                subject_id=c.claim_id,
                subject_title=c.text,
                noun=hit.noun,
                use=use,
                verdict=hit.verdict,
                reason=reason,
                cause=hit.cause,
                citation_url=hit.citation_url,
                quoted_terms=hit.quoted_terms,
            )
            rows.append(_row(v, corpus_hit=True, asked_as=c.text))
            continue

        parallel_calls += 1
        v = judge_claim(c, locator=locator, live_search=True, fetch=True)
        store = Verdict(
            subject_id=key,
            subject_title=c.text,
            noun=v.noun,
            use=use,
            verdict=v.verdict,
            reason=v.reason,
            cause=v.cause,
            citation_url=v.citation_url,
            quoted_terms=v.quoted_terms,
        )
        corpus.remember(con, [store])
        rows.append(_row(
            Verdict(
                subject_id=c.claim_id,
                subject_title=c.text,
                noun=v.noun,
                use=use,
                verdict=v.verdict,
                reason=v.reason,
                cause=v.cause,
                citation_url=v.citation_url,
                quoted_terms=v.quoted_terms,
            ),
            corpus_hit=False,
        ))

    sourced = sum(1 for r in rows if r["label"] == "SOURCED")
    n = len(rows)
    return {
        "ok": True,
        "subject": subject,
        "extractor": extractor.name,
        "locator": locator.name,
        "claims_extracted": n,
        "sourced": sourced,
        "unsourced": n - sourced,
        "parallel_calls": parallel_calls,
        "corpus_hits": corpus_hits,
        "rows": rows,
        "markdown": _markdown(rows, subject=subject, n=n, sourced=sourced),
    }


def _markdown(rows: list[dict], *, subject: str, n: int, sourced: int) -> str:
    gaps = n - sourced
    out = [
        f"# GAP REPORT — subject `{subject}`",
        "",
        f"| Claims | {n} |",
        f"| SOURCED | {sourced} ({(sourced/n if n else 0):.0%}) |",
        f"| UNSOURCED | {gaps} ({(gaps/n if n else 0):.0%}) |",
        "",
    ]
    if gaps:
        out += ["## Claims requiring action", ""]
        for r in rows:
            if r["label"] != "SOURCED":
                out.append(f"- **{r['claim_id']}** — {r['label']} ({r['cause']})")
                out.append(f"  {r['why']}")
        out.append("")
    derived = [r for r in rows
               if r["label"] == "SOURCED" and r.get("source_class") == "derived"]
    if derived:
        out += [f"## Source independence — {len(derived)} of {sourced} sourced rows rest "
                "on a DERIVED document", "",
                "A source that is the claim's own origin is not evidence, and nothing at "
                "the passage level can tell self-citation from corroboration: the text "
                "matches perfectly, which is exactly the problem. The engine flags these; "
                "it cannot resolve them. See docs/FINDING-circular-sourcing.md.", ""]
        out += [f"- {r['claim_id']} — {r['citation_url']}" for r in derived]
        out.append("")
    for r in rows:
        if r["label"] == "SOURCED":
            out.append(f"### {r['claim_id']} — SOURCED")
            if r["corpus_hit"]:
                out.append("*Resolved from corpus — no Parallel call.*")
                if r.get("reused_from"):
                    out.append(f'> ⚠ the reused evidence was gathered for a DIFFERENT '
                               f'wording: "{r["reused_from"][:120]}". Same distinctive '
                               f'term, possibly not the same assertion — a human should look.')
            out.append(f"- {r['citation_url']}")
            out.append(f'> "{(r["quoted_terms"] or "")[:200]}"')
            if r.get("source_note"):
                out.append(f"- {r['source_note']}")
            out.append("")
    return "\n".join(out)


def run(path: Path, *, subject: str = "default", offline: bool = False,
        model: str = "gemini-3.5-flash-lite"):
    script = path.read_text()
    print(f"# AGENT SCIENCE — {path.name}\n")
    if offline:
        print("MODE: offline. No claims are extracted and no sources are searched;\n"
              "      offline mode exists for the control suite, not for judging.\n")
        return

    result = clear_script(script, subject=subject, model=model, offline=offline)
    if not result.get("ok"):
        print(result.get("error", "failed"))
        return

    print(f"1. Gemini extracted {result['claims_extracted']} claim(s) [{result['extractor']}]\n")
    for r in result["rows"]:
        tag = r["label"]
        hit = " (corpus_hit)" if r["corpus_hit"] else ""
        print(f"2. {r['claim_id']} — {tag}{hit}")
        if r["label"] == "SOURCED":
            print(f"   {r['citation_url']}")
            print(f'   "{(r["quoted_terms"] or "")[:120]}"')
        else:
            print(f"   {r['why']}")
        print()

    print("=" * 72)
    print(result["markdown"])
    print(f"\nParallel calls: {result['parallel_calls']} · Corpus hits: {result['corpus_hits']}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    subj = "default"
    args = sys.argv[1:]
    if "--subject" in args:
        i = args.index("--subject")
        subj = args[i + 1]
        del args[i : i + 2]
    path = Path(args[0])
    run(path, subject=subj, offline="--offline" in args)
