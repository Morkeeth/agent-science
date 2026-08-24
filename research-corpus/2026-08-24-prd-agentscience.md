# PRD grounding — Agent Science (2026-08-24)

Facts behind `PRD-2026-08.md`. Written in the corpus `[CLAIM]` / `[URL]` shape so the
product can clear its own PRD: `python3 clear_corpus.py` parses these; `verify_corpus`
fetches each URL and checks the claim verbatim, or refuses. Repo-internal facts carry
`[REPO: ...]` (a pointer, not a web source — those clear only against the local file).

## The EU AI Act wedge — dated, penalised, mandatory

- [CLAIM] The European Commission's AI Office published the mandatory template for the public summary of GPAI training content on 24 July 2025, implementing Article 53(1)(d) of Regulation (EU) 2024/1689. [URL: https://digital-strategy.ec.europa.eu/en/faqs/template-general-purpose-ai-model-providers-summarise-their-training-content]
- [CLAIM] The training-content summary obligation has been a legal obligation since 2 August 2025; from 2 August 2026 the AI Office may verify compliance and issue corrective measures. [URL: https://kla.digital/blog/eu-ai-act-august-2026-what-still-applies]
- [CLAIM] Non-compliance may result in fines of up to 3% of the provider's annual total worldwide turnover, or 15,000,000 Euros, whichever is higher. [URL: https://digital-strategy.ec.europa.eu/en/faqs/template-general-purpose-ai-model-providers-summarise-their-training-content]
- [CLAIM] The summary must be updated at least every six months, or sooner on a materially significant update to training data. [URL: https://digital-strategy.ec.europa.eu/en/faqs/template-general-purpose-ai-model-providers-summarise-their-training-content]
- [CLAIM] GPAI models placed on the market before 2 August 2025 have until 2 August 2027 to publish the summary. [URL: https://www.wilmerhale.com/en/insights/blogs/wilmerhale-privacy-and-cybersecurity-law/european-commission-releases-mandatory-template-for-public-disclosure-of-ai-training-data]
- [CLAIM] The template requires narrative summaries, not item-by-item listings, deliberately to protect trade secrets — so no regulator reads a per-item annex; the value is substantiating the narrative, not generating it. [URL: https://digital-strategy.ec.europa.eu/en/faqs/template-general-purpose-ai-model-providers-summarise-their-training-content]

## The competitors — they downweight or score; nobody refuses-or-verifies with independence

- [CLAIM] Factiverse fact-checks by integrating a database of over 350,000 fact-checks and a Stance Detection API that identifies claims in text — it returns a stance/signal, not a refuse-or-verify verdict with source-independence classification. [URL: https://www.factiverse.ai/solutions/api]
- [CLAIM] Patronus AI's flagship hallucination-detection model Lynx detects inaccuracies in retrieval-augmented generation; hosted evaluator API pricing runs about $10-20 per 1,000 calls — it scores a probability of hallucination, it does not emit "this claim is unsourceable" as a first-class output. [URL: https://venturebeat.com/ai/patronus-ai-launches-worlds-first-self-serve-api-to-stop-ai-hallucinations]

## What EXISTS at the object (verified 2026-08-24) — repo-internal, cite the file

- [CLAIM] The hosted service at agent-science-33kamss2jq-uc.a.run.app returns HTTP 200 and /health reports gemini_path vertex:hack-fleet, parallel true, agent_builder true (ADK 2.7.1), engine_default adk — all three partner integrations live. [REPO: cloud/service.py /health handler; live curl 2026-08-24]
- [CLAIM] The Verdict constructor cannot build a GREEN, RED or DISPUTED without a citation_url and quoted_terms — enforced in __post_init__ via UncitedVerdict, with no demo bypass. [REPO: clearance/verdict.py]
- [CLAIM] The verifier refuses any proposed passage that does not occur verbatim in the fetched document, does not carry the claim's distinctive term, or does not read as a statement — structural checks only, no site-specific strings. [REPO: clearance/verify.py]
- [CLAIM] Independence is classified as a property of the source SET: mirrors and caches collapse to one origin_key, and primary/derived/unclassified is printed beside each verdict, never used to silently promote. [REPO: clearance/independence.py]
- [CLAIM] The control suite passes 72 tests, 0 failed, and a refuse-everything locator is asserted to FAIL the held-out set — the guard is watched going red in both directions. [REPO: tests/test_watch_it_go_red.py — 72 passed]
- [CLAIM] clear_corpus.py parses 137 claims from research-corpus/ deterministically with no network, and verify_corpus runs each through the same clearance engine that clears a documentary script. [REPO: clear_corpus.py; python3 clear_corpus.py -> 137 claims parsed]
- [CLAIM] article53.py produces the Article 53(1)(d) evidence annex; the shipped fixture assesses 600 items and reports 524 of 600 (87%) carrying an instrument in which the rights-holder reserved the rights this use would require. [REPO: clearance/article53.py; fixtures/ARTICLE-53-ANNEX.md]

## Honest gaps (verified at the object)

- [CLAIM] clearance/ledger.py — the cross-production refusal ledger meant to compound across every production forever — is NOT imported by the live pipeline (agent_science.py) or the hosted service; the live path uses only the per-subject corpus. The fact leg and the rights/asset leg share the Verdict shape but not a live shared ledger. [REPO: grep ledger agent_science.py cloud/service.py — only CSS class refs, no import]
- [CLAIM] Nothing yet catches a WRONG refusal, a verbatim-but-off-claim passage, or a source that is the claim's own origin; these are flagged open, not solved. [REPO: docs/FINDING-refusal-correctness.md, docs/FINDING-substring-is-not-a-statement.md, docs/FINDING-circular-sourcing.md]
- [CLAIM] The compounding curve was measured on 56 claims across four scripts on one subject; per-claim cost stays flat (~$0.003-0.004) while reuse rises 0->20->39->46%. Unmeasured at real GPAI-dataset scale (hundreds of thousands of items). [REPO: README.md, measure_compounding.py, run_curve.py]
