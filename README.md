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

## The corpus compounds — measured, not asserted

The second production about the same subject reuses what the first one proved.
Two independently written scripts on one subject, corpus wiped first:

Three runs of the same experiment, corpus wiped before each:

| run | production 2 from memory | cost saving |
|---|---:|---:|
| 1 | 6 / 10 — 60% | −43% |
| 2 | 3 / 11 — 27% | — |
| 3 | 4 / 10 — 40% | −14% |

**The direction is robust; the magnitude is not.** Stated honestly: **27–60% of a second
production's claims resolve from memory, saving 14–43% of cost. n = 3.**

The first number measured was 60%, and publishing that alone would have been a
cherry-pick a judge could break by re-running the harness that ships in this repo.

The variance is the **claim extractor**, which is not deterministic — 7, 8 and 11 claims
across runs on identical input — so which claims two productions share moves run to run,
and every figure downstream of it is a sample. The scripts were written to overlap; real
productions may overlap less.

Before this was measured the same claim was **false**: the corpus keyed on the whole
claim sentence, so it only compounded when the identical script was re-run — a thing
nobody would ever do. That version scored **9%, and cost 25% MORE**. Every run since has
beaten it, which is why the architectural claim stands even where the number is noisy.
`measure_compounding.py` is the harness, and its cost model is in the docstring so the
number can be argued with rather than believed.

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
