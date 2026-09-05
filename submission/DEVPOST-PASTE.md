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

**Measured 2026-09-05:** hosted revision `agent-science-00026-zel` is `mode: private-workspaces`. Logged-out `/`, `/visibility/ui`, `/truths/ui`, `/registry`, and `/clear` redirect to **Sign in**. Public JSON health remains:

- https://agent-science-568004190078.us-central1.run.app/health → `ok: true`, `mode: private-workspaces`

Oscar may restore a public judge surface or demo from a workspace; until then the stranger proof is the cold clone:

```
git clone https://github.com/Morkeeth/agent-science.git && cd agent-science
bash scripts/cinema_pack_gate.sh
# or:
bash scripts/verify_cold_clone.sh
bash scripts/demo_truth_layer.sh
python3 scripts/compound_exhibit_receipt.py   # offline A=2→B=1 Parallel, corpus_hits≥1
```

`bash scripts/demo_clearance_desk.sh` exits 2 with BLOCKED while the hosted desk requires sign-in.

Film/screenshots from the last public desk: `docs/film/` · pack: `docs/CINEMA-PACK-2026-09-05.md`.

## About the project

### What it does

Paste a documentary script. Every checkable claim comes back one of two ways: SOURCED, with the exact passage quoted verbatim from the document and its URL, or UNSOURCED, with a named cause a lawyer can read (no admissible source found, holder state not evaluated, every document derived from the same origin). The rule is structural, not a prompt: a model may only locate evidence; if the proposed passage is not verbatim in the fetched document, the verdict is UNSOURCED. It never paraphrases and never infers.

The same engine is a websearch companion for agentic builders. Ask "ralph loop agentic" and you get a primary verdict (sourced, refused with cause, or CONTRARY TO RESEARCH when practitioner adoption outruns the papers) plus the whole search: every variant tried, every route and cost tier, and an imbalance warning when the evidence is GitHub stars only.

Every claim it clears joins a shelf. A claim proven, or proven unprovable, once is free for every production afterward. On the hosted URL today: 298 claims, 244 queries logged, dictionary hit rate 0.639, 121 reuses across 23 productions.

### Technological implementation

- Parallel Search API at runtime through the official parallel-web SDK (1.3.2), used for discovery on a dictionary miss; the hosted `/health` endpoint reports `parallel_sdk: true` and `parallel_transport: parallel-web`.
- Gemini on Vertex AI (`gemini-3.5-flash`) extracts claims and proposes candidate passages; it is never allowed to write the verdict.
- Google Cloud Run hosts the desk, the websearch companion and the JSON API; the shelf (the refusal log and the corpus SQLite files) is pulled from and pushed to a Google Cloud Storage bucket around each write (`CORPUS_GCS_URI` and `REFUSAL_LOG_GCS_URI`, set by `deploy.sh`).
- Agent Development Kit (2.7.1) is the default clearance engine (`engine_default: adk`; the report names the tool call `clear_script_tool`).
- Verbatim verification is deterministic code: the fetched document must contain the proposed span, or the row is refused. An independence check refuses claims where every supporting document derives from one origin.
- Three cost tiers: free (registry replay and alias hit), cheap (URL routing to EUR-Lex, arXiv and the rights vocabularies), live (Parallel plus Gemini). `science_lookup` defaults to the free tier.
- Controls: 127 checks across 11 suites, 72 of them mutation-watched (each one is shown to go red when the rule it guards is removed); a refusal holdout set hash-pinned on 2026-09-03 (its last content change is the 2026-08-31 semantic-guard commit, so it is a regression pin, not a pre-tuning freeze); a symmetric scorer that judges baseline and shipping arms on delivered labels only (baseline 5/6, shipping 6/6, McNemar p = 1.0 at n = 6, stated as a real but not significant delta).

### Design

One product, two doors on the same layer. The desk at `/` takes narration and returns a gap report: claims, sourced, unsourced, Parallel calls, a buyer-week strip (claims cleared vs caught over seven days, the number a clearance desk reports upward), a compounding strip (Parallel API vs corpus hits on this run), then every row with its verdict, cause, URL and quoted span. The websearch companion at `/visibility/ui` shows the verdict and the route table under it. The truths dashboard at `/truths/ui` ranks what people actually ask with sourced and miss counts. Refusals sit in the same column as evidence, on purpose: what the desk cannot prove is the report the buyer pays for.

Measured on the hosted desk on 2026-09-03: the pitch headline "94% of film archives are unclearable for AI training" returned 1 claim, 0 sourced, 1 UNSOURCED, cause `search_found_no_admissible_source`, 0 Parallel calls. One line about Directive 2012/28/EU returned 1 claim, 1 SOURCED, the EUR-Lex URL, the verbatim span, source class PRIMARY (EU primary law), 0 Parallel calls and 1 corpus hit, in 18 seconds.

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
