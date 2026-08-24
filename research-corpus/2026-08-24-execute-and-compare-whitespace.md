# The execute-and-compare whitespace — no shipped context-linter RUNS documented commands

**Date:** 2026-08-24
**Question:** Is Helicon's "execute-and-compare" wedge (run the documented build/test command and grade its claimed outcome against the real exit code) actually uncontested, or has a competitor already shipped it?
**Answer (verified at the object 2026-08-24):** Uncontested. Every shipped context-file linter is STATIC — it checks that a referenced file/command *exists* or is *defined*, never that a documented command still *passes* when run.

## The competitors, and exactly where each one stops

| Tool | What it checks | Does it RUN the documented command? |
|---|---|---|
| **ctxlint** (YawLabs, `@ctxlint/ctxlint` on npm) | "catches stale file references, **dead build commands**, hardcoded secrets, token waste… Every rule runs against your actual codebase — it checks whether referenced files exist, **whether npm scripts are real**, whether your linter config already covers a style rule." | **No.** "npm scripts are real" = the script is *defined* in package.json (existence). It cross-references; it does not execute. |
| **AgentLint** (0xmariowu / agentlint.app) | "Lint your CLAUDE.md, AGENTS.md, and AI agent harness." Static linting of the harness files. | **No.** |
| **cclint** (carlrannaberg) | "Linter for Claude Code project files" — config quality + conventions + LSP. | **No.** |
| **cclint** (felixgeelhaar) | "validating and optimizing CLAUDE.md context files… follow best practices." Style/structure. | **No.** |

The strongest-sounding phrase in the whole field — ctxlint's **"dead build commands"** — is the closest anyone comes, and it is still *existence*: it flags a command whose npm script is not defined. It does not run `npm run build` and prove the build passes. That distinction is the wedge:

> **They check the command is DEFINED. Helicon runs it and proves the claim it PASSES is still true.**
> They lint the map; Helicon drives the road.

## Why the whitespace exists (and is defensible)

Running a stranger repo's documented command is a **safety surface**: it executes arbitrary repo code (conftest.py, the package.json script body, a Makefile recipe). That is precisely why the static linters stopped at name-resolution — it is the easy, safe tier. Helicon's moat is doing the hard, opt-in, allowlisted execution nobody else will:

- strict allowlist of test/build/lint verbs (pytest, npm test, npm run build|lint, make test, vitest, tsc, cargo/go test) — never install/deploy/publish/rm/curl/push;
- the resolved npm script *body* is denylist-scanned too (a `test` script that shells out to `curl … | sh` is refused, not run);
- opt-in per invocation (`HELICON_EXECUTE=1`), timeout, process-group kill, stdin closed, best-effort proxy denial.

The honest limit: the allowlist gates the *verb class*, but any test command runs repo code. No allowlist prevents that — opt-in is the mitigation. Competitors avoiding this is exactly the reason the lane is empty.

## Corroborating market signal (why the surface is worth owning)

- **75.9% of context files include test/build procedures** (arXiv:2511.12884, *Agent READMEs*, 2,303 files across 1,925 repos) — the single most common instruction type, and exactly the executable claim that rots silently.
- ETH Zurich / SRI Lab, ICSE 2026 (*Evaluating AGENTS.md*): LLM-generated context files cut task success 2–3% while raising cost >20%. A wrong context file is a net negative that hides — and a documented-but-failing test is the sharpest form of "wrong."
- One competitor's own launch post is titled *"I built a linter that proves 74% of your AGENTS.md is wasting your AI agent's time"* — demand for the tier below the wedge is already proven; nobody has climbed to execution.

## Sources

- ctxlint (YawLabs): https://github.com/YawLabs/ctxlint · https://www.npmjs.com/package/@ctxlint/ctxlint
- AgentLint (0xmariowu): https://github.com/0xmariowu/AgentLint · https://www.agentlint.app/
- cclint (carlrannaberg): https://github.com/carlrannaberg/cclint
- cclint (felixgeelhaar): https://github.com/felixgeelhaar/cclint
- "I built a linter that proves 74%…" (DEV): https://dev.to/vamshidhar_reddy_392c2302/i-built-a-linter-that-proves-74-of-your-agentsmd-is-wasting-your-ai-agents-time-46an
- arXiv:2511.12884 — Agent READMEs: https://arxiv.org/abs/2511.12884
- ETH Zurich / SRI Lab, ICSE 2026 — Evaluating AGENTS.md: https://www.sri.inf.ethz.ch/publications/gloaguen2026agentsmd

*Method: two web searches 2026-08-24 for shipped context-file linters that execute documented commands. Every hit was a static/existence-tier linter. No shipped tool runs the documented build/test and compares to a claimed outcome. Whitespace confirmed.*
