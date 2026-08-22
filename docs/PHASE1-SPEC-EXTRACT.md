---
date: 2026-08-22
project: CLEARED
event: Agentic Cinema — The Blockbuster Hackathon
phase: 1 (spec extract)
source: https://agentic-cinema.devpost.com/rules + /overview, fetched 2026-08-22
status: live
stale_when: organiser edits the rules page
---

# Phase 1 · SPEC EXTRACT — every literal constraint, quoted, as a checkbox

Rule: constraints are QUOTED from the organiser's page, never paraphrased from memory.
Anything not quoted below is NOT a known constraint.

## HARD DEADLINES (Pacific Time)
- [ ] Submission deadline: **"September 9, 2026, 2:00 PM PT"**
- [ ] Contest period opened: **"July 27, 2026, 9:00 AM PT"** — work must be created inside this window
- [ ] Judging: "September 23 - October 7, 2026"

## MANDATORY ARTIFACTS (a missing one = inadmissible, not "mostly done")
- [ ] "Hosted project URL" — functional, running on web, Android or iOS, testable by a judge
- [ ] "Demonstration video (max 3 minutes, English required, YouTube/Vimeo hosted)" — must be PUBLIC
- [ ] "Public GitHub/GitLab/Bitbucket repository" with **"complete open source license file"**
- [ ] OSI-approved licence "permitting commercial use"
- [ ] "Text description with features and learnings"
- [ ] Partner track selected on the Devpost form
- [ ] Completed Devpost submission form

## TECH CONSTRAINTS — the kill clause
- [ ] "Projects may only use Google Cloud artificial intelligence tools ... (with examples including
      Gemini models on Agent Platform, BigQuery ML, and relevant APIs)"
- [ ] **"No other AI models, agent frameworks, or AI APIs are permitted, regardless of vendor — this
      includes but is not limited to AWS, Microsoft, OpenAI, and Anthropic AI tools."**
- [ ] Framing: "a functional, production-ready AI agent or multi-agent network—powered by Gemini and
      Google Cloud Agent Builder"
- [ ] ClickHouse track requirement: **"ClickHouse MCP server connection"** — at runtime
- [ ] "integrate a Partner Entity's product or MCP to power a real media & entertainment workflow"

### Derived guards (NOT quotes — my rulings from the quotes above)
- [ ] No `anthropic` / `openai` package in the shipped repo, `.env.example`, README or fallback path
- [ ] Coding agents (Cursor, Claude Code) are BUILD tools, not project components.
      Evidence this is permitted: the IBM track *requires* IBM Bob and the Replit track *requires*
      Replit Agent — both AI coding agents. Organisers separate build tooling from project stack.
- [ ] Web enrichment uses **Gemini Grounding with Google Search**, NOT Parallel Search API
      (another partner's AI-adjacent API = avoidable risk on the exclusivity clause)

## ORIGINALITY
- [ ] "Projects must be newly created by the entrant during the Contest Period. The Project must be
      Your original creation not a modification or extension of Your or anyone else's existing work."
- [ ] → **Helicon cannot be vendored, extended, or renamed into this.** Nothing Oscar owns carries over.

## ELIGIBILITY
- [ ] "Teams of maximum 4 eligible individuals"
- [ ] 18+ ; Oscar's residence is not on the excluded list (Afghanistan, Belarus, China, Cuba, Iran,
      Iraq, North Korea, Russia, Syria, Venezuela, specific Ukraine regions)
- [ ] Not an employee/contractor of Google or a Partner entity

## JUDGING RUBRIC — verbatim, four criteria, EQUALLY weighted
- [ ] **"Technological Implementation"** — "effectiveness using Google Cloud and Partner services"
- [ ] **"Design"** — "complete, coherent product experience"
- [ ] **"Potential Impact"** — "credible solution addressing real problems"
- [ ] **"Quality of Idea"** — "creative application showing genuine understanding"

Read: the sponsor rewards DEPTH ON ITS OWN PRIMITIVE. Every extra call pattern against ClickHouse
MCP scores twice. A feature beside it scores once.

## PRIZES / FIELD
- [ ] 5 tracks x ($7,500 / $4,500 / $3,000) = 15 paying slots, "$75,000 in prizes"
- [ ] Registered participants at 2026-08-22: **7,415** (registration != submission)

## OPEN / UNVERIFIED
- [ ] Per-track submission counts — unknowable before the gallery opens. Track pick reasoned, not measured.
