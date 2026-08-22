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

## The corpus — measured, and the saving is NOT yet proven

The second production about the same subject reuses what the first one proved. Whether
that is a *saving* is a measurement, and it is the one claim in this repo that has been
corrected three times. Two independently written scripts on one subject, corpus wiped
before each run:

| run | production 2 from memory | cost | wall clock |
|---|---:|---:|---:|
| 1 | 6 / 10 — 60% | −43% | −21% |
| 2 | 3 / 11 — 27% | — | — |
| 3 | 4 / 10 — 40% | −14% | −16% |
| 4 | 2 / 10 — 20% | — | **+12% SLOWER, and MORE searches** |

**The saving is NOT demonstrated at this scale. n = 4, and the variance swamps it.**

What IS established: sentence-keying made compounding **impossible by construction** —
9% hits and 25% *more* expensive. Term-keying makes it **possible**: every run since has
had real hits. But "possible" is not "a saving", and run 4 was slower than cold with
more live searches, not fewer.

An earlier version of this file claimed 60%, then "27–60%, direction robust". Both were
wrong: the first was a cherry-pick, the second asserted a direction that run 4 broke.
**Three corrections to one number, which is itself the finding — at 7–11 claims per
script the measurement is too noisy to carry a headline.** The open question is whether
it stabilises at 50–100 claims; that experiment has not been run.

The variance is the **claim extractor**, which is not deterministic — 7, 8, 10 and 11
claims across runs on identical input — so which claims two productions share is partly
luck, and at this size two hits either way moves the percentage by twenty points. The
scripts were written to overlap; real productions may overlap less.

`measure_compounding.py` is the harness and its cost model is in the docstring, so the
number can be argued with rather than believed. **Run it yourself; you will get a
different number, and that is the point.**

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
