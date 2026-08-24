# Research corpus — HELICON PRD cited facts (2026-08-24)

Two load-bearing facts behind the HELICON PRD (`~/CODE/mountain-of-helicon/PRD-2026-08.md`).
Both verified via web search 2026-08-24. Note the second fact's exact wording — the PRD
corrects a misquote that ships in `helicon/review.py`'s `_BASIS` footer.

## Fact 1 — context files are a measured net-negative when wrong

**Claim:** LLM-generated agent context files cut task success by 2–3% while raising cost >20%
(more agent steps). Developer-written files bought ~4% success at up to +19% cost.

**Source:** ETH Zurich, SRI Lab — Gloaguen et al., *"Evaluating AGENTS.md: Are
Repository-Level Context Files Helpful for Coding Agents?"*, ICSE 2026.
https://www.sri.inf.ethz.ch/publications/gloaguen2026agentsmd

**Why it matters for Helicon:** context is not free; a *wrong* context file is a net
negative that hides. That is the problem Helicon audits.

## Fact 2 — three-quarters of context files carry executable claims

**Claim (exact):** In an empirical study of 2,303 agent context files across 1,925 repos,
**75.9% of context files include test procedures** — the single most common instruction
type (ahead of implementation details 70.8%, architecture 68.1%). The paper frames these
files as evolving "like configuration code through frequent, small additions."

**Source:** arXiv:2511.12884 — *"Agent READMEs: An Empirical Study of Context Files for
Agentic Coding"* (Nov 2025). https://arxiv.org/abs/2511.12884

**Wording caution:** the paper says context files *include* test procedures. It does NOT
say "75.9% carry test procedures that rot." Helicon's `review.py` `_BASIS` line overstates
this; the PRD cites it correctly. The honest read is stronger for the wedge anyway: 3/4 of
these files carry executable claims that only execute-and-compare can verify are still true.

## Competitor grounding (existence tier is commoditized)

- ctxlint (YawLabs): npx + CI Action + MCP; catches stale file references AND dead build
  commands cross-referenced against the codebase. https://github.com/YawLabs/ctxlint
- cclint: config quality + conventions + LSP. https://github.com/carlrannaberg/cclint

These check a reference EXISTS. Helicon's defensible lane is to prove the claim is TRUE
(run the documented build/test and compare) — unbuilt as of 2026-08-24.
