# Devpost paste: Agent Science (Agentic Cinema, Parallel track)

## Project name

Agent Science

## Tagline (elevator pitch)

The truth layer for what people believe and use: every checkable claim comes back as a verbatim quote with its source URL, or UNSOURCED with a named reason, and the shelf compounds so the second ask is free.

## Partner track

Parallel

## Hosted project URL

https://agent-science-568004190078.us-central1.run.app

## Open-source repository

https://github.com/Morkeeth/agent-science (MIT, public since 2026-08-22)

## Built with

python, parallel-web (Parallel Search SDK 1.3.2), gemini (Vertex AI), google-cloud-run, google-adk (Agent Development Kit 2.7.1), sqlite, google-cloud-storage

## Try it in 60 seconds (judges)

**Hosted (measured 2026-09-05):** revision `agent-science-00026-zel`, mode `private-workspaces`.
Unauthenticated `/health` returns JSON; `/`, `/visibility/ui`, `/truths/ui`, `/search`, and `POST /clear` hit a **Sign in** wall (or 401). Do not treat open UI URLs as the stranger demo on this revision.

- Public health only: https://agent-science-568004190078.us-central1.run.app/health

**Terminal, no keys (authoritative stranger path):**

```
git clone https://github.com/Morkeeth/agent-science.git && cd agent-science
bash scripts/verify_cold_clone.sh
python3 tests/test_registry_surface.py -q
python3 scripts/compound_exhibit_receipt.py
python3 scripts/eval_artifact_claims.py
bash scripts/demo_truth_layer.sh
```

A cold path on 2026-09-05 re-measured: watch_it_go_red **72/72**, registry **16/16**, bench_check_docs **128/128**, offline compound A=**2**→B=**1** with corpus_hits=**2**, artifact-claims OK after pack honesty.

## About the project

### What it does

Paste a documentary script. Every checkable claim comes back one of two ways: SOURCED, with the exact passage quoted verbatim from the document and its URL, or UNSOURCED, with a named cause a lawyer can read (no admissible source found, holder state not evaluated, every document derived from the same origin). The rule is structural, not a prompt: a model may only locate evidence; if the proposed passage is not verbatim in the fetched document, the verdict is UNSOURCED. It never paraphrases and never infers.

The same engine is a websearch companion for agentic builders. Ask "ralph loop agentic" and you get a primary verdict (sourced, refused with cause, or CONTRARY TO RESEARCH when practitioner adoption outruns the papers) plus the whole search: every variant tried, every route and cost tier, and an imbalance warning when the evidence is GitHub stars only.

Every claim it clears joins a shelf. A claim proven, or proven unprovable, once is free for every production afterward. Re-measure dictionary stats locally with `python3 -m clearance stats` or on a workspace-authenticated hosted session — do not carry a hosted claim count from an older open revision.

### Technological implementation

- Parallel Search API at runtime through the official parallel-web SDK (1.3.2), used for discovery on a dictionary miss.
- Gemini on Vertex AI (`gemini-3.5-flash`) extracts claims and proposes candidate passages; it is never allowed to write the verdict.
- Google Cloud Run hosts private workspaces (2026-09-05: `/health` public; desk and search behind Sign in). Workspace shelf data is tenant-scoped — do not seed cloud from local user case DBs.
- Agent Development Kit (2.7.1) is the default clearance engine on the local/ADK path (`engine_default: adk` in local health when configured).
- Verbatim verification is deterministic code: the fetched document must contain the proposed span, or the row is refused. An independence check refuses claims where every supporting document derives from one origin.
- Three cost tiers: free (registry replay and alias hit), cheap (URL routing to EUR-Lex, arXiv and the rights vocabularies), live (Parallel plus Gemini). `science_lookup` defaults to the free tier.
- Controls (re-measured 2026-09-05): **128** checks across 11 pack suites, **72** mutation-watched; refusal holdout hash-pinned; symmetric scorer baseline 5/6 vs shipping 6/6; artifact-claims gate re-measures pack claims at the submitted commit.

### Design

One product, two doors on the same layer. Locally, the desk takes narration and returns a gap report; `python3 -m clearance visibility --full` shows the websearch companion panes. On the 2026-09-05 hosted revision those UI doors require workspace Sign in — film the local CLI path or an authenticated session, not an open URL.

### Potential impact

The buyer who already owns this budget line is the documentary Errors & Omissions underwriter or the clearance supervisor at a production company. Documentary E&O is a flat premium, roughly $2,000 to $10,000 per film ($2,000 to $3,500 for festival-to-showcase coverage per C&S International Insurance Brokers via Desktop Documentaries; $2,500 to $10,000 for a standard three-year term at a $1M limit per Wrapbook, 2025-10-01). Under that premium sits clearance labor: manual fact-check passes on every narration revision, duplicate researcher hours when the same orphan-works or settlement claims recur across episodes, and the re-open cost when a lawyer cannot show a per-claim audit trail. The gap report is that audit trail: sourced quote plus URL, or named refusal, per claim, and the recurring metric is claims cleared per week against claims caught.

The honest limit: we prove verdict and cause on public scripts today; we do not sell a signed E&O endorsement, and no named buyer has been contacted yet. The volume user is the agent operator who runs `science_lookup` before raw web search; the paying vertical is the clearance desk.

### Quality of the idea

Fact-checkers give you a confidence score. Search engines give you one answer with footnotes. Neither tells you what was skipped or refuses when the source is not there. Agent Science does the non-obvious thing with Parallel and Gemini: it uses them only to find candidate passages, then lets deterministic code decide, and it shows the whole search rather than the summary. The second non-obvious move is the shelf: because verdicts are verbatim spans with URLs, they are reusable across productions, so the most-asked claims get cheaper for everyone. The sealed prediction for this event (second run on a shared shelf returns corpus hits and fewer Parallel calls) was measured on the hosted URL on 2026-08-31 and again on 2026-09-02: Run A 1 Parallel call, Run B 0, corpus hits 1. Re-run on 2026-09-03 on a fresh subject: Run A 1 Parallel call, Run B 1 Parallel call with 1 corpus hit, because the second script carried one new claim; the single-claim reuse shown in the demo cost 0 Parallel calls.

We pointed the desk at our own pitch. It refused our headline. That refusal is in the demo.

### Data sources

EUR-Lex (Directive 2012/28/EU and related CELEX documents), rightsstatements.org vocabularies (InC, CNE), arXiv, GitHub star counts, practitioner blogs and repositories, and a fleet research corpus of 312 claims frozen by hash (`research-corpus/MANIFEST.json`) so every published denominator reproduces from a clean checkout.

### Challenges

- EUR-Lex blocks live fetches (403) from Cloud Run, so the directive routes through a CELEX fixture and the free tier; the live path is proven on rightsstatements.org and arXiv.
- The full orphan-works script on the hosted desk times out at 300 seconds (504); the compound is demonstrated on shorter scripts and on cross-production reuse.
- Alias fragmentation: "2012/28/EU" and "Directive 2012/28/EU" were two shelf entries until the popular-queries surface exposed it; the dashboard now drives alias fixes.
- Our privacy control was a false green (it scanned zero files); it was rewritten on `git grep` and proven red on a planted hit before it was trusted again.

### What we learned

A claim can be correct about the wrong object. Our own buyer numbers ("$15k to $80k of researcher time", "0.5 to 2% of budget") had no primary source and were removed; the claims map in the repo (`docs/CLAIMS-MAP-2026-09-02.md`) checks 35 pitch and submission claims and, re-counted on 2026-09-03, holds 32 PROVEN (29 proven as written plus three whose numbers were updated to the live value) and 3 UNPROVEN as written, each softened in the text. The desk applied the same rule to us that it applies to a script.

### What is next

Export the gap report as an E&O-ready record with stable claim IDs; a buyer-context flip (same asset, different verdict by licensee intent, already in the fixtures); ClaimReview-compatible output for interoperability; and the fleet corpus as a shared shelf so every research session grows everyone's free tier.

## Video

The three-minute trailer shows, in order: the problem, the desk refusing our own headline, a sourced verdict with its EUR-Lex URL, the websearch companion with the whole search shown, the shelf, and the buyer.

## Honesty notes for the judge

- Repository public since 2026-08-22; no API key has ever been in the repository (history grep in `tests/test_watch_it_go_red.py`).
- Eval delta is +1 at n = 6 and not statistically significant; the number is reported as measured.
- The shelf count and hit rate move with use; the values above are the 2026-09-03 readings.
