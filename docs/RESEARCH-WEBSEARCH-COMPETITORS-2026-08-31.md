# Competitor & adjacent research: Agent Science “truth-layer websearch”

**Only Agent Science:** finds the latest truths across the agentic stack *and* shows how it searched (angles, imbalance, stack-fit) — not one verified badge.

**Date:** 2026-08-31  
**Scope:** Primary sources only (product pages, GitHub, first-party docs/blogs). Secondary comparisons used only as discovery pointers, never as facts.  
**Lens:** Agent Science websearch = *believe + use → verify verbatim or refuse → remember → multi-pane visibility*; personal truth DB; not raw Google; not one summarized answer.  
**Internal frame:** `docs/WEBSEARCH-FULL-RUNDOWN.md`, `docs/TRUTH-LAYER-SOURCES.md`.

### Confidence legend

| Tag | Meaning |
|-----|---------|
| **HIGH** | Claim taken from the company/product’s own page or docs in this pass |
| **MED** | First-party page partially fetched, or product state changed (rebrand/removal) |
| **LOW** | Primary page blocked, timed out, or identity ambiguous — treat as pointer only |

---

## Executive map (where the field sits vs Agent Science)

| Layer | What the field optimizes | Agent Science gap vs them |
|-------|--------------------------|---------------------------|
| Answer engines | One cited summary, speed, chat follow-ups | Structural refuse + multi-pane + remember |
| Agent search APIs | Fresh snippets / crawl / agent grounding | Verbatim verify gate; ★ as *use* not truth |
| Memory products | Persist prefs / graphs / agent state | Sourced claims + retract + refuse |
| Claim/verify | Markup, explorer, claim DBs, domain agents | Composition: search → verify → shelf |
| Deep research | Long multi-step reports | Free/cheap/live tiers; peer-query flywheel |
| Dev docs search | Version-true library docs / repo Q&A | Field-wide agentic *practices* truth, not just APIs |
| Personal index | Private RAG over *your* files | Shared fleet dictionary + visibility panes |

No product in this survey ships the full stack: **use signal ≠ truth**, **verbatim-or-refuse**, **remember as free tier**, **multi-pane UI**, and **personal/fleet truth DB** together.

---

## 1 · Answer engines

### Perplexity

| | |
|--|--|
| **What** | AI answer engine: real-time web search → distilled conversational answer with numbered source citations. Pro Search / Research modes for deeper multi-source / multi-step work. |
| **Optimizes** | Speed-to-answer, citations as footnotes, research reports |
| **Angle to steal** | Citations as *first-class UI*, not afterthought — but invert: show **span verify / refuse** as pane 1, not a prose summary. Steal the *habit* of always showing sources; reject the *habit* of one answer. |
| **Primary URL** | https://www.perplexity.ai/help-center/en/articles/10352895-how-does-perplexity-work |
| **Confidence** | HIGH (help center); API citation details MED (mostly third-party guides in this pass) |

### You.com

| | |
|--|--|
| **What** | Positions as web search / contents / answer / research APIs for agents and LLMs — “real-time web data layer for AI.” Consumer chat history exists; current homepage is API-forward. |
| **Optimizes** | Accuracy, freshness, latency for agents; enterprise (ZDR, SOC 2) |
| **Angle to steal** | Explicit **API surface for agents** (search vs contents vs answer vs research). Agent Science can expose the same *jobs* but with verify/refuse receipts instead of synthesized answers. |
| **Primary URL** | https://you.com/ |
| **Confidence** | HIGH |

### Brave Search / Ask Brave / Leo

| | |
|--|--|
| **What** | **Brave Search:** independent index + AI Answers / **Ask Brave** (search+chat, Deep Research mode, enrichments). **Leo:** in-browser assistant (summarize tabs, BYOM, privacy); can use Brave Search for fresher answers. Separate products. |
| **Optimizes** | Privacy, grounded answers on own index, optional AI (not forced) |
| **Angle to steal** | “When you need them” philosophy — AI optional. Deep Research with **transparent research steps**. Leo admits hallucinations and tells users to double-check. Steal **honesty about failure** and **optional synthesis**; own **structural refuse** instead of “double-check yourself.” |
| **Primary URLs** | https://brave.com/blog/ask-brave/ · https://brave.com/leo/ · https://brave.com/search/api/ |
| **Confidence** | HIGH |

### Phind

| | |
|--|--|
| **What** | Developer-oriented AI search / agent product (historically code-focused answers). |
| **Optimizes** | Dev Q&A (historically) |
| **Angle to steal** | Vertical answer engines win by **domain** (code). Agent Science vertical = **agentic practices / believe+use**, not general web. |
| **Primary URL** | https://www.phind.com/ |
| **Confidence** | LOW — Cloudflare bot wall blocked first-party content in this pass |

### Arc / Dia (The Browser Company)

| | |
|--|--|
| **What** | **Dia:** AI-first browser; URL bar as chat+search; synthesizes across tabs and connected tools (Slack, Notion, Calendar, GSuite); Morning Brief; profiles/context splits; memory toggle. Arc is prior product / maintenance-era (secondary coverage); Dia is current primary. |
| **Optimizes** | Personal context across *browser life*, synthesis you’ll act on |
| **Angle to steal** | Multi-context synthesis UI (“between the tabs”) without pretending to be a truth DB. Steal **visibility of work context**; own **verified claim shelf** that survives tab close. |
| **Primary URL** | https://www.diabrowser.com/ |
| **Confidence** | HIGH for Dia product page; Arc history MED (press) |

---

## 2 · Agent / search infrastructure

### Parallel.ai

| | |
|--|--|
| **What** | Web infra for agents: Search, Extract, Task (deep research), FindAll, Monitor, Responses. Proprietary web index. **Basis** framework: provenance, citations, calibrated confidence, reasoning traces. Claims “pay for answers, not tokens.” |
| **Optimizes** | Agent grounding accuracy, confidence scoring, production auditability |
| **Angle to steal** | **Confidence + provenance as API contract** (Basis). Agent Science can treat Parallel as *discovery* (already in live tier) while owning the **verify-or-refuse** gate and personal shelf. Steal **monitor** idea for field-signal refresh, not for answer generation. |
| **Primary URL** | https://www.parallel.ai/ · docs: https://docs.parallel.ai/api-reference/search/search |
| **Confidence** | HIGH |

### Exa.ai

| | |
|--|--|
| **What** | Semantic / neural web search for agents; Search, Contents, Agent, Monitors, Websets, MCP. Emphasizes latency tiers (Instant), verticals (company/people/code), token-efficient highlights. |
| **Optimizes** | Semantic discovery, latency, coding-agent docs/repos |
| **Angle to steal** | **Semantic “find similar / find the page an LLM would want”** as discovery. Keep Exa (or Parallel) *below* the truth layer — never let semantic similarity author SOURCED. |
| **Primary URL** | https://exa.ai/ · https://exa.ai/docs/reference/search |
| **Confidence** | HIGH |

### Tavily

| | |
|--|--|
| **What** | “Connect AI agents to the web” — Search / Extract / Crawl / Research API; LLM-ready chunks; security filters (PII, injection). Heavy agent/RAG positioning. |
| **Optimizes** | Agent-ready snippets, latency, production safeguards |
| **Angle to steal** | Chunks-for-LLM as input to **verify**, not as the answer. Steal **content validation / malicious-source** posture for ingest hygiene. |
| **Primary URL** | https://tavily.com/ · https://docs.tavily.com/documentation/api-reference/endpoint/search |
| **Confidence** | HIGH |

### Linkup

| | |
|--|--|
| **What** | Web Search API for AI: Fetch / Search / Research; private index and BYOC deployment modes; enterprise / regulated buyers. |
| **Optimizes** | Accuracy + enterprise deployment control |
| **Angle to steal** | **Private index** as a product mode — Agent Science’s personal/fleet truth DB is the *claim* analog of Linkup’s private web index. |
| **Primary URL** | https://www.linkup.so/ |
| **Confidence** | HIGH |

### Firecrawl

| | |
|--|--|
| **What** | Context API: Search, Scrape, Crawl, Map, Interact — turn messy web into LLM-ready markdown/JSON. Open-source + hosted. Developer Index for coding agents. |
| **Optimizes** | Extraction reliability, token efficiency, agent tooling |
| **Angle to steal** | Clean fetch is a **prerequisite for verbatim span verify**. Steal agent-onboarding (`SKILL.md`) distribution pattern for Magnet / MCP skills. |
| **Primary URL** | https://www.firecrawl.dev/ |
| **Confidence** | HIGH (product claims; do not treat marketing star counts as audited) |

### Serper

| | |
|--|--|
| **What** | Fast/cheap Google SERP API (organic, news, scholar, etc.) — raw Google results as JSON. |
| **Optimizes** | Price, latency, Google parity |
| **Angle to steal** | Nothing philosophically — this is **raw Google**. Use as reminder of the anti-pattern Agent Science rejects. If used, only as discovery behind verify. |
| **Primary URL** | https://serper.dev/ |
| **Confidence** | HIGH |

### Bing Grounding (Microsoft Foundry / Azure)

| | |
|--|--|
| **What** | Grounding with Bing Search / Custom Search tools for Foundry agents — real-time public web into model responses with citations; also Web Search tool variants. Admin can disable grounding for compliance. |
| **Optimizes** | Enterprise agent grounding inside Azure stack |
| **Angle to steal** | **Admin kill-switch for web** and explicit compliance boundary messaging. Agent Science analog: **refuse causes** and tier visibility as governance, not just UX. |
| **Primary URL** | https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/bing-tools |
| **Confidence** | HIGH |

---

## 3 · Memory / personal knowledge

### Mem0

| | |
|--|--|
| **What** | Drop-in memory layer for agents/apps: add conversations → extract memories → search. User/session/agent levels. Managed + OSS. |
| **Optimizes** | Persistent personalization, lower token cost, easy integration |
| **Angle to steal** | **Ask once, reuse** ergonomics — but memories are preferences/facts without structural provenance. Steal the API simplicity; require **source + verify** before shelf. |
| **Primary URL** | https://mem0.ai/ · https://github.com/mem0ai/mem0 · https://docs.mem0.ai |
| **Confidence** | HIGH |

### Zep

| | |
|--|--|
| **What** | Enterprise agent memory as temporal **context graphs**: entities, facts with validity windows, provenance to episodes, Observations (patterns), Context Lake, ABAC/retention/audit. |
| **Optimizes** | Time-aware facts, governance, sub-200ms retrieval at scale |
| **Angle to steal** | **Fact succession + validity intervals** and **provenance to source episode**. Closest memory product to “knowledge that changes.” Steal temporal contradiction handling; still add **verbatim refuse** for web claims. |
| **Primary URL** | https://www.getzep.com/ |
| **Confidence** | HIGH |

### Letta (MemGPT lineage)

| | |
|--|--|
| **What** | Research lab + product: agents that manage their own memory (MemGPT OS metaphor → Letta Agent / Letta Code). Context constitution, git-based context repos, sleep-time compute. |
| **Optimizes** | Long-running self-improving agents, agent-owned memory tiers |
| **Angle to steal** | Memory as **agent-operated**, not just a sidecar DB. Magnet skill-as-truth rhymes with “agent edits its own constitution.” Steal **versioned context** idea for truth dictionary commits. |
| **Primary URL** | https://www.letta.com/ · MemGPT paper era via Letta research links |
| **Confidence** | HIGH for product positioning |

### Rewind

| | |
|--|--|
| **What** | Domain `rewind.ai` currently markets an **AI tools aggregator / multi-model chat API**, not the classic “record your screen / personal computer memory” product. |
| **Optimizes** | (Current site) multi-tool access, free tier |
| **Angle to steal** | None from current site for truth-layer. Historical Rewind angle (life-log retrieval) is **adjacent** to personal truth but **not citable from this primary** without older first-party archives. |
| **Primary URL** | https://www.rewind.ai/ |
| **Confidence** | MED — product identity appears shifted; do not cite old Rewind features from memory |

### Notion AI

| | |
|--|--|
| **What** | Agents, Custom Agents, Enterprise Search across connected apps, AI Meeting Notes, Research Mode, verified pages for citations. Workspace as knowledge plane. |
| **Optimizes** | Team knowledge + automation where work already lives |
| **Angle to steal** | **“Verify any page”** badge for trusted sources in search/AI citations. Steal **verified source marking**; own claim-level verify/refuse. |
| **Primary URL** | https://www.notion.com/product/ai |
| **Confidence** | HIGH |

### Cursor Memories (public status)

| | |
|--|--|
| **What** | Cursor forum staff stated **Memories were removed** (from ~2.1.17); users directed to export memories into **Rules**. Persistence now = Rules / Skills / AGENTS.md, not a Memories product. |
| **Optimizes** | (Successor) durable prompt-level guidance |
| **Angle to steal** | Market proof that **unstructured auto-memory is fragile**; durable truth wants **explicit rules + sourced dictionary**. Magnet skill-as-truth aligns with Skills; Agent Science owns **verified claims** those skills consult. |
| **Primary URLs** | https://forum.cursor.com/t/memories-not-showing/143820 · https://cursor.com/docs/rules.md · https://cursor.com/help/customization/skills |
| **Confidence** | HIGH for removal note (staff reply); product docs for Rules/Skills HIGH |

---

## 4 · Claim / verify

### AttestDB (omic/attest)

| | |
|--|--|
| **What** | Claim-native database: statements with source, timestamp, confidence; contradiction coexistence; retraction cascades; time-aware queries; local-first Rust engine; MCP tools. Positions as “truth layer for AI agents.” |
| **Optimizes** | Provenance, retraction, uncertainty as storage primitives |
| **Angle to steal** | Closest **storage philosophy** cousin. Differentiate: Agent Science is **websearch UX + believe/use panes + fleet shelf + structural refuse at answer time**, not only a claim DB. Partner/interop angle: shelf backend could resemble Attest primitives. |
| **Primary URLs** | https://attestdb.com/developers/ · https://github.com/omic/attest · https://attestdb.com/ |
| **Confidence** | HIGH |

### ClaimReview (Schema.org)

| | |
|--|--|
| **What** | Schema.org type for fact-check review markup (claim reviewed, rating, URL). Industry standard for publisher fact checks. |
| **Optimizes** | Interoperable fact-check metadata on the open web |
| **Angle to steal** | Publish Agent Science **refuse/SOURCED receipts** in a ClaimReview-*compatible* or parallel schema for crawlability — popularity flywheel via structured data. |
| **Primary URL** | https://schema.org/ClaimReview |
| **Confidence** | HIGH |

### Google Fact Check Tools

| | |
|--|--|
| **What** | ClaimReview Read/Write API (authorized publishers via Search Console) + Claim Search API (query fact checks / Fact Check Explorer corpus). |
| **Optimizes** | Publisher markup + discovery of existing fact checks |
| **Angle to steal** | **Search existing claim reviews** as a cheap tier before live web — but Agent Science domain is agentic *engineering* truth, not news fact-check. Use as pattern for **claim search API**, not content. |
| **Primary URL** | https://developers.google.com/fact-check/tools/api |
| **Confidence** | HIGH |

### PeriodCheck (ahsan3274/periodcheck) — Cinema track

| | |
|--|--|
| **What** | Evidence-first historical accuracy agent for screenplays: Document AI anchors → Gemini claim extract → Parallel Search research → line-level verdicts (supported / anachronistic / uncertain / not verifiable) with citations. Hackathon/Parallel partner track. |
| **Optimizes** | Domain-specific claim extract + grounded verdicts + line anchors |
| **Angle to steal** | **Explicit verdict vocabulary including “not verifiable”** (refuse cousin). Line/page anchors = span discipline. Vertical demo path for Agent Science (Cinema) without diluting core agentic-truth wedge. |
| **Primary URLs** | https://github.com/ahsan3274/periodcheck · https://devpost.com/software/period-check |
| **Confidence** | HIGH for GitHub/Devpost |

---

## 5 · Agentic research

### OpenAI Deep Research

| | |
|--|--|
| **What** | ChatGPT agentic multi-step web research → analyst-grade cited reports (minutes). API: `o3-deep-research` / `o4-mini-deep-research` via Responses API; web search, MCP, file search, code interpreter. Updates: trusted-site restrict, MCP apps, progress interrupt. |
| **Optimizes** | Depth, citations, autonomous browsing |
| **Angle to steal** | Sidebar of **steps + sources** while running. Steal **progress visibility**; replace final “report” with **claim rows that verify or refuse**, shelved for free re-ask. |
| **Primary URLs** | https://openai.com/index/introducing-deep-research/ · https://developers.openai.com/api/docs/guides/deep-research |
| **Confidence** | HIGH |

### Gemini Deep Research

| | |
|--|--|
| **What** | Gemini Advanced agentic research: multi-step plan (user approves) → iterative browse → comprehensive report with links; export to Docs. |
| **Optimizes** | Supervised plan + thorough web synthesis |
| **Angle to steal** | **User-approved research plan** before spend — maps to Agent Science live-tier consent / optimize pane. |
| **Primary URL** | https://blog.google/products/gemini/google-gemini-deep-research/ |
| **Confidence** | HIGH (Dec 2024 announce; product may have evolved — verify in-product) |

### Anthropic / Claude Research

| | |
|--|--|
| **What** | Claude Research: agentic multi-search across web + Google Workspace; citations; Docs cataloging for Enterprise retrieval quality. |
| **Optimizes** | Work-context + web research with checkable citations |
| **Angle to steal** | **Internal + web** in one research pass. Agent Science analog: dictionary + field blogs + live web panes — already multi-source; steal **Workspace-style personal corpus** as personal truth DB ingest. |
| **Primary URL** | https://www.anthropic.com/news/research (canonical post also at https://claude.com/blog/research) |
| **Confidence** | HIGH |

### LangChain Open Deep Research

| | |
|--|--|
| **What** | Open-source deep research agent repo (`langchain-ai/open_deep_research`) — compose your own research loops. |
| **Optimizes** | Hackable agentic research architecture |
| **Angle to steal** | Open loop as **competition for builders**; Agent Science differentiates by **dictionary + refuse correctness**, not by being another research graph. |
| **Primary URL** | https://github.com/langchain-ai/open_deep_research |
| **Confidence** | HIGH for existence; README fetch was empty in this pass — feature details MED |

---

## 6 · Developer truth / docs search

### Context7 (Upstash)

| | |
|--|--|
| **What** | Up-to-date, version-specific library documentation and code examples injected into coding agents (MCP / CLI skills). Pulls from source repos; fights stale training data. |
| **Optimizes** | Correct *library* API truth for coding agents |
| **Angle to steal** | **Version-pinned primary docs as context**. Agent Science for *practices/tools believe+use*; Context7 for *API surface*. Interop: Context7 for code APIs, Agent Science for “what the field runs / refuses to invent.” |
| **Primary URLs** | https://context7.com/about · https://github.com/upstash/context7 · https://upstash.com/blog/context7-llmtxt-cursor |
| **Confidence** | HIGH |

### Sourcegraph Cody

| | |
|--|--|
| **What** | AI coding assistant grounded in Sourcegraph Search across local/remote codebases; chat, edits, prompts, context filters. Enterprise-oriented. |
| **Optimizes** | Codebase-grounded answers at org scale |
| **Angle to steal** | **Search API as truth substrate** for code. Agent Science is not Cody — keep wedge on *agentic field truth*, optionally cite Cody pattern for “answers must be grounded in an index.” |
| **Primary URL** | https://about.sourcegraph.com/cody |
| **Confidence** | HIGH |

### Continue.dev

| | |
|--|--|
| **What** | Open coding assistant; `@` context providers; MCP for external tools/docs; custom code RAG guides. Docs/web providers deprecated toward MCP. |
| **Optimizes** | Configurable local agent context |
| **Angle to steal** | Distribution: Agent Science as **MCP context provider** (`science_visibility`) — Continue’s model of pluggable truth sources. |
| **Primary URL** | https://docs.continue.dev/customize/deep-dives/custom-providers |
| **Confidence** | HIGH |

### Devin (Ask Devin / DeepWiki)

| | |
|--|--|
| **What** | Index repos → Ask Devin (cited codebase Q&A + planning) → handoff to Agent sessions; DeepWiki auto docs. |
| **Optimizes** | Repo-grounded Q&A → execution |
| **Angle to steal** | **Index → ask with citations → act**. Agent Science stops at **verified shelf** (and may refuse); Devin continues to code. Clear product boundary. |
| **Primary URL** | https://docs.devin.ai/work-with-devin/ask-devin · https://docs.devin.ai/onboard-devin/index-repo |
| **Confidence** | HIGH |

---

## 7 · Personal search index / second brain / private search

| Product | What | Optimizes | Angle | Primary URL | Conf. |
|---------|------|-----------|-------|-------------|-------|
| **AnythingLLM** | Local/self-hosted RAG + agents over your docs | Private ownership, on-device | Personal corpus ingest → still need verify for *web* claims | https://anythingllm.com/ · https://github.com/mintplex-labs/anything-llm | HIGH |
| **Onyx** (ex-Danswer) | Enterprise search/chat over company apps (40+ connectors), ACL-aware | Org knowledge + permissions | Permissioned private index; Agent Science fleet dictionary is cross-agent not cross-SaaS | https://onyx.app/ · https://github.com/onyx-dot-app/onyx | HIGH |
| **Linkup Private Index** | Dedicated private web/data index in their stack | Regulated retrieval | Same as §2 — private index productizing | https://www.linkup.so/ | HIGH |
| **Notion Enterprise Search** | Search workspace + connected apps | Team answerability | Personal/team plane, not verify gate | https://www.notion.com/product/ai | HIGH |
| **Dia browser context** | Answers from tabs + connected tools | Life/work synthesis | Ephemeral context ≠ durable verified shelf | https://www.diabrowser.com/ | HIGH |
| **Mem0 / Zep / Letta** | See §3 | Memory not search index | Memory ≠ indexed second brain | (see §3) | HIGH |
| **Self-hosted “memex” projects** | Various GitHub “personal AI brain / hybrid search” experiments | Local MCP knowledge | Pattern validation for personal index; not a single category leader | e.g. discovery via GitHub search — **LOW** as category | LOW |

**Gap the field leaves open:** private RAG answers from *your files*; almost none do **structural refuse + use-signal panes + shared fleet popularity** for *agentic web truth*.

---

## Differentiation angles Agent Science can own

(Field is weak or contradictory here — not feature checklist.)

1. **Structural refuse as product** — First-class `NOT_CLEARED` / cause codes, not “maybe check sources.” Brave/Leo tell users to double-check; PeriodCheck has “not verifiable”; almost no consumer answer engine *refuses by design*.

2. **Believe ≠ use ≠ true** — Explicit panes: practitioner/docs belief, GitHub ★ adoption, verified span. Stars never author SOURCED (`TRUTH-LAYER-SOURCES.md`). Field collapses these into one answer.

3. **Popularity / peer-query flywheel** — Fleet asks and refusal_log make the next ask free and teach the system what’s expensive. Deep research products burn tokens every time; memory products remember *preferences*, not *shared verified claims*.

4. **Personal + fleet truth DB** — AttestDB-class claims + Mem0-class persistence, but shelved only after verify. Not chat memory; not unmarked RAG chunks.

5. **Multi-pane visibility (not one summary)** — Parallel Basis / OpenAI deep research show steps; Agent Science shows **primary + aliases + ★ + blogs + peers + probes + optimize**. Done = all panes considered.

6. **Magnet / skill-as-truth** — Cursor Skills + Context7 skills distribute *how to fetch*; Agent Science distributes *what was verified*. Skill points at dictionary, not at another summarizer.

7. **Cost tiers as honesty** — free → cheap → live (`WEBSEARCH-FULL-RUNDOWN.md`). Competitors hide spend inside “unlimited chat” or per-token research. Showing tier is a trust feature.

8. **Vertical wedge without losing the layer** — PeriodCheck proves cinema claim-verify; Clearance proves rights/E&O; Companion proves agentic practices — same engine. Answer engines stay horizontal mush.

---

## Competitive posture (one paragraph)

Build **on** Parallel/Exa/Tavily/Firecrawl for discovery and fetch; **do not** compete as another answer engine (Perplexity/Brave Ask) or another memory API (Mem0/Zep). The scarce product is the **truth gate + shelf + multi-signal visibility**. Closest conceptual cousins: **AttestDB** (claim storage), **PeriodCheck** (verdict vocabulary), **Parallel Basis** (confidence/provenance), **Context7** (version-true docs for a vertical). None own the Agent Science composition end-to-end.

---

## Honesty / limits of this pass

- Phind primary content blocked (Cloudflare).  
- Perplexity help article sometimes timed out; claims prefer the help-center URL when available.  
- Rewind.ai no longer presents classic life-log memory — do not cite historical Rewind features from this URL.  
- Vendor benchmark tables (Parallel, Exa, Tavily, Brave) are **self-reported** — useful for positioning, not for claiming who “wins.”  
- Star counts and funding figures **not inventoried here** unless needed; where vendors display stars on pages, treat as marketing until `gh api` audited.  
- Gemini Deep Research primary post is Dec 2024; confirm current Gemini UI naming before external marketing claims.  
- LangChain Open Deep Research README body did not load in fetch — cite repo existence only unless re-fetched.

---

## Sources

### Answer engines
- https://www.perplexity.ai/help-center/en/articles/10352895-how-does-perplexity-work  
- https://you.com/  
- https://brave.com/blog/ask-brave/  
- https://brave.com/leo/  
- https://brave.com/search/api/  
- https://www.phind.com/  
- https://www.diabrowser.com/  

### Agent / search infra
- https://www.parallel.ai/  
- https://docs.parallel.ai/api-reference/search/search  
- https://exa.ai/  
- https://exa.ai/docs/reference/search  
- https://tavily.com/  
- https://docs.tavily.com/documentation/api-reference/endpoint/search  
- https://www.linkup.so/  
- https://www.firecrawl.dev/  
- https://serper.dev/  
- https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/bing-tools  

### Memory / knowledge
- https://mem0.ai/  
- https://github.com/mem0ai/mem0  
- https://www.getzep.com/  
- https://www.letta.com/  
- https://www.rewind.ai/  
- https://www.notion.com/product/ai  
- https://forum.cursor.com/t/memories-not-showing/143820  
- https://cursor.com/docs/rules.md  
- https://cursor.com/help/customization/skills  

### Claim / verify
- https://attestdb.com/developers/  
- https://github.com/omic/attest  
- https://schema.org/ClaimReview  
- https://developers.google.com/fact-check/tools/api  
- https://github.com/ahsan3274/periodcheck  
- https://devpost.com/software/period-check  

### Agentic research
- https://openai.com/index/introducing-deep-research/  
- https://developers.openai.com/api/docs/guides/deep-research  
- https://blog.google/products/gemini/google-gemini-deep-research/  
- https://www.anthropic.com/news/research  
- https://claude.com/blog/research  
- https://github.com/langchain-ai/open_deep_research  

### Developer truth
- https://context7.com/about  
- https://github.com/upstash/context7  
- https://upstash.com/blog/context7-llmtxt-cursor  
- https://about.sourcegraph.com/cody  
- https://docs.continue.dev/customize/deep-dives/custom-providers  
- https://docs.devin.ai/work-with-devin/ask-devin  
- https://docs.devin.ai/onboard-devin/index-repo  

### Personal / private index
- https://anythingllm.com/  
- https://github.com/mintplex-labs/anything-llm  
- https://onyx.app/  
- https://github.com/onyx-dot-app/onyx  

### Internal Agent Science frame
- `docs/WEBSEARCH-FULL-RUNDOWN.md`  
- `docs/TRUTH-LAYER-SOURCES.md`  
