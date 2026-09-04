# Agentic science field pass — 2026-09-05

Queries were run through Agent Science: four local visibility queries, then six live Parallel searches across memory, retrieval, agent UX and coordination. Follow-up source reads included primary HTML papers and a PDF. The underlying cases, snapshots and full revision histories are saved in the default private local case store. This file records research leads and authored interpretations, not universal recommendations.

## Memory

Claim assessed: LLM-generated repository context files reliably improve coding-agent task success.
[CLAIM] Ultimately, we conclude that unnecessary requirements from context files make tasks harder, and human-written context files should describe only minimal requirements.
[URL] https://arxiv.org/html/2602.11988v1

Assessment: contradicts. This evaluation challenges automatic context-file expansion on the studied coding tasks. It is heavily Python-focused and measures task resolution, not every benefit of persistent memory. Proposed local test: compare no project context, a concise human-authored file and generated context on the same pinned tasks; measure completion and cost.

Local case: `c5d4051a667f`; claim: `790ab2dfcd89`.

## Retrieval

Claim assessed: Repository retrieval needs task-aware evaluation; no single retrieval family wins uniformly in Agent Retrieval Bench.
[CLAIM] The results show that agentic retrieval is not solved by a single retrieval family.
[URL] https://arxiv.org/html/2607.24882

Assessment: supports. The paper compares lexical, repository-structure and embedding retrieval on different file-finding tasks. File retrieval and exact span localization are separate outcomes. Proposed local test: compare lexical/path search, embeddings and a hybrid on frozen questions from the same repository; score necessary-file recall, irrelevant context and token cost.

Local case: `5b54d783ec1f`; claim: `b654c6f9b56f`.

## Ux

Claim assessed: Early adopters report that opaque multi-agent loops and error propagation hinder collaboration.
[CLAIM] We conducted semi-structured interviews with 13 developers, all early adopters of multi-agent Gen AI technology who work at Microsoft .
[URL] https://arxiv.org/html/2510.06224v1

Assessment: supports. This is an interview study with 13 developers at Microsoft, not a controlled comparison of UI designs. It supports an observed user problem. Proposed local test: compare raw activity logs with progress, current intent and intervention controls; measure correct intervention and recovery effort.

Local case: `7be7dab537cd`; claim: `1fb30a5d2ca6`.

## Coordination

Claim assessed: Multiple agents inherently outperform a single agent on multi-hop reasoning under matched thinking-token budgets.
[CLAIM] We find that SAS consistently match or outperform MAS on multi-hop reasoning tasks when reasoning tokens are held constant.
[URL] https://arxiv.org/html/2604.02460v1

Assessment: contradicts. The result concerns multi-hop reasoning across the tested model families, not repository coding or all forms of collaboration. Thinking-token budgets exclude prompts and final answers. Proposed local test: compare one agent with delegated roles under both equal total cost and equal wall time, using pinned coding tasks and independently checked outcomes.

Local case: `6f9c8e80b194`; claim: `2cee8ab5e617`.

## What this changes in the product

The research surface must carry study task, population, budget definition and limitations beside the conclusion. A reasoning benchmark does not settle coding-fleet design; a context-file study does not settle all persistent-memory architectures; qualitative interviews do not establish a causal UX improvement. Returned search snippets are leads. Follow through to primary methods and limitations before assessing a claim.

Next local experiments are proposals only. No coding-agent performance, retrieval lift, UX improvement or fleet superiority was measured in this pass.

## Memory counterpoint: context curation

[CLAIM] ACE prevents collapse with structured, incremental updates that preserve detailed knowledge and scale with long-context models.
[URL] https://arxiv.org/html/2510.04618v1

The ACE paper proposes incremental curation and evaluates different settings from the AGENTS.md paper. It does not refute that paper on the same tasks. Compare update policy and useful content locally; do not turn the evidence into a blanket instruction to shorten or expand all context. Added to the same memory case.
