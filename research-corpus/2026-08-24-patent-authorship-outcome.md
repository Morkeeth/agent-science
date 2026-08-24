# Patent Prior-Art Kill Test — "Authorship-to-Outcome Prompt Attribution"

Date: 2026-08-24. Adversarial prior-art search. Goal: KILL the candidate before Oscar files.
Format: each line = claim + source URL, tagged [ELEMENT-n]/[COMBO]/[VERDICT]. "unverified" where not directly fetched.

## The candidate (as stated)
A method that (1) deterministically separates genuine HUMAN operator turns from agent-generated turns in a
mixed AI-agent transcript corpus (gate on message provenance/metadata — promptSource typed/queued, not
tool-result/meta); (2) measures which human-authored prompts produced work that DURABLY LASTED (resulting
commit/artifact survived, not reverted/superseded over time); (3) ranks and auto-PROPAGATES the highest-outcome
human prompt into a team's shared instruction/skill file, unprompted. Novelty claim: attribute measured
downstream outcome-durability back to the specific originating human prompt, across an agent-workforce log.

---

## [ELEMENT-1] Human-vs-AI turn separation via deterministic provenance metadata

- Grammarly Authorship deterministically tags every chunk of text by ORIGIN at capture time — human keystroke, single paste, GrammarlyGO AI-accept, or third-party-AI paste — logging the writing PROCESS (keystroke/paste/AI-rephrase events), not statistical inference on the finished content. This is exactly "deterministic gate on provenance metadata, not stylometry." https://www.grammarly.com/authorship
- Grammarly Authorship launched 2024; produces a per-source share breakdown (share of text from each origin). https://www.inc.com/brian-contreras/this-new-grammarly-tool-aims-to-tell-if-ai-wrote-a-document
- GRANTED US patent US12462318 "Content editing software via automatic and auditable authorship attribution" — content can have human authors, artificial authors, or both, and separating them from content alone is hard; so attribution is recorded via provenance rather than inference. https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/12462318 (unverified full-claim read)
- US11042599B1 "Identifying relevant messages in a conversation graph" — message records carry an Author Account ID field identifying the author of each message; deterministic per-message authorship in a conversation log. https://patents.google.com/patent/US11042599B1/en
- ToolSandbox (arXiv 2408.04682) — LLM agent eval with explicit message roles User / Agent / Execution-Environment; every message carries a sender-role field. Gating on a role/provenance field to separate user turns from tool/agent turns is standard practice in agent frameworks. https://arxiv.org/pdf/2408.04682
- Linux kernel / Fedora "Assisted-by:" commit trailer — deterministic provenance marker separating human author (accountable) from AI assistance. https://zircote.com/blog/2026/07/recording-ai-authorship-in-provenance/
- Prior work on code provenance already distinguishes human-written from machine-generated code and does multi-class source attribution. https://arxiv.org/pdf/2603.04212 (Code Fingerprints)

VERDICT E1: ANTICIPATED. Deterministic provenance-metadata gating to separate human from AI authorship is shipped product (Grammarly) + granted patents + standard agent-framework role fields. No novelty in the separation step.

## [ELEMENT-2] Outcome / durability attribution (did the result SURVIVE)

- "Will It Survive? Deciphering the Fate of AI-Generated Code in Open Source" arXiv 2601.16809 — survival analysis over 201 repos, 200k+ code units; a line is "born" at merge and "dies" when git blame attributes it to a different commit SHA at a later timestamp; compares AI-agent vs human survival (hazard of modification, 15.8pp lower mod rate). This IS the durability measure attributed to authorship class. https://arxiv.org/abs/2601.16809
- GitHub Copilot production telemetry optimizes for "accepted and RETAINED characters" — how much of an AI suggestion stays in the final code over time vs. is deleted/modified shortly after; measured 88% of accepted chars retained in one deployment. Durability attribution of an AI-originated artifact, in production, at scale. https://github.blog/ai-and-ml/github-copilot/the-road-to-better-completions-building-a-faster-smarter-github-copilot-with-a-new-custom-model/
- Copilot telemetry records a tuple on every shown/accepted/rejected suggestion and feeds acceptance/retention back to improve the model — closed outcome-attribution loop from suggestion to downstream retention. https://www.erichorvitz.com/copilot_display_AAAI.pdf (When to Show a Suggestion, AAAI 2024)
- Code Revert Prediction with GNNs — J.P. Morgan Chase — forecasts probability a code change is rolled back; revert = the negative of durability, attributed to the change. https://arxiv.org/pdf/2403.09507
- Pre-Filtering Code Suggestions using Developer Behavioral Telemetry to Optimize LLM-Assisted Programming — arXiv 2511.18849. https://arxiv.org/pdf/2511.18849
- gitwhy — provenance for AI-written code, links code lines back to the originating agent prompt/session, 100% local. Ties surviving code to the prompt that produced it. https://github.com/mehrtam/gitwhy

VERDICT E2: ANTICIPATED. Code-survival-by-git-blame-SHA-change (Will It Survive), retention attribution of AI output (Copilot retained chars), and revert prediction (JPMC) all measure durability of an artifact and attribute it to its origin. No novelty in the durability step.

## [ELEMENT-3] Auto-propagation of the winning prompt into shared config

- US patent 7043435 "System and method for optimizing prompts for speech-enabled applications" — determines prompt alternatives, auto-presents during evaluation periods, auto-records results, analyzes by performance criteria, and AUTOMATICALLY IMPLEMENTS the winning alternative. This is measure-outcome-then-auto-propagate-the-winner, patented. https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/7043435 (unverified full-claim read)
- US survey-patent US10657549B2 — auto-updates heuristics from user-interaction data, changing prompt variation order for more effective review. https://patents.google.com/patent/US10657549B2/en
- PromptLayer Prompt Registry — every LLM call auto-versions into a shared registry; passive collection, no manual discipline. https://docs.promptlayer.com/features/prompt-registry/overview
- Braintrust / Databricks / MLflow prompt registries — run variant A vs B through one eval suite, compare, and PROMOTE THE WINNER through a review workflow into the shared prompt of record. https://www.braintrust.dev/articles/best-prompt-versioning-tools-2025 ; https://docs.databricks.com/aws/en/mlflow3/genai/prompt-version-mgmt/prompt-registry/
- DSPy / GEPA — optimize a prompt against a downstream task metric and write the optimized prompt back into the pipeline automatically. https://github.com/gepa-ai/gepa ; https://arxiv.org/abs/2507.03620
- "Computer-based interactive prompt variation generator" US12536208 — generating/selecting prompt variations. https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/12536208 (unverified)

VERDICT E3: ANTICIPATED. Measure prompt outcome then auto-promote the best into shared config is a granted patent (7043435) plus the entire prompt-registry/DSPy product category. No novelty in the propagation step.

## [COMBO] The pipeline: separation + durability + propagation together

- Each of the three steps is a known technique performing its known function: Grammarly (separation), Will-It-Survive/Copilot-retained-chars (durability of an origin-tagged artifact), 7043435/prompt-registries/DSPy (auto-promote the winning prompt). Arranging them in series is a predictable combination under KSR/§103.
- The one framing that is not literally shown in a single reference: attributing durability to the ORIGINATING HUMAN PROMPT (not the developer, not the model, not the commit) across a mixed agent-workforce log. BUT:
  - Copilot already attributes retention to an AI SUGGESTION; DSPy already attributes a downstream metric to a PROMPT; gitwhy already links surviving code back to the originating prompt/session. Choosing "human-authored prompt" as the attribution unit is an obvious substitution of one known unit (suggestion/commit/developer) for another (prompt) — analogous-art substitution, KSR "obvious to try" with a finite set of attribution units.
  - "Across an agent-workforce log" is just applying the same measurement to a larger corpus — no new function.
  - Auto-writing the winner "into a team's shared instruction/skill file" is the prompt-registry promote-the-winner workflow pointed at a CLAUDE.md/skill file instead of a registry row — same function, different sink.
- Closest 3 references for the COMBINATION rejection: (a) Will It Survive 2601.16809 [durability by SHA-change] + (b) Grammarly Authorship [deterministic provenance separation] + (c) US7043435 [auto-implement the outcome-winning prompt]. A single examiner motivation — "surface the input that produced the most durable output and reuse it" — spans all three.

## [VERDICT] DOES-NOT-SURVIVE

- Each of the three elements is independently anticipated by shipped product or granted patents.
- The combination is an obvious §103 arrangement of known elements, each performing its established function, with a single coherent motivation to combine. The only non-literal seam (attribute durability to the human prompt) is an obvious substitution of the attribution unit.
- Most-novel element (weak): outcome-durability attributed specifically to the originating HUMAN prompt across a mixed human/agent workforce log — thin, because Copilot retained-characters + gitwhy already tie durability to an AI-origin unit and DSPy ties a metric to a prompt.
- Tightest claim IF forced (still likely obvious): "A method comprising: gating a mixed human/agent transcript on a per-message provenance field to isolate human-authored prompt turns; for each isolated prompt, computing a durability score of its resulting version-controlled artifact via later-timestamp blame-SHA reassignment; and, upon the score exceeding a threshold, automatically writing the highest-scoring prompt into a shared agent instruction file." — reads onto Grammarly + Will-It-Survive + 7043435 in combination.

Recommendation to Oscar: do NOT file this. It is weaker than the composition-honesty angle that already died. If any patent value exists it is NOT in the pipeline as framed; a defensible angle would need a genuinely novel mechanism (e.g., a specific non-obvious causal-attribution technique isolating prompt contribution from confounds), which this candidate does not contain.
