# Agent Science

**A production cannot be insured until every fact is sourced. Today that is done by hand,
and a miss is a lawsuit.**

Paste a documentary script. Get back every checkable claim with the document that
supports it — quoted verbatim — and the ones that cannot be sourced printed with the
reason.

Built for [Agentic Cinema](https://agentic-cinema.devpost.com/) · Parallel track.

```bash
python3 agent_science.py fixtures/scripts/documentary-orphan-works.txt
./demo.sh          # the whole story in one command
```

## The one rule

**A model may only LOCATE evidence. It may never ASSERT it.**

Gemini proposes a passage. `clearance/verify.py` proves that passage occurs **verbatim**
in the fetched document, carries the claim's own terms, and reads as a statement rather
than a run of link labels. If it does not, the verdict is UNSOURCED — never SOURCED.

This is enforced in a constructor, not by convention: `Verdict.__post_init__` **cannot
build** a GREEN, RED or DISPUTED without a citation and quoted terms. There is no path
around it, including for a demo.

## What it refuses, and why that is the product

| Verdict | Means |
|---|---|
| **SOURCED** | a fetched document states this, in these words, from an independent origin |
| **UNSOURCED** | no source, or none we read states it, or every source traces to one origin |
| **DISPUTED** | a fetched document states something incompatible, quoted verbatim |

Three things it does that a web search with citations does not:

**Independence is a property of the source SET, not of a verdict.** Three sources that
all trace to one origin are one source. Every Wikipedia mirror is Wikipedia; every cache
is the page it cached. On the demo script this **demoted 3 of 6 sourced claims** — a
worse number, and the true one.

**Unclassified is never promoted to primary.** For a clearance desk the two errors cost
very differently: promoting a blog to primary and being wrong is a cleared claim that
gets a production sued; demoting a real source is a human spending two minutes
overruling a flag the report already shows them. One is a lawsuit, the other is a click.

**It prints the questions it cannot answer.** A source that may be derived, a cache hit
whose evidence was gathered for a different wording, a verdict resting on our legal
reading rather than the document's plain words — each is flagged rather than resolved
silently in our own favour.

## The corpus compounds — measured at 56 claims

Four independently written scripts on one subject, run in sequence into one corpus.
Not an A-to-B pair: the shape a buyer actually experiences.

| production | claims | from memory | cost / claim |
|---|---:|---:|---:|
| 1 | 15 | 0% | $0.00377 |
| 2 | 10 | 20% | $0.00309 |
| 3 | 18 | 39% | $0.00396 |
| 4 | 13 | 46% | $0.00352 |

**Reuse compounds, monotonically: 0 → 20 → 39 → 46%.** Cumulative 15 of 56 = 27%.

**Cost per claim does not fall, and that is the more interesting result.** Reuse rises
while spend stays flat because **the corpus removes the EASY claims first**. What remains
is a residue of hard ones needing escalation — a second search aimed at a primary source.
Each production checks a higher proportion of difficult claims than the last.

**So the saving is in claims a researcher no longer has to chase by hand, not in the API
bill.** That is invisible in a single ratio and only shows up in a curve.

Earlier versions of this file published 60%, then 27-60%, then "not demonstrated" — three
corrections, each caught by the repo re-running its own harness and disagreeing with the
README. `measure_compounding.py` and `run_curve.py` ship here; run them.

## Runtime integrations

| | How |
|---|---|
| **Google Cloud AI** | Vertex AI via ADC — answers as `gemini-3.5-flash (vertex:<project>)`. Falls back to an AI Studio key only when ADC is absent, and the verdict records **which path answered** |
| **Parallel Search** | `clearance/search.py` — finds the source document. Until this existed, every claim arrived with a source URL filled in by hand |

Keys are read at runtime from `~/.config/keys/*.key` (0600) and never enter this repo. A
control greps the working tree **and `git log -p --all`** to keep it that way, and another
fails the build if any deploy surface passes a secret via `--set-env-vars`.

## Controls

```bash
python3 tests/test_watch_it_go_red.py     # 56 passed, 0 failed
```

Every control is watched **going red** before it is trusted green. They include five
adversarial proposers, a live-model forced-lie transcript, a network tripwire, and — the
one that matters most — a check that a **refuse-everything** locator fails the suite.
A guard that only watches one direction is not a guard.

## Known open, deliberately

- `docs/FINDING-refusal-correctness.md` — nothing yet catches a **wrong refusal**
- `docs/FINDING-substring-is-not-a-statement.md` — a passage can be genuine, verbatim,
  on-topic and still not state the claim
- `docs/FINDING-circular-sourcing.md` — a source that is the claim's own origin is not
  evidence, and nothing at the passage level can tell the two apart

MIT licensed.
