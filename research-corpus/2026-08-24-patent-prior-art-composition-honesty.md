# Prior-art search: is "composition-honesty detection" patentable?

as_of: 2026-08-24 · inline websearch (coordinator) · for the patent decision

[CLAIM] The general idea "every atomic number is true but the aggregate/composition misleads" is DECADES-OLD prior art — it is Simpson's Paradox + aggregation bias.
[URL] https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7175433/ (Simpson's paradox, misleading aggregated vs subgroup)
[URL] https://www.statology.org/simpsons-paradox-when-aggregated-data-tells-a-different-story/
[CLAIM] USPTO already has patents on misleading-aggregate / distribution estimation from source data.
[URL] https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/8180717
[URL] https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/8959047 (false-positive reduction in data validation via statistical heuristics)
[CLAIM] AI-agent consistency-checking is an active 2026 research area (U-statistics, self-consistency, semantic entropy) — prior art against a broad "verify agent output consistency" claim.
[URL] https://arxiv.org/html/2605.10516v1 (Consistency as a Testable Property)
[URL] https://arxiv.org/html/2602.16666v1 (Towards a Science of AI Agent Reliability)
[VERDICT] Broad patent = dead on arrival (Simpson's paradox). NARROW claim MAY survive: deterministic detection of the SPECIFIC shapes (denominator-excludes-its-failures, count-vs-its-list, percent-vs-contradicting-rows) in an AGENT'S OWN natural-language report, used as a pre-production gate. Needs a patent attorney's novelty read; not a slam dunk.
[DECISION] Skip patent as the moat; write the paper instead (cheaper, half-done via the Kaggle Working Note). Real moat = the authorship-to-outcome corpus (which prompt produced lasting work), which is harder to copy. If patenting anyway: file provisional BEFORE any publication (ex-US grace period is zero).
[PROVENANCE] Nothing published yet — the composition method lives in PRIVATE repos (agent-claims-inbox, hack-fleet-ata), so patentability/novelty is preserved either way.
