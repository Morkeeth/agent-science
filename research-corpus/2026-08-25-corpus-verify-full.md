# Corpus verify — full red-build run

**Date:** 2026-08-25  ·  **Command:** `python3 clear_corpus.py --verify all`  ·  **Path:** urllib fetch + default string locator (no Parallel, no Gemini, no paid quota)

This is the Agent Science dogfood: every claim the fleet saved to `research-corpus/` is run through the SAME clearance engine that clears a documentary script. Each claim names its own cited URL; the engine fetches that URL and checks whether it VERBATIM carries the claim's distinctive span, or refuses. A research finding clears only if its own cited source actually states it.

## Counts

170 claims parsed from 17 files (128 distinct URLs). Two count views:

| bucket | script raw | re-bucketed by cause |
|---|---|---|
| SOURCED | 28 | 28 |
| UNSOURCED | 142 | 133 |
| UNKNOWN (dead-url / fetch-error) | 0 | 9 |
| **total** | **170** | **170** |

**Why the two columns differ — a real finding from the dogfood.** `verify_corpus` counts a claim UNKNOWN only when `judge_claim` raises a Python exception. But `instruments.document()` swallows every fetch failure (403/404/network/timeout) and returns `None`, so a dead URL comes back as an UNKNOWN verdict with cause `source_never_fetched` — which the harness's top-line then folds into its `refused` (UNSOURCED) bucket. So the script prints `UNSOURCED 142 · UNKNOWN 0`, but 9 of those 142 are dead URLs, not refusals. The re-bucketed column splits them apart by the verdict's own `cause` field (the verdict rule itself was NOT changed):

- **UNSOURCED (real, gate-relevant):** cause `source_does_not_state_it` — the source was fetched and read, and it does not verbatim carry the claim. This is a research finding failing its own evidence gate.
- **UNKNOWN (not a verdict on the claim):** cause `source_never_fetched` — the fetch failed (paywall, 403/404, dead host, JS-only page). The engine could not read the document, so it makes no claim about whether the source states the finding.

## UNSOURCED — the honest negative space (133 rows)

These are the red-build failures: a saved research finding whose OWN cited source does not verbatim state it. Cause is `source_does_not_state_it` for every row (the source opened and was read; the locator found no admissible passage carrying the claim's span). No claim below was edited or deleted to improve the number.

| file:line | url |
|---|---|
| 2026-08-24-execute-and-compare-whitespace.md:40 | https://github.com/0xmariowu/AgentLint |
| 2026-08-24-execute-and-compare-whitespace.md:41 | https://github.com/carlrannaberg/cclint |
| 2026-08-24-execute-and-compare-whitespace.md:42 | https://github.com/felixgeelhaar/cclint |
| 2026-08-24-execute-and-compare-whitespace.md:43 | https://dev.to/vamshidhar_reddy_392c2302/i-built-a-linter-that-proves-74-of-your-agentsmd-is-wasting-your-ai-agents-time-46an |
| 2026-08-24-execute-and-compare-whitespace.md:45 | https://www.sri.inf.ethz.ch/publications/gloaguen2026agentsmd |
| 2026-08-24-kaggle-ceiling-research.md:50 | https://arxiv.org/abs/2507.20526 |
| 2026-08-24-kaggle-ceiling-research.md:51 | https://arxiv.org/abs/2507.20526 |
| 2026-08-24-kaggle-ceiling-research.md:52 | https://arxiv.org/abs/2507.20526 |
| 2026-08-24-kaggle-ceiling-research.md:57 | https://arxiv.org/abs/2509.22830 |
| 2026-08-24-kaggle-ceiling-research.md:58 | https://arxiv.org/abs/2509.22830 |
| 2026-08-24-kaggle-ceiling-research.md:65 | https://arxiv.org/html/2605.30686v1 |
| 2026-08-24-kaggle-ceiling-research.md:66 | https://arxiv.org/html/2605.30686v1 |
| 2026-08-24-kaggle-ceiling-research.md:69 | https://sqmagazine.co.uk/prompt-injection-statistics/ |
| 2026-08-24-kaggle-ceiling-research.md:70 | https://sqmagazine.co.uk/prompt-injection-statistics/ |
| 2026-08-24-kaggle-ceiling-research.md:73 | https://www.emergentmind.com/topics/agentdojo-benchmark |
| 2026-08-24-kaggle-ceiling-research.md:74 | https://arxiv.org/abs/2509.22830 |
| 2026-08-24-kaggle-ceiling-research.md:75 | https://arxiv.org/abs/2503.00061 |
| 2026-08-24-kaggle-ceiling-research.md:81 | https://github.com/openai/harmony |
| 2026-08-24-kaggle-ceiling-research.md:82 | https://www.geeky-gadgets.com/gpt-oss-jailbreak-2025/ |
| 2026-08-24-kaggle-ceiling-research.md:96 | https://arxiv.org/abs/2509.22830 |
| 2026-08-24-patent-103-fight.md:84 | https://arxiv.org/abs/2512.22886 |
| 2026-08-24-patent-angle-generation.md:13 | https://www.uspto.gov/web/offices/pac/mpep/s2153.html |
| 2026-08-24-patent-angle-generation.md:22 | https://arxiv.org/html/2506.11887 |
| 2026-08-24-patent-angle-generation.md:23 | https://arxiv.org/html/2605.18796 |
| 2026-08-24-patent-angle-generation.md:24 | https://arxiv.org/pdf/2502.01459 |
| 2026-08-24-patent-angle-generation.md:34 | https://arxiv.org/abs/2404.18971 |
| 2026-08-24-patent-angle-generation.md:35 | https://en.wikipedia.org/wiki/Circular_reporting |
| 2026-08-24-patent-angle-generation.md:36 | https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/10331682 |
| 2026-08-24-patent-angle-generation.md:37 | https://newsguardtech.com |
| 2026-08-24-patent-angle-generation.md:45 | https://arxiv.org/abs/2507.03620 |
| 2026-08-24-patent-angle-generation.md:47 | https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/9633674 |
| 2026-08-24-patent-angle-generation.md:55 | https://arxiv.org/abs/2510.25694 |
| 2026-08-24-patent-angle-generation.md:56 | https://arxiv.org/html/2503.14443 |
| 2026-08-24-patent-angle-generation.md:57 | https://docs.python.org/3/library/doctest.html |
| 2026-08-24-patent-angle-generation.md:58 | https://patents.google.com/patent/US8607193B2/en |
| 2026-08-24-patent-angle-generation.md:59 | https://github.com/YawLabs/ctxlint |
| 2026-08-24-patent-angle-generation.md:65 | https://www.grammarly.com/authorship |
| 2026-08-24-patent-angle-generation.md:66 | https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/12462318 |
| 2026-08-24-patent-angle-generation.md:75 | https://www.amazon.science/blog/custom-policy-checks-help-democratize-automated-reasoning |
| 2026-08-24-patent-angle-generation.md:81 | https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/9633674 |
| 2026-08-24-patent-angle-generation.md:82 | https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/11289096 |
| 2026-08-24-patent-angle-generation.md:83 | https://aclanthology.org/2021.emnlp-main.143.pdf |
| 2026-08-24-patent-angle-generation.md:89 | https://arxiv.org/html/2605.18796 |
| 2026-08-24-patent-angle1-draft-ready.md:4 | https://arxiv.org/html/2605.18796 |
| 2026-08-24-patent-authorship-outcome.md:18 | https://www.grammarly.com/authorship |
| 2026-08-24-patent-authorship-outcome.md:20 | https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/12462318 |
| 2026-08-24-patent-authorship-outcome.md:22 | https://arxiv.org/pdf/2408.04682 |
| 2026-08-24-patent-authorship-outcome.md:24 | https://arxiv.org/pdf/2603.04212 |
| 2026-08-24-patent-authorship-outcome.md:26 | https://arxiv.org/abs/2508.02866 |
| 2026-08-24-patent-authorship-outcome.md:33 | https://github.blog/ai-and-ml/github-copilot/the-road-to-better-completions-building-a-faster-smarter-github-copilot-with-a-new-custom-model/ |
| 2026-08-24-patent-authorship-outcome.md:34 | https://www.erichorvitz.com/copilot_display_AAAI.pdf |
| 2026-08-24-patent-authorship-outcome.md:35 | https://arxiv.org/pdf/2403.09507 |
| 2026-08-24-patent-authorship-outcome.md:36 | https://arxiv.org/pdf/2511.18849 |
| 2026-08-24-patent-authorship-outcome.md:37 | https://github.com/mehrtam/gitwhy |
| 2026-08-24-patent-authorship-outcome.md:44 | https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/7043435 |
| 2026-08-24-patent-authorship-outcome.md:45 | https://patents.google.com/patent/US10657549B2/en |
| 2026-08-24-patent-authorship-outcome.md:46 | https://docs.promptlayer.com/features/prompt-registry/overview |
| 2026-08-24-patent-authorship-outcome.md:47 | https://www.braintrust.dev/articles/best-prompt-versioning-tools-2025 |
| 2026-08-24-patent-authorship-outcome.md:48 | https://github.com/gepa-ai/gepa |
| 2026-08-24-patent-authorship-outcome.md:49 | https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/12536208 |
| 2026-08-24-patent-counsel-priorart.md:92 | https://arxiv.org/abs/2502.19335 |
| 2026-08-24-patent-counsel-priorart.md:93 | https://arxiv.org/abs/2509.21837 |
| 2026-08-24-patent-narrow-angle.md:22 | https://arxiv.org/pdf/2510.25402 |
| 2026-08-24-patent-narrow-angle.md:24 | https://patents.google.com/patent/US8572048B2/en |
| 2026-08-24-patent-narrow-angle.md:26 | https://patents.google.com/patent/US9367373B2/en |
| 2026-08-24-patent-narrow-angle.md:28 | https://patents.google.com/patent/EP1852811A2/en |
| 2026-08-24-patent-narrow-angle.md:33 | https://bmdpat.com/blog/ai-agent-claims-done-verify-2026 |
| 2026-08-24-patent-narrow-angle.md:36 | https://arxiv.org/pdf/2604.21375 |
| 2026-08-24-patent-narrow-angle.md:41 | https://www.statology.org/simpsons-paradox-when-aggregated-data-tells-a-different-story/ |
| 2026-08-24-patent-narrow-angle.md:43 | https://www.braintrust.dev/articles/best-hallucination-detection-tools-2026 |
| 2026-08-24-patent-prior-art-composition-honesty.md:6 | https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7175433/ |
| 2026-08-24-patent-prior-art-composition-honesty.md:7 | https://www.statology.org/simpsons-paradox-when-aggregated-data-tells-a-different-story/ |
| 2026-08-24-patent-prior-art-composition-honesty.md:9 | https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/8180717 |
| 2026-08-24-patent-prior-art-composition-honesty.md:10 | https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/8959047 |
| 2026-08-24-patent-prior-art-composition-honesty.md:12 | https://arxiv.org/html/2605.10516v1 |
| 2026-08-24-patent-prior-art-composition-honesty.md:13 | https://arxiv.org/html/2602.16666v1 |
| 2026-08-24-prd-agentscience.md:10 | https://digital-strategy.ec.europa.eu/en/faqs/template-general-purpose-ai-model-providers-summarise-their-training-content |
| 2026-08-24-prd-agentscience.md:11 | https://kla.digital/blog/eu-ai-act-august-2026-what-still-applies |
| 2026-08-24-prd-agentscience.md:12 | https://digital-strategy.ec.europa.eu/en/faqs/template-general-purpose-ai-model-providers-summarise-their-training-content |
| 2026-08-24-prd-agentscience.md:13 | https://digital-strategy.ec.europa.eu/en/faqs/template-general-purpose-ai-model-providers-summarise-their-training-content |
| 2026-08-24-prd-agentscience.md:14 | https://www.wilmerhale.com/en/insights/blogs/wilmerhale-privacy-and-cybersecurity-law/european-commission-releases-mandatory-template-for-public-disclosure-of-ai-training-data |
| 2026-08-24-prd-agentscience.md:15 | https://digital-strategy.ec.europa.eu/en/faqs/template-general-purpose-ai-model-providers-summarise-their-training-content |
| 2026-08-24-prd-agentscience.md:19 | https://www.factiverse.ai/solutions/api |
| 2026-08-24-prd-helicon.md:27 | https://arxiv.org/abs/2511.12884 |
| 2026-08-24-prd-helicon.md:37 | https://github.com/YawLabs/ctxlint |
| 2026-08-24-prd-zup.md:96 | https://verify-agents-workshop.github.io/ |
| 2026-08-24-prd-zup.md:101 | https://arxiv.org/abs/2607.05397 |
| 2026-08-24-prompting-coach.md:57 | https://www.inflectra.com/Ideas/Topic/AI-Agent-Prompt-Engineering.aspx |
| 2026-08-24-prompting-coach.md:58 | https://claude.com/blog/best-practices-for-prompt-engineering |
| 2026-08-24-prompting-coach.md:59 | https://artjoker.net/blog/ai-prompt-engineering-best-practices/ |
| 2026-08-24-prompting-coach.md:60 | https://musketeerstech.com/blogs/prompt-engineering-best-practices/ |
| 2026-08-24-prompting-coach.md:61 | https://arxiv.org/html/2603.16348v1 |
| 2026-08-24-prompting-coach.md:62 | https://arxiv.org/abs/2606.26300 |
| 2026-08-24-prompting-coach.md:63 | https://verify-agents-workshop.github.io/ |
| 2026-08-24-stranger-auditor-checks.md:8 | https://link.springer.com/article/10.1007/s10664-023-10397-6 |
| 2026-08-24-stranger-auditor-checks.md:9 | https://arxiv.org/pdf/2212.01479 |
| 2026-08-24-stranger-auditor-checks.md:12 | https://www.betterclaw.io/blog/agents-md-best-practices |
| 2026-08-24-stranger-auditor-checks.md:13 | https://www.agentlint.app/blog/writing-a-good-agents-md/ |
| 2026-08-24-stranger-auditor-checks.md:14 | https://www.aicodex.to/articles/claude-md-maintenance |
| 2026-08-24-stranger-auditor-checks.md:15 | https://www.aicodex.to/articles/claude-md-maintenance |
| 2026-08-24-stranger-auditor-checks.md:16 | https://tianpan.co/blog/2026-02-14-writing-effective-agent-instruction-files |
| 2026-08-24-stranger-auditor-checks.md:17 | https://www.agentlint.app/blog/writing-a-good-agents-md/ |
| 2026-08-24-stranger-auditor-checks.md:18 | https://github.com/cli/cli/issues/14075 |
| 2026-08-24-stranger-auditor-checks.md:19 | https://hackernoon.com/when-documentation-lies-detecting-drift-between-code-and-reality |
| 2026-08-24-stranger-auditor-checks.md:25 | https://github.com/YawLabs/ctxlint |
| 2026-08-24-stranger-auditor-checks.md:26 | https://github.com/YawLabs/ctxlint |
| 2026-08-24-stranger-auditor-checks.md:27 | https://github.com/0xmariowu/AgentLint |
| 2026-08-24-stranger-auditor-checks.md:28 | https://github.com/carlrannaberg/cclint |
| 2026-08-24-stranger-auditor-checks.md:30 | https://agentlinter.com/ |
| 2026-08-24-stranger-auditor-checks.md:32 | https://www.agentlint.app/blog/writing-a-good-agents-md/ |
| 2026-08-24-stranger-auditor-checks.md:37 | https://www.betterclaw.io/blog/agents-md-best-practices |
| 2026-08-24-stranger-auditor-checks.md:42 | https://github.com/YawLabs/ctxlint |
| 2026-08-24-stranger-auditor-checks.md:43 | https://www.systemshardening.com/articles/cicd/pre-commit-security-hooks/ |
| 2026-08-24-stranger-auditor-checks.md:44 | https://iceberglakehouse.com/posts/agentic-coding-tools/ |
| 2026-08-24-stranger-auditor-checks.md:46 | https://dosu.dev/blog/how-to-catch-documentation-drift-claude-code-github-actions |
| 2026-08-24-verification-stack-positioning.md:10 | https://www.norm.ai/resources/norm-ai-raises-20-million-at-a-1-2-billion-valuation |
| 2026-08-24-verification-stack-positioning.md:11 | https://www.barchart.com/story/news/925121/gen-and-openclaw-team-co-host-post-rsa-event-showcasing-the-future-of-safe-ai-agents |
| 2026-08-24-verification-stack-positioning.md:14 | https://aws.amazon.com/blogs/machine-learning/build-trustworthy-ai-agents-with-amazon-bedrock-agentcore-observability |
| 2026-08-24-verification-stack-positioning.md:18 | https://www.braintrust.dev/articles/best-hallucination-detection-tools-2026 |
| 2026-08-24-verification-stack-positioning.md:22 | https://arxiv.org/pdf/2503.03750 |
| 2026-08-24-verification-stack-positioning.md:23 | https://arxiv.org/pdf/2604.08401 |
| 2026-08-24-verification-stack-positioning.md:28 | https://www.grammarly.com/blog/company/superhuman-authorship-docs/ |
| 2026-08-24-verification-stack-positioning.md:29 | https://arxiv.org/html/2608.00966v1 |
| 2026-08-24-verification-stack-positioning.md:30 | https://link.springer.com/chapter/10.1007/978-3-032-21321-1_32 |
| 2026-08-24-verification-stack-positioning.md:37 | https://techcrunch.com/2026/07/07/ai-law-startup-norm-raises-120m-hits-unicorn-valuation/ |
| 2026-08-24-verification-stack-positioning.md:38 | https://newmarketpitch.com/blogs/news/ai-safety-funding-news |
| 2026-08-24-verification-stack-positioning.md:39 | https://zylos.ai/research/2026-05-01-ai-agent-governance-compliance-2026/ |
| 2026-08-24-verification-stack-positioning.md:41 | https://www.digitalapplied.com/blog/ai-agent-governance-policy-compliance-2026 |
| 2026-08-24-verification-stack-positioning.md:46 | https://allthingsagentichackathon.devpost.com/rules |
| 2026-08-24-verification-stack-positioning.md:47 | https://allthingsagentichackathon.devpost.com/rules |
| 2026-08-25-agentscience-log.md:15 | https://www.nfx.com/post/network-effects-manual |
| 2026-08-25-zup-onemove.md:35 | https://pickaxe.co/post/human-in-the-loop-ai-agents |
| 2026-08-25-zup-onemove.md:36 | https://www.teneo.ai/blog/next-best-action-software |

## UNKNOWN — fetch failed, no verdict on the claim (9 rows)

Cause `source_never_fetched`. The URL could not be read (paywall/403/404/dead), so the engine refuses to rule on the finding. These are NOT UNSOURCED — the claim may well be stated at the source; we simply could not open it.

| file:line | url |
|---|---|
| 2026-08-24-patent-authorship-outcome.md:19 | https://www.inc.com/brian-contreras/this-new-grammarly-tool-aims-to-tell-if-ai-wrote-a-document |
| 2026-08-24-prd-agentscience.md:20 | https://venturebeat.com/ai/patronus-ai-launches-worlds-first-self-serve-api-to-stop-ai-hallucinations |
| 2026-08-24-verification-stack-positioning.md:8 | https://www.businesswire.com/news/home/20260803963850/en/Zenity-Raises-$125-Million-to-Secure-the-Era-of-1-Billion-AI-Agents |
| 2026-08-24-verification-stack-positioning.md:12 | https://www.businesswire.com/news/home/20260318888449/en |
| 2026-08-24-verification-stack-positioning.md:13 | https://stackshare.io/stackups/ai-agent-reputation-evaluation-vs-trust360 |
| 2026-08-24-verification-stack-positioning.md:21 | https://openreview.net/pdf?id=lN3yKqqzF1 |
| 2026-08-24-verification-stack-positioning.md:24 | https://www.sciencedirect.com/science/article/pii/S2949719124000141 |
| 2026-08-24-verification-stack-positioning.md:36 | https://www.businesswire.com/news/home/20260803963850/en/Zenity-Raises-$125-Million-to-Secure-the-Era-of-1-Billion-AI-Agents |
| 2026-08-24-verification-stack-positioning.md:40 | https://medium.com/@Indext_Data_Lab/ai-agent-audit-the-complete-2026-governance-and-compliance-guide-aa945b2d2f67 |

## Is the corpus clean enough to gate CI on?

**Not yet, and the gate condition matters.** Gating a red build on the script's raw `refused > 0` would fire on all 142 rows and **would flap**, because 9 of them are dead URLs whose reachability changes run to run (paywalls, rate limits, host outages) — a green-then-red build with no change to any claim. The CI-safe gate is `cause == source_does_not_state_it` only: that is stable across fetch weather and is a true statement about a document we read. On this run that gate stands at **133 real UNSOURCED**, so a red-build-if-UNSOURCED>0 rule would (correctly) fail the build today. The corpus is dogfood research notes, not a curated evidence base — 28/170 clearing verbatim is expected for finding-style notes whose cited page paraphrases or aggregates rather than quotes. To gate CI, the corpus first needs a pass that either tightens each finding to its source's verbatim span or re-points it at a page that carries it. Until then this receipt is the standing baseline: the product's own evidence gate, run over the product's own research, reported without laundering the number.

_Generated from the live run tee'd to `/tmp/verify-corpus-full.txt`. SOURCED held at 28 across the tee run and the row-dump run — no fetch-weather drift on this pass._
