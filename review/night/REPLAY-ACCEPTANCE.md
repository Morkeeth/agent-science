# Saved-source acceptance, 2026-09-05

The coordinator froze 18 questions before implementation: 12 development questions and six held-out questions. Three fresh agent contexts received the held-out questions and saved public source snapshots, without the expected distinctions or other agents’ answers. Each used the real stdio MCP server to read sources and submit proposals. Full transcripts and databases remain outside Git; `replay-acceptance.json` contains transcript hashes and counts derived from the actual JSON-RPC responses.

Observed: **207 tool calls; 18 completed initial runs; three completed challenges; zero MCP error responses**. These are workflow counts, not evidence-quality scores. There were 128 separate source drill-down calls. Host reasoning and these calls are outside the engine’s usage counters. Total tokens, latency per scientific question and billing were not measured. No configured-model or fresh discovery call was made.

## What the saved evidence supports, with limits

- **Memory/context:** a universal benefit from longer retained context was not established. The [ACE limitations](https://arxiv.org/html/2510.04618v1) distinguish tasks and context usefulness; the [repository context study](https://arxiv.org/html/2602.11988v1) changes instruction content and requirements. These are not isolated retention-length interventions. Challenge one changed the same claim from contradicted-as-assessed to unresolved, preserving the previous assessment and explaining the narrower causal question. Needed experiment: vary retained length while holding content policy, tasks and resource allowance fixed.
- **Retrieval:** [the retrieval study](https://arxiv.org/html/2607.24882) distinguishes file exposure from localization within the file. Finding a file alone does not establish that the useful span reached the agent. Needed experiment: score both file exposure and exact evidence localization on the same frozen tasks and context budgets, then measure downstream acceptance separately.
- **Coding:** [the context study](https://arxiv.org/html/2602.11988v1) measures selected test outcomes; supplied evidence does not establish correctness on unseen behavior. This topic reused an existing paper rather than recovering new coding evidence. Needed experiment: freeze an independent hidden behavioral test set before generating patches and evaluate public-test-passing patches against it.
- **UX/design:** [the interview study](https://arxiv.org/html/2510.06224v1) supports descriptions of collaboration problems and preferences. It does not establish that an intervention interface causes better task success. Needed experiment: assign interface conditions on fixed tasks, measure task acceptance and intervention burden, and retain participant differences.
- **Coordination:** [the reasoning-budget study](https://arxiv.org/html/2604.02460v1) constrains intermediate reasoning tokens. That does not establish equal end-to-end cost; prompts, final outputs, tools and actual consumption need separate measurement. Its task scope cannot become a repository-coding verdict. Needed experiment: compare delegation and single-agent work on identical tasks under a common total resource allowance.
- **Evaluation:** [the retrieval study](https://arxiv.org/html/2607.24882) does not establish lower human rework or even a general patch-success effect. This topic reused retrieval evidence and has a named missing external outcome. Needed experiment: measure independent reviewer acceptance and rework time on matched repository changes, alongside benchmark scores.

These are coordinator summaries of authored replay conclusions, not freshly verified scientific recommendations. Source hashes and exact quotations reside in the private cases. All three rounds retained the essential distinctions above, but their claim wording and relationship labels differed. A supported negative assertion and a contradicted positive assertion are not necessarily disagreement. No semantic agreement percentage is reported. Original figures, PDFs and underlying experiments were not independently replicated.

## Baseline and variation

The exact baseline `e12ca6f7c4ad489b8e20bb16c307470635b0883d` ran 18 local retrieval requests against a frozen case-store copy. Outputs and source snapshots were preserved outside Git. Candidate MCP synthesis is a different operation from baseline retrieval, so these outputs do **not** establish a matched-budget research-quality improvement. Six fresh-web questions, their repeated runs, live adapter behavior and billing remain unmeasured.

## Errors found and changes made

- A repository-scoped start initially missed general research and could stop at a page full of other repositories. It now retrieves general and matching-repository work across ranked pages.
- MCP host work was absent from engine counters without a clear enough warning. Usage now explicitly states these exclusions.
- Source drill-down references lost an explicit alternate database. References now retain it.
- Context-only/different-scope answers could expose no gap. Synthesis now names unresolved relationship/applicability gaps and unassessed sources.
- CLI could not attach a new question to an existing case. `research start --case-id` now exposes the same path as MCP.
- Broken SQLite paths could print a traceback. CLI now returns a clean error and status 2.

These fixes were exercised with actual entry points and failure controls. The original transcripts remain unchanged and predate the fixes.
