# Agent Science

**LIVE:** https://agent-science-568004190078.us-central1.run.app · [registry](https://agent-science-568004190078.us-central1.run.app/registry) · [popular](https://agent-science-568004190078.us-central1.run.app/popular/ui)  
**Status:** `docs/STATUS.md` · **Deadline:** Agentic Cinema · Sep 9 2026 · Parallel track

**Paste a documentary script. Get back every checkable claim with the document that
supports it — quoted verbatim — and every claim you cannot source, with the reason
you cannot.**

**Proof:** `python3 scripts/seed_document_cache.py && python3 tests/test_watch_it_go_red.py` → **72/72** mutation controls; orphan-works A/B **2 → 1** Parallel calls offline (`docs/COMPOUND-EXHIBIT-2026-08-29.md`).

**Constraint:** a model may only **locate** evidence. If the proposed passage is not
**verbatim** in the fetched document, the verdict is UNSOURCED — never paraphrase,
never infer.

Built for [Agentic Cinema](https://agentic-cinema.devpost.com/) · Parallel track.

**Architecture:** [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) · diagrams + [screenshots](docs/assets/README.md)

## Stack websearch (use this for all fleet research)

```bash
python3 scripts/boot_registry.py              # once: fleet corpus → registry
python3 scripts/install-mcp.sh                # Cursor: science_search tool
python3 -m clearance search "your query"      # CLI
python3 -m clearance serve                    # HTTP :8080 — /search /registry /clear
```

See **`AGENTS.md`** — route every agent websearch through Agent Science, not raw search.

```bash
python3 scripts/seed_document_cache.py   # offline document cache (cold clone)
python3 agent_science.py fixtures/scripts/documentary-orphan-works.txt
./demo.sh          # the whole story in one command (live keys required)
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

## Why this is a company, not a fact-checker

**The EU AI Act made this filing mandatory, and it has a date and a penalty.**

The Commission's AI Office published a mandatory template on 24 July 2025 implementing
Article 53(1)(d) of Regulation (EU) 2024/1689. Every provider of a general-purpose AI
model must publish a summary of its training content — including free and open-source.

| | |
|---|---|
| **Enforcement begins** | **2 August 2026** |
| **Penalty** | up to 3% of worldwide turnover **or €15,000,000, whichever is higher** |
| **Cadence** | updated **every six months**, or sooner on material change |

**What we do NOT do.** The filing is a *narrative* summary — deliberately not
item-by-item, to protect trade secrets. **No regulator reads a per-item annex.** Anyone
selling "we generate your AI Act disclosure" is selling a paragraph.

**What we do.** The regulation requires telling rightsholders *"to what extent the
conditions for lawful text and data mining ... have been respected."* **An extent cannot
be stated truthfully without being measured.** `clearance/article53.py` produces the
record that the measurement was performed — see `fixtures/ARTICLE-53-ANNEX.md`, where
**524 of 600 items (87%) carry an instrument in which the rights-holder reserved the
rights this use would require**, each instrument named.

**The recurring case, measured on the real corpus:**

    undetermined at filing 1        37 of 600
    without a log, re-opened at every 6-month filing
    over four filings (two years):  148 human enquiries  →  37

All 37 are the same cause: *the holder states copyright was never evaluated.* Those are
the archive's permanent gaps, not ours — they will still be undetermined at filing 8.
**The log's value is not that it resolves them. It remembers that you already tried,
and what you tried.**

Marketplaces sell pre-cleared data. Nobody proves clearance on material you already hold,
and **nobody else can tell you a claim is unsourceable** — absence is not something you
find by searching harder.

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
python3 scripts/seed_document_cache.py
python3 tests/test_watch_it_go_red.py     # 72 passed, 0 failed
python3 tests/test_adk_default_path.py    # 5 passed — engine_default: adk when configured
```

Every control is watched **going red** before it is trusted green. They include five
adversarial proposers, a live-model forced-lie transcript, a network tripwire, a scan
that fails the build if any deploy surface passes a secret in the clear, and — the one
that matters most — a check that a **refuse-everything** locator fails the suite.
A guard that only watches one direction is not a guard.

## Honesty & limitations (worst numbers first)

| Finding | Number | Command |
|---------|--------|---------|
| Eval tie vs naive substring baseline | **5/6 = 0.833** — shipping adds **+0** delta | `python3 scripts/eval_refusal_baseline.py` |
| RC5 substring trap | **Both arms false-GREEN** on the same item | same script, row RC5 |
| Ablation (verify off) | **+0** vs shipping on n=6 | `python3 scripts/eval_refusal_ablation.py` |
| External anchor (live rightsstatements.org) | **2/2 tied** — no delta vs baseline | `python3 scripts/eval_external_anchor.py` |
| Hosted compound (warm subject) | **pass=False** if shelf reused | `docs/RECEIPT-live-compound-exhibit-2026-08-31.md` §2 |
| Hosted orphan-works B | **503** after A succeeded (~5 min) | same receipt §3 |

The verifier wins on independence demotion, transport propagation, and forced-lie refusal — not on the 6-item accuracy score alone. See `docs/QWEN-EVAL-GATE-2026-08-30.md`.

## Known open, deliberately

- `docs/FINDING-refusal-correctness.md` — nothing yet catches a **wrong refusal**
- `docs/FINDING-substring-is-not-a-statement.md` — a passage can be genuine, verbatim,
  on-topic and still not state the claim
- `docs/FINDING-circular-sourcing.md` — a source that is the claim's own origin is not
  evidence, and nothing at the passage level can tell the two apart

MIT licensed.
