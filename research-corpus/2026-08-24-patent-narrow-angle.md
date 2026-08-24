# Prior-art pressure-test: the NARROW composition-honesty patent claim

as_of: 2026-08-24 · deep prior-art search (Google Patents + arXiv + web, 8 probes) · for the ~$150 provisional decision
verdict_one_line: DOES-NOT-SURVIVE as a defensible provisional. Every element of the four-element combination is anticipated or rendered obvious by 2026 prior art; the only differentiator (apply arithmetic/set consistency to the agent's OWN natural-language self-report) is an obvious "known technique to known object" application under KSR.

## The claim under test (all four elements together)
Deterministic/LLM-free method that inspects an autonomous AI agent's OWN generated NL status/completion report, detects a claim that is compositionally false while every atomic figure is individually true (ratio whose denominator excludes failures named in the same report; headline count disagreeing with its own adjacent list length; success-% above named zero-of-a-good-thing items), and BLOCKS that report from entering a delivered/production/accepted state — a pre-production verification GATE on agent-authored text.

## Element-by-element prior art

### Element (a) agent-authored output + (b) deterministic/LLM-free + (d) block-from-production — NOT NOVEL. Two 2026 papers already do exactly this trio.
[CLOSEST-1] "Reason Less, Verify More: Deterministic Gates Recover a Silent Policy-Violation Failure Mode in Tool-Using LLM Agents" — deterministic, read-only, LLM-FREE pre-execution gates that inspect the agent's proposed action + current state and BLOCK writes that violate policy; airline-booking domain, +12pp success. Deterministic + agent + block trio, established.
[URL] https://arxiv.org/abs/2607.07405
[DIFF] Gates the AGENT'S ACTIONS / tool calls / state transitions — NOT the numeric/compositional content of the agent's natural-language self-report. Our claim differs only by the OBJECT inspected (NL report text vs proposed call).

[CLOSEST-2] "The LLM Proposes, the Executive Disposes: A Self-Verifying Agent Instrument" — deterministic LLM-FREE code admits a claim only when a prediction pre-registered before acting is matched against observation; runs auto-INVALIDATE (blocked from results) when write-error/token/canary floors breach. Deterministic + agent self-claim + block-from-delivered trio, established.
[URL] https://arxiv.org/html/2608.04066
[DIFF] Verifies PRE-REGISTERED PREDICTIONS vs environment observations — NOT the internal numeric consistency of a free-text report. Again differs only by object.

### Element (c) the specific composition shapes (count-vs-list, numeric verification, list-length) — NOT NOVEL as a class. Document-QA numeric/list consistency checking is well-trodden.
[CLAIM] Automated document QA already does pattern-based numeric verification: sample-size claims, prioritized-candidate counts, validation-test counts, method counts, FEATURE COUNTS, and figure-reference/list-length mismatch detection.
[URL] https://arxiv.org/pdf/2510.25402 (Automated QA of Patent Specifications — count mismatch + list-length verification)
[CLAIM] Internal-consistency checking of a document against its own entries is patented (coded-journal internal consistency).
[URL] https://patents.google.com/patent/US8572048B2/en
[CLAIM] Automatic configuration consistency check (deterministic self-consistency of a spec) — patented.
[URL] https://patents.google.com/patent/US9367373B2/en
[CLAIM] Entailment + contradiction detection between statements — patented (EP).
[URL] https://patents.google.com/patent/EP1852811A2/en
[DIFF] These check documents/configs, not an agent self-report; but the ARITHMETIC (count == len(list); denominator ⊇ named failures; %>0 vs 0-count item) is basic set/arithmetic logic a POSITA applies obviously once the object is chosen.

### The very CONCEPT ("treat every agent 'done' as a falsifiable claim a script verifies before trusting") is already PUBLIC.
[CLAIM] Patent-firm blog (2026): "AI agents report work as done that they never did, so every completion should be treated as a falsifiable claim that a script can verify before trusting it." Exact motivation, published.
[URL] https://bmdpat.com/blog/ai-agent-claims-done-verify-2026
[CLAIM] VLAA-GUI "Completion Gate" — a completion-verification gate that emits accept/reject on an agent's DONE claim before it is trusted (but LLM/MLLM-judge based, not deterministic).
[URL] https://arxiv.org/pdf/2604.21375
[DIFF] bmdpat says "a script can verify" — anticipates the deterministic-script framing at the concept level. VLAA-GUI's gate is LLM-based (our deterministic angle differs) but shows the gate-on-completion-claim architecture is known.

### Broad idea already dead (recap from prior file)
[CLAIM] "Aggregate misleads though parts true" = Simpson's paradox / aggregation bias — decades old.
[URL] https://www.statology.org/simpsons-paradox-when-aggregated-data-tells-a-different-story/
[CLAIM] Claim-decomposition + NLI atomic-claim verification is the standard hallucination-guardrail technique; guardrails already block/rewrite/route before delivery (Galileo Luna sub-200ms inline blocking, Patronus Lynx). No public Galileo/Patronus/Zenity PATENT surfaced on this exact mechanism.
[URL] https://www.braintrust.dev/articles/best-hallucination-detection-tools-2026

## Tightest surviving differentiator (marginal, not a slam dunk)
The ONE element not directly shown by any single reference: inspecting the agent's OWN natural-language self-report for SELF-REFERENTIAL compositional falsehood — i.e. detecting that a numeric claim contradicts the OTHER items ENUMERATED IN THE SAME REPORT (denominator excludes failures the report itself names; %>0 above an item the report itself scores zero), purely from the text, no ground truth, no LLM. "Same-document, self-referential, deterministic, on agent-authored text" is the narrowest non-anticipated slice.
[WHY IT STILL PROBABLY FAILS §103] Combining CLOSEST-1/2 (deterministic LLM-free agent gate that blocks) with document-QA numeric/set consistency (2510.25402, US8572048B2) yields this claim by routine substitution of the inspected object. KSR v. Teleflex: applying a known technique (numeric/set consistency) to a known object (agent self-report, whose falsifiability bmdpat already flags) to produce a predictable result is prima facie obvious.

## Decision inputs
[VERDICT] DOES-NOT-SURVIVE — not worth ~$150. A provisional parks a priority date but the eventual non-provisional would face a strong §103 rejection built from 2–3 references already in hand. A patent that issues then gets invalidated is worse than none (Oscar's own bar).
[IF-OSCAR-FILES-ANYWAY] Tightest one-sentence claim to try: "A computer-implemented method that, without invoking a language model, parses an autonomous agent's own natural-language completion report, and blocks the report from an accepted/production state when a numeric claim in it is contradicted by the report's OWN enumerated contents — specifically a ratio whose denominator omits a failure the same report names, a headline count unequal to the length of its own adjacent list, or a success percentage exceeding zero over an item the same report scores zero." Sell the self-referential-same-document + deterministic + agent-report triple, not the shapes.
[3 STRONGEST DISTINGUISHERS vs closest] (1) inspects the report's NL TEXT, not the agent's actions/tool-calls/pre-registered predictions (vs 2607.07405, 2608.04066); (2) SELF-referential — no external ground truth, no retrieval, no NLI model, no LLM judge (vs VLAA-GUI, Galileo/Patronus, RAG-NLI guardrails); (3) the contradiction is between a numeric claim and items ENUMERATED IN THE SAME REPORT (vs document-QA which checks against drafting rules / figures / external spec).
[STRATEGIC] Prior file's call stands: skip patent as the moat, write the paper (cheaper, half-done in the Kaggle Working Note), keep the authorship-to-outcome corpus as the real moat. If any filing: provisional BEFORE any publication (ex-US grace period is zero).
