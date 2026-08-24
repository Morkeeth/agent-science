# Patent-Angle Generation — 8 candidates from the fleet's technical methods

as_of: 2026-08-24 · divergent generation + adversarial prior-art search (WebSearch ×10, WebFetch ×2)
Format: each line = claim + source URL, tagged [ELEMENT]/[PRIOR-ART]/[DIFF]/[VERDICT]. "unverified" = not fetched full-text.
Scope note: two angles are pre-killed and NOT re-proposed — composition-honesty (true parts / false whole = Simpson's Paradox; killed by bmdpat blog + arXiv 2607.07405 / 2608.04066, see 2026-08-24-patent-narrow-angle.md) and the authorship→outcome pipeline (DOES-NOT-SURVIVE, see 2026-08-24-patent-authorship-outcome.md).

## Object-level verification of the numbers the task handed me
- [MEASURED] confident-set precision claim VERIFIED at object: `python3 ~/CODE/hack-fleet-ata/contract/test_confidence.py` → 5/5 PASS, incl. `test_confident_answers_are_never_wrong` and `test_every_floor_error_is_deferred_not_asserted` (run 2026-08-24). Source: repo test, not a doc claim.
- [SOURCE] 95.1% agent-authored / 537 real prompts / 10,866 records: PITCH.md line 58-61, `~/CODE/hack-fleet-ata/PITCH.md` — Oscar's own corpus, single-machine, NOT externally reproduced. Treat as internal-unverified.

## DISCLOSURE STATUS (bears on DEFENSIBLE — public disclosure is prior art against Oscar himself)
- [DISCLOSURE] hack-fleet-ata, cleared (agent-science), agent-attack, helicon (mount-helicon) all have PUBLIC GitHub remotes (`git remote -v`, 2026-08-24). Several were hackathon submissions.
- [RULE] EPO/most-of-world: any public disclosure before filing = novelty DEAD (absolute novelty). US: 12-month grace window from first inventor disclosure (35 USC §102(b)(1)). So every angle below is at best US-filable with a clock already running from the repo's first public commit. https://www.uspto.gov/web/offices/pac/mpep/s2153.html (unverified — standard grace-period rule)

---

## ANGLE 1 — Structural-deferral cascade (deterministic predicate marks the provably-sole-undecidable region)
Method: a rule-based classifier computes object-token sets + intent bucket for two NL inputs; it answers deterministically in every case EXCEPT the single cell {objects disjoint AND intents compatible} (the synonym-suspect zone), which it defers to an LLM — so deferral is triggered by a closed-form structural predicate, not a tuned confidence score, and the non-deferred "confident" set is empirically error-free.
Most-novel element: the deferral region is a NAMED, closed-form lexical-structural cell that is provably the model's only undecidable region — no probability threshold, no calibration set.
- [ELEMENT] source: `~/CODE/hack-fleet-ata/contract/deterministic.py::classify_with_confidence` — confident unless disjoint-objects ∧ compatible-intents; `classify_cascade` escalates only that tail.
- [PRIOR-ART] FrugalGPT and the cascade literature defer on a CONFIDENCE SCORE below a learned threshold. https://arxiv.org/html/2506.11887 (Cascaded LLMs for cost-effective decisions)
- [PRIOR-ART] UCCI — calibrated uncertainty for cost-optimal LLM cascade routing; deferral by calibrated uncertainty threshold. https://arxiv.org/html/2605.18796
- [PRIOR-ART] Learning-to-Defer generalizes selective prediction: abstain/defer on uncertain inputs to an expert. https://arxiv.org/pdf/2502.01459 (Learning to Partially Defer for Sequences)
- [PRIOR-ART] repo cites the escalate-the-low-confidence-tail result itself (arXiv:2502.09054) — self-disclosed art.
- [DIFF] All prior art defers on a SCORE (learned/calibrated threshold). This method defers on a deterministic structural predicate that is closed-form and needs no calibration; the confident set is provably error-free on the test set (test_confidence.py 5/5). I found NO patent/paper framing deferral as "escalate exactly the one lexically-undecidable cell, threshold-free."
- [VERDICT] NOVEL (marginal). Obviousness risk is real — "defer when the deterministic rule cannot decide" reads as an obvious species of selective prediction. But the specific mechanism (structural predicate = provably-sole undecidable region → threshold-free confident set) is not literally shown anywhere I found. STRONGEST candidate.

## ANGLE 2 — Independence-refusal verdict taxonomy (refuse to round a derived source up to primary)
Method: for a factual claim, classify each supporting source as primary / derived-or-mirror / unclassified by structural signals; and emit a THREE-WAY verdict that treats "documents state it but every one traces to a single derived/unclassified origin" as a DISTINCT non-cleared verdict from "no source at all" — refusing to clear rather than producing a weighted consensus score.
Most-novel element: independence failure is a REFUSAL (a distinct verdict a human must resolve), not a down-weight into a blended score.
- [ELEMENT] source: `~/CODE/cleared/clearance/independence.py` + `agent_science.py` LABEL/WHY maps — `no_independent_source` ("documents state this, every one derived") is a separate verdict from `no_source_offered`.
- [PRIOR-ART] Automated fact-checking already rates source independence High/Med/Low (bibliometric/citation-graph overlap) and DOWN-WEIGHTS low-independence sources into a consensus score. https://arxiv.org/abs/2404.18971 (Credible, Unreliable or Leaked? Evidence Verification)
- [PRIOR-ART] Circular reporting / citogenesis is a named, well-mapped problem; dedup mirrored sources when counting independent evidence. https://en.wikipedia.org/wiki/Circular_reporting
- [PRIOR-ART] Source credibility scoring patented (score ∝ how often a source agrees with others). https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/10331682 (Secondary profiles with credibility scores, unverified)
- [PRIOR-ART] NewsGuard: 0-100 trust score per domain on nine criteria — a graded score, not a refusal. https://newsguardtech.com (rating methodology, unverified)
- [DIFF] The field DOWN-WEIGHTS (a score); this REFUSES and prints the open question, and distinguishes derived-origin from no-origin as two facts. That is an output-policy distinction over a well-trodden mechanism.
- [VERDICT] MARGINAL → leans OBVIOUS. The structural classification is anticipated; "refuse instead of down-weight" is a policy choice a POSITA makes, not a novel mechanism.

## ANGLE 3 — Verbatim witnessed prompt propagation (no LLM rewrite)
Method: rank operator prompts within a task class by fewest corrective follow-up turns, then propagate the LITERAL winning text into the shared instruction file with an on-disk/Firestore witness hash — no model rewrite.
Most-novel element: verbatim copy + cryptographic witness, explicitly no optimization/rewrite step.
- [ELEMENT] source: `~/CODE/hack-fleet-ata/fleet/propagate.py`, `fleet/org_proof.py`, README ("propagate the literal text ... No LLM rewrite").
- [PRIOR-ART] DSPy / GEPA optimize a prompt against a downstream metric and write the OPTIMIZED (rewritten) prompt back automatically. https://arxiv.org/abs/2507.03620 (GEPA)
- [PRIOR-ART] Prompt registries (PromptLayer/Braintrust/MLflow) version prompts and promote-the-winner through review. (see 2026-08-24-patent-authorship-outcome.md E3)
- [PRIOR-ART] Selecting the best prompt by fewest user re-phrasings = rephrase-as-dissatisfaction, already patented as an implicit-quality signal. https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/9633674 (detect repeated input as dissatisfaction, unverified)
- [DIFF] Verbatim-not-rewrite + witness hash distinguishes from DSPy (rewrites) and registries (manual promote). Thin: "copy the best instead of rewriting it" is a design choice; witness-hashing an artifact is standard provenance.
- [VERDICT] OBVIOUS. The selection metric is anticipated (rephrase-dissatisfaction), the promote-winner is anticipated (registries), verbatim-vs-rewrite is a substitution. Task hinted this as the narrow system; the pipeline is already killed in the sibling file, and the surviving sliver is a design choice, not a mechanism.

## ANGLE 4 — Execute-and-compare setup verification gate (run the documented command, block on a false repo claim)
Method: parse setup/build/test commands and factual claims from an instruction/README file, EXECUTE them against the repo, and block acceptance when the observed result contradicts the documented claim.
Most-novel element: (attempted) block-from-accepted-state on a proven-false documented claim, not just report drift.
- [ELEMENT] source: helicon `helicon/commands.py`, `helicon/pointers.py` (static now); planned EXECUTE-and-compare in ROADMAP.
- [PRIOR-ART] EnConda-Bench INJECTS realistic README errors and evaluates agents localizing + repairing them in Docker — the exact "false documented instruction, detect by executing" loop. https://arxiv.org/abs/2510.25694
- [PRIOR-ART] SetupAgent/EnvBench/SetupX: read README, execute installation+test commands in a clean env, verify correctness by test results. https://arxiv.org/html/2503.14443 (EnvBench)
- [PRIOR-ART] doctest / Sphinx doctest / pytest --doctest: executable documentation — run the documented example, compare to expected output. https://docs.python.org/3/library/doctest.html
- [PRIOR-ART] US8607193B2 tracking stale comments in source; US20170308379A1 evaluating documentation coverage; US9086944 sync code↔docs. https://patents.google.com/patent/US8607193B2/en
- [PRIOR-ART] ctxlint validates command names statically vs package.json but never executes. https://github.com/YawLabs/ctxlint
- [DIFF] "Block from accepted state" is the only unclaimed framing, but doctest already fails a build on a mismatch and EnConda-Bench already does inject→execute→detect.
- [VERDICT] DEAD. Executable-documentation (doctest, 20+ yrs) + EnConda-Bench + SetupAgent fully anticipate execute-and-compare. The gate/block is doctest-in-CI.

## ANGLE 5 — Authorship provenance-gate + fleet-echo separation (per-harness schema)
Method: deterministically gate a mixed human/agent transcript on per-record provenance fields to isolate genuine human turns; measure that ~95% of `type:user` records are agent-injected at fleet scale; note the schema differs per harness.
- [PRIOR-ART] Grammarly Authorship tags every text chunk by origin via process metadata, not stylometry — shipped 2024. https://www.grammarly.com/authorship
- [PRIOR-ART] US12462318 "Content editing software via automatic and auditable authorship attribution" (granted). https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/12462318 (unverified)
- [VERDICT] DEAD. Fully analyzed and killed in 2026-08-24-patent-authorship-outcome.md (VERDICT E1 ANTICIPATED). The 95% number is a measurement/finding, not a patentable mechanism.

## ANGLE 6 — Composition-honesty (true parts, false whole)
- [VERDICT] DEAD — pre-killed by task. See 2026-08-24-patent-narrow-angle.md (DOES-NOT-SURVIVE) and 2607.07405 / 2608.04066. Not re-proposed.

## ANGLE 7 — Reachability positional-impossibility proof (agent-attack)
Method: given a guardrail decide(tool,args,context), enumerate predicates and prove which are provably unreachable under any taint window K≥2 — a combinatorial impossibility, not a heuristic to evade.
- [ELEMENT] source: `~/CODE/agent-attack/jed/reachability.py`, WRITEUP.md §3.
- [PRIOR-ART] AWS Zelkova translates IAM policies to SMT and proves properties over ALL possible requests, incl. proving a formula CANNOT be satisfied (unreachable). https://www.amazon.science/blog/custom-policy-checks-help-democratize-automated-reasoning
- [PRIOR-ART] "Beyond Red-Teaming: Formal Guarantees of LLM Guardrail Classifiers" — formal reachability/coverage over guardrail input regions. https://arxiv.org/abs/2605.10901
- [VERDICT] DEAD as a patent. It is a benchmark FINDING about one guardrail, and formal reachability/policy-property proving is exactly Zelkova's established method. Not patentable subject matter as framed.

## ANGLE 8 — Corrective-turns as prompt-quality signal
Method: count human re-statements of the same intent after a prompt as a negative quality signal.
- [PRIOR-ART] US9633674 detects the same input repeated within a short window as dissatisfaction. https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/9633674 (unverified)
- [PRIOR-ART] US11289096 / US11830499 "Providing answers to voice queries using user feedback" — negative feedback = rephrase. https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/11289096 (unverified)
- [PRIOR-ART] Amazon "Contextual Rephrase Detection for Reducing Friction in Dialogue Systems." https://aclanthology.org/2021.emnlp-main.143.pdf
- [VERDICT] DEAD/OBVIOUS. Rephrase-as-dissatisfaction is a granted-patent + established-research signal.

---

## RANKED SHORTLIST (defensible-first)
1. ANGLE 1 structural-deferral cascade — **NOVEL (marginal)** — closest: FrugalGPT/UCCI/L2D (all defer on a score, not a structural cell). https://arxiv.org/html/2605.18796
2. ANGLE 2 independence-refusal taxonomy — **MARGINAL→OBVIOUS** — closest: arXiv 2404.18971 (down-weight, don't refuse) + citogenesis.
3. ANGLE 3 verbatim witnessed propagation — **OBVIOUS** — closest: GEPA 2507.03620 + prompt registries + rephrase-dissatisfaction.
4. ANGLE 4 execute-and-compare gate — **DEAD** — closest: EnConda-Bench 2510.25694 + doctest.
5. ANGLE 5 authorship gate — **DEAD** — Grammarly Authorship + US12462318 (see sibling file).
6. ANGLE 6 composition-honesty — **DEAD** (pre-killed).
7. ANGLE 7 reachability proof — **DEAD** — Zelkova.
8. ANGLE 8 corrective-turns — **DEAD** — US9633674.

## SINGLE MOST-PROMISING (honest: only MARGINAL)
ANGLE 1. Tightest one-sentence claim:
"A computer-implemented cost-bounded classification method comprising: deriving, from each of two natural-language inputs, a set of object tokens and a discrete intent bucket; returning a deterministic class label whenever either input has no placeable object, or the object-token sets overlap, or the object-token sets are disjoint AND the intent buckets are incompatible; and, ONLY in the remaining case where the object-token sets are disjoint AND the intent buckets are compatible, deferring the input pair to a language model — whereby every model call corresponds to a closed-form, lexically-undecidable synonym-ambiguity region rather than a calibrated confidence threshold, and the non-deferred label set is produced without any tuned score."

Why only marginal: it is a plausible non-obvious species of selective prediction/learning-to-defer, but a §103 examiner can characterize "defer when the deterministic rule provably cannot decide" as an obvious variant of confidence-based deferral. Its one real edge over every reference found — threshold-free deferral keyed to a provably-sole undecidable cell, with an empirically error-free confident set — is narrow, and US-only with the grace clock already running from the public repo. No angle here is clearly, comfortably novel; ANGLE 1 is the only one worth an attorney's hour, and only as a narrow method claim.
