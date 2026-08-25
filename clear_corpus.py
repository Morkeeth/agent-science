"""Agent Science over the fleet's own research — Oscar's idea: every websearch the
fleet saves becomes a claim Agent Science verifies against its own cited source.

The research corpus (research-corpus/*.md) is written as `[CLAIM] ...` lines each
followed by one or more `[URL] ...` (or a bare URL) lines. This reads those pairs and
runs each through the SAME clearance engine that clears a documentary script: the URL is
the offered source, the engine fetches it and checks whether it VERBATIM states the
claim, or refuses. So a research finding is not trusted because an agent wrote it down —
it clears only if its own cited source actually says it.

  parse_corpus(dir)  -> [(claim_text, url, file, line)]   (deterministic, no network)
  verify_corpus(dir) -> per-claim verdict via clearance.judge_claim (network: fetch+locate)

Offline callers use parse_corpus (tested here). verify_corpus is the live loop; it needs
Parallel/Gemini only for the fetch+locate, never to decide the verdict — clearance.verify
still refuses anything not verbatim in the fetched page.
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Optional

_URL = re.compile(r"https?://[^\s)\]]+")
_CLAIM_TAG = re.compile(r"^\s*\[CLAIM\]\s*(.+)$", re.I)


@dataclass
class CorpusClaim:
    text: str
    url: str
    file: str
    line: int


def _must_contain(claim: str) -> str:
    """A distinctive span the source must contain — the longest quoted phrase if the
    claim quotes one, else the claim's first strong clause. Kept short so the verifier
    checks a real anchor, not the whole sentence."""
    q = re.search(r'"([^"]{6,})"', claim)
    if q:
        return q.group(1)
    # first clause up to a dash/semicolon/comma, capped
    head = re.split(r"[—;,:]| - ", claim, 1)[0].strip()
    return head[:80]


def parse_corpus(corpus_dir: str) -> list[CorpusClaim]:
    """Pair each [CLAIM] with the nearest following URL(s). A bare URL line with no
    preceding [CLAIM] in its block is attached to the last claim seen (the Fable files
    write claim + url as adjacent lines)."""
    out: list[CorpusClaim] = []
    if not os.path.isdir(corpus_dir):
        return out
    for name in sorted(os.listdir(corpus_dir)):
        if not name.endswith(".md"):
            continue
        path = os.path.join(corpus_dir, name)
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                lines = fh.read().splitlines()
        except OSError:
            continue
        pending_claim: str | None = None
        for i, line in enumerate(lines, 1):
            m = _CLAIM_TAG.match(line)
            if m:
                pending_claim = m.group(1).strip()
                inline = _URL.search(line)
                if inline:
                    out.append(CorpusClaim(pending_claim, inline.group(0), name, i))
                continue
            url = _URL.search(line)
            if not url:
                continue
            # Two shapes: (a) my format — a bare [URL] line under a [CLAIM]; (b) Fable
            # format — the claim and its URL on ONE bullet line. Prefer the line's own
            # text as the claim when it carries enough of one; else fall back to the
            # pending [CLAIM].
            own = _line_claim(line)
            claim = own or pending_claim
            if claim:
                out.append(CorpusClaim(claim, url.group(0), name, i))
    return out


# Tags/markup to strip so the claim reads as a sentence, not a bullet with brackets.
_STRIP = re.compile(r"\[(?:URL|REPO|MATH|primary|secondary|internal[\w-]*)\s*:?[^\]]*\]", re.I)


def _line_claim(line: str) -> str | None:
    """The claim text of a one-line 'claim + url' bullet, or None if the line is just a
    URL with no real claim around it."""
    text = _URL.sub(" ", line)          # drop the URL
    text = _STRIP.sub(" ", text)         # drop [URL:]/[REPO:]/[primary] tags
    text = text.lstrip("-*• \t").strip(" —-:·").strip()
    # needs real words, not a stray fragment
    return text if len(text) >= 20 and " " in text else None


def stage_corpus(corpus_dir: str) -> dict:
    """OFFLINE structural stage — parse every claim and report how many carry a fetchable
    source, with ZERO network. This is the dogfood's cheap half: it proves the whole
    corpus reaches the clearance engine's front door before any quota is spent.

    "Fetchable" here is structural, not a live HEAD: an http(s) URL the engine's fetch
    path (urllib) can attempt. A claim with no such URL never entered `parse_corpus`, so
    the honest number is claims-with-a-source over claims-parsed.
    """
    claims = parse_corpus(corpus_dir)
    fetchable = [c for c in claims if c.url.startswith(("http://", "https://"))]
    return {
        "claims": len(claims),
        "fetchable": len(fetchable),
        "distinct_urls": len({c.url for c in claims}),
        "files": len({c.file for c in claims}),
        "rows": [{"file": c.file, "line": c.line, "url": c.url,
                  "must_contain": _must_contain(c.text)} for c in claims],
    }


def verify_corpus(corpus_dir: str, *, fetch: bool = True, live_search: bool = False,
                  limit: Optional[int] = None) -> dict:
    """Run each corpus claim through the clearance engine against its cited URL.

    Returns {sourced, refused, unknown, rows}. NETWORK: fetch (urllib) + locate (the
    DEFAULT string locator, no model). It does NOT search Parallel and does NOT call
    Gemini — the source is named, so the only cost is HTTP fetches. `limit` runs only the
    first N claims, so a small sample proves the path without a full red-build run.
    Import is local so parse_corpus / stage_corpus stay usable with zero dependencies.
    """
    from clearance.facts import Claim, judge_claim
    from clearance.verdict import (GREEN, NO_SOURCE, SOURCE_UNREAD,
                                   SEARCH_FOUND_NOTHING)

    # A fetch that never returned a document is FETCH WEATHER, not a verdict on the
    # claim: it flips run-to-run as a URL 403s or a paywall moves. Bucketing those as
    # UNSOURCED made the dogfood cry wolf (the harness folded 9 dead URLs into
    # "refused"). UNSOURCED must mean ONLY "we read the source and it does not state
    # this" (SOURCE_SILENT / source_does_not_state_it) — the one cause a CI gate can
    # stand on without flapping.
    _FETCH_WEATHER = {NO_SOURCE, SOURCE_UNREAD, SEARCH_FOUND_NOTHING}

    rows = []
    sourced = refused = unknown = 0
    staged = parse_corpus(corpus_dir)
    if limit is not None:
        staged = staged[:limit]
    for i, c in enumerate(staged, 1):
        claim = Claim(claim_id=f"K{i}", text=c.text, source_url=c.url,
                      must_contain=_must_contain(c.text))
        try:
            v = judge_claim(claim, fetch=fetch, live_search=live_search)
        except Exception as e:  # a dead URL / fetch failure is UNKNOWN, never SOURCED
            rows.append({"file": c.file, "line": c.line, "verdict": "UNKNOWN",
                         "cause": f"error: {type(e).__name__}", "url": c.url})
            unknown += 1
            continue
        cause = getattr(v, "cause", "") or ""
        if getattr(v, "verdict", None) == GREEN:
            verdict, bucket = "SOURCED", "sourced"
        elif cause in _FETCH_WEATHER:
            verdict, bucket = "UNKNOWN", "unknown"
        else:  # read it, and it does not carry the claim — the real red-build failure
            verdict, bucket = "UNSOURCED", "refused"
        rows.append({"file": c.file, "line": c.line, "verdict": verdict,
                     "cause": cause, "url": c.url})
        if bucket == "sourced":
            sourced += 1
        elif bucket == "unknown":
            unknown += 1
        else:
            refused += 1
    return {"sourced": sourced, "refused": refused, "unknown": unknown,
            "total": sourced + refused + unknown, "rows": rows}


def main(argv=None) -> int:
    """Dogfood CLI.

      clear_corpus.py [dir]                 offline stage: parse + fetchable-source count
      clear_corpus.py [dir] --verify N      LIVE verify the first N claims (urllib fetch;
                                            no Parallel, no Gemini). --verify all = full
                                            red-build run (heavy: one fetch+locate each).
    """
    import sys
    args = list(argv if argv is not None else sys.argv[1:])
    limit: Optional[int] = 0  # 0 => stage only (offline)
    if "--verify" in args:
        i = args.index("--verify")
        val = args[i + 1] if i + 1 < len(args) else "3"
        limit = None if val == "all" else int(val)
        del args[i:i + 2]
    corpus = args[0] if args else os.path.join(os.path.dirname(__file__), "research-corpus")

    stage = stage_corpus(corpus)
    print(f"STAGE (offline): {stage['claims']} claim(s) parsed from {corpus}")
    print(f"  fetchable source (http/https): {stage['fetchable']}/{stage['claims']}"
          f"  ·  {stage['distinct_urls']} distinct URL(s)  ·  {stage['files']} file(s)")
    for c in stage["rows"][:10]:
        print(f"  {c['file']}:{c['line']}  <- {c['url'][:60]}")

    if limit == 0:
        print("\n(stage only. Pass --verify N to LIVE-verify a sample, "
              "--verify all for the full red-build run.)")
        return 0

    scope = "ALL" if limit is None else f"first {limit}"
    print(f"\nLIVE VERIFY ({scope}) — urllib fetch + string locator, no paid quota:")
    res = verify_corpus(corpus, limit=limit)
    print(f"  SOURCED {res['sourced']}  ·  UNSOURCED {res['refused']}  ·  "
          f"UNKNOWN/error {res['unknown']}  of {res['total']}")
    for r in res["rows"]:
        print(f"  {r['verdict']:9} {r.get('cause') or '':30} {r['url'][:55]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
