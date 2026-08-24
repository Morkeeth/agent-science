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


def verify_corpus(corpus_dir: str, *, fetch: bool = True, live_search: bool = False) -> dict:
    """Run each corpus claim through the clearance engine against its cited URL.

    Returns {sourced, refused, unknown, rows}. NETWORK: fetch+locate. Import is local so
    parse_corpus stays usable with zero dependencies.
    """
    from clearance.facts import Claim, judge_claim
    from clearance.verdict import GREEN

    rows = []
    sourced = refused = unknown = 0
    for i, c in enumerate(parse_corpus(corpus_dir), 1):
        claim = Claim(claim_id=f"K{i}", text=c.text, source_url=c.url,
                      must_contain=_must_contain(c.text))
        try:
            v = judge_claim(claim, fetch=fetch, live_search=live_search)
        except Exception as e:  # a dead URL / fetch failure is UNKNOWN, never SOURCED
            rows.append({"file": c.file, "line": c.line, "verdict": "UNKNOWN",
                         "cause": f"error: {type(e).__name__}", "url": c.url})
            unknown += 1
            continue
        ok = getattr(v, "verdict", None) == GREEN
        rows.append({"file": c.file, "line": c.line,
                     "verdict": "SOURCED" if ok else "UNSOURCED",
                     "cause": getattr(v, "cause", ""), "url": c.url})
        if ok:
            sourced += 1
        else:
            refused += 1
    return {"sourced": sourced, "refused": refused, "unknown": unknown,
            "total": sourced + refused + unknown, "rows": rows}


def main(argv=None) -> int:
    import sys
    args = argv if argv is not None else sys.argv[1:]
    corpus = args[0] if args else os.path.join(os.path.dirname(__file__), "research-corpus")
    claims = parse_corpus(corpus)
    print(f"{len(claims)} claim(s) parsed from {corpus}")
    for c in claims[:20]:
        print(f"  {c.file}:{c.line}  {c.text[:70]!r}  <- {c.url[:50]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
