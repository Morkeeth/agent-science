# Prompt-quality signals — what makes a prompt "survive" (facts corpus)

*Captured 2026-08-24 for Transcripto's prompting-coach (PRD-2026-08 §6 Slice 1). Web-cited.
This grounds the coach's ranking claim: it does not invent "good prompt" categories — the
patterns it ranks (states-a-check, cites-a-file, detailed vs terse, intent) are the ones the
2026 literature independently names as the drivers of first-try success.*

## The one that matters: an explicit done-condition

2026 best practice, stated repeatedly across independent sources: **define what "done" looks
like inside the prompt.**

- "Success criteria means defining what 'done' looks like and how you will judge it … Asking
  the model to 'analyze,' 'improve,' or 'optimize' without defining success criteria leads to
  inconsistent and subjective outputs." (Claude / Anthropic; ARTJOKER 2026)
- "Prompts should end with a verifiable check (a passing test, a clean build, a diff) so the
  agent closes its own loop." (Inflectra, *Prompt Engineering for AI Agents: 2026 Guide*)

→ This is exactly the coach's top-ranked pattern on Oscar's real logs:
`states-a-check-or-done-condition` = **65% survival (64/99)**, the single highest of any tag.
The measured signal and the literature agree.

## Specificity + a named object beat vagueness

- "Success rate drops dramatically if the prompt is missing key information … output quality
  is improved by using specific prompts, decomposing problems into steps." (arXiv 2603.16348,
  *Prompts Blend Requirements and Solutions*)
- "Instructions like 'be helpful' are too vague for production agents; specify 'do not take
  account actions without verified identifiers.'" (Inflectra 2026)

→ Matches the coach's bottom tier: `intent:none` (39%) and `terse (<8 words)` (42%) are the
lowest-survival patterns in Oscar's corpus. Vague/short = loops.

## Context assembly, not prompt cleverness, is the real failure mode

- "Most agent failures aren't model failures anymore — they're context failures … bad context
  assembly." (musketeerstech 2026)
- "Teams winning with workflow agents in 2026 … treat prompts as versioned, tested, budgeted
  production artifacts" and prefer prompt **chaining** over one mega-prompt. (Claude blog 2026)

→ Supports the coach's premise: the best prompt for a codebase already exists in someone's
own history; surfacing and reusing it (propagation) beats re-deriving prompt tricks.

## Verification is the 2026 bottleneck (why the survival PROXY is the honest frame)

- "The quality of verification signals should be characterized along three dimensions:
  scalability, faithfulness, and robustness." (arXiv 2606.26300, *The Verification Horizon*)
- NeurIPS 2026 ran a *Who Verifies the Agents?* workshop — verifying agent work is an open
  problem, not a solved one.

→ Why the coach labels "survived" a **proxy, not truth**: transcript-derived durability
(un-reverted commit / Write-Edit) is a *faithfulness*-limited signal. Honest to rank on, not
to certify with.

## Sources

- [Prompt Engineering for AI Agents: 2026 Guide — Inflectra](https://www.inflectra.com/Ideas/Topic/AI-Agent-Prompt-Engineering.aspx)
- [Prompt engineering best practices for 2026 — Claude by Anthropic](https://claude.com/blog/best-practices-for-prompt-engineering)
- [AI Prompt Engineering Best Practices 2026 — ARTJOKER](https://artjoker.net/blog/ai-prompt-engineering-best-practices/)
- [Prompt Engineering Best Practices for AI Agents (2026) — musketeerstech](https://musketeerstech.com/blogs/prompt-engineering-best-practices/)
- [Prompts Blend Requirements and Solutions — arXiv 2603.16348](https://arxiv.org/html/2603.16348v1)
- [The Verification Horizon: No Silver Bullet for Coding Agent Rewards — arXiv 2606.26300](https://arxiv.org/abs/2606.26300)
- [Who Verifies the Agents? — NeurIPS 2026 Workshop](https://verify-agents-workshop.github.io/)
