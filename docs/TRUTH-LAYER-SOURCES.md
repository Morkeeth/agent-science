# Truth layer sources — more than research

**Ruling:** Agent Science is the truth layer for what people **believe** and **use**.  
Research papers are one input. Blogs, official docs, and GitHub adoption are others.

## Signal types

| Signal | Answers | Example | Not |
|--------|---------|---------|-----|
| **Research** | Peer / preprint claim | arXiv 2512.14012 | Enough alone for “used in building” |
| **Practitioner blog** | What a named builder documents as belief/practice | Willison, Huntley, Osmani, Anthropic eng | A citation wall if never verified |
| **Official product docs** | What the tool vendor says you should do | code.claude.com best practices | Marketing as proof of field use |
| **GitHub stars / push** | What the field **installs and watches** (use proxy) | `anthropics/claude-code` 143k★ | Stars ≠ correctness — adoption signal only |
| **Fleet / popular queries** | What *our* agents ask | `science_popular` | Thin until habit exists |
| **Clearance / regulatory** | E&O / law / rights truths | 2012/28/EU, CNE | Vertical on the same layer |

Stars and “latest blog” feed **believe + use**. Verify still decides SOURCED vs refuse. A star count never authors a verdict.

## Field snapshot (stars read 2026-08-31 via `gh api`)

| Repo | ★ | Last push (UTC) | Why it matters |
|------|--:|-----------------|----------------|
| Significant-Gravitas/AutoGPT | 187035 | 2026-08-31 | Long-running agent loop adoption |
| anthropics/claude-code | 143565 | 2026-08-28 | Dominant coding-agent surface |
| hesreallyhim/awesome-claude-code | 53287 | 2026-08-31 | Curated “what people use” index |
| Aider-AI/aider | 48628 | 2026-05-22 | Pair-programming agent, high use |
| cursor/cursor | 33202 | 2026-05-12 | Editor+agent product signal |
| frankbria/ralph-claude-code | 9612 | 2026-07-18 | Ralph loop — used in building |
| mikeyobrien/ralph-orchestrator | 3118 | 2026-08-29 | Ralph orchestration — active |

Machine file: `truth-dictionary/field-signals.json` · refresh: `python3 scripts/refresh_field_signals.py` · HN: `python3 scripts/refresh_hn_signals.py`

### Hacker News (honest ingest)

| Source | Status | Refresh |
|--------|--------|---------|
| HN Algolia API | Live when network allows | `scripts/refresh_hn_signals.py` writes `hacker_news.source=hn_algolia_api` |
| HN snapshot | Fallback when API blocked | `source=snapshot` — **do not claim live** |

### ARKIVX (snapshot only)

| Source | Status | Note |
|--------|--------|------|
| ARKIVX | **Not wired** | Static snapshot in `field-signals.json` · `arkivx.source=snapshot` |

## Latest blogs / docs (seed, not exhaustive)

| Source | URL | Kind |
|--------|-----|------|
| Anthropic — Claude Code best practices | https://code.claude.com/docs/en/best-practices | official docs |
| Anthropic — context engineering | https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents | eng blog |
| Willison — agentic engineering patterns | https://simonwillison.net/2026/Feb/23/agentic-engineering-patterns | practitioner |
| Huntley / Ralph coverage | https://linearb.io/blog/ralph-loop-agentic-engineering-geoffrey-huntley | practitioner |
| Ball — how to build an agent | https://ampcode.com/how-to-build-an-agent | practitioner |
| Osmani — self-improving agents | https://addyosmani.com/blog/self-improving-agents | practitioner |
| Loop engineering (Claude Code) | https://genaiunplugged.substack.com/p/loop-engineering-claude-code | latest blog |
| Traversaal — agentic loops guide | https://blog.traversaal.ai/claude-code-agentic-loops-developer-guide-loop-engineering/ | latest blog |
| ShipWithAI — loop guardrails | https://shipwithai.io/blog/loop-guardrails-unattended/ | latest blog |

Claim seeds: `research-inbox/2026-08-31-field-blogs.md` · Grinder corpus: `docs/inspiration/PRACTICES-CORPUS.md`

## Discipline

1. **Import widely** — research + blogs + docs + star signals.  
2. **Verify narrowly** — verbatim span or refuse; stars never greenlight a claim.  
3. **Rank by use** — stars + `science_popular` + push recency for “what the field runs.”  
4. **Keep clearance on the layer** — EU/E&O are truths here too, not a separate product.

## Next build (when Oscar says go)

- [x] Transparency panes in `visibility --full` (angles / shallow / imbalance)
- [x] HN refresh script (`refresh_hn_signals.py`) — live or snapshot
- [ ] Auto-refresh stars on a schedule into `field-signals.json`
- [ ] `/popular/ui` strip: top field repos ★ beside top queries
- [ ] Ingest pipeline: blog RSS / awesome-list → claim candidates → verify
- [ ] Gemini locate pass on practitioner seeds (first ingest was all UNSOURCED)
