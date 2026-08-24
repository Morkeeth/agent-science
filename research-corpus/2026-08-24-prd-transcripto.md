# TRANSCRIPTO / hack-fleet-ata — PRD grounding facts (2026-08-24)

Facts gathered at the object for `~/CODE/hack-fleet-ata/PRD-2026-08.md`. Every claim
here is either a file+line citation, a command output, or a web-cited source. No claim
is repeated from another doc without naming that doc as the author.

## What the code actually does (verified by running it)

- **`contract/gate.py` — `verify_report(text, *, prompt_pair=None)`** is the single call.
  Two axes in one product:
  - COMPOSITION (`find_adjacency`) — BLOCKS the report if it lies by composition. Gated.
  - TASK/AUTHORSHIP (`classify_with_confidence`) — OPTIONAL, only when a prompt pair is
    passed; REPORTED, not gated (a task-class judgement is not a production-safety verdict).
- **`contract/adjacency.py` catches FOUR shapes** (task brief said 3; object says 4,
  fourth added commit 5bb88ed):
  1. DENOMINATOR-EXCLUDES-ITS-FAILURES (the "96% that's 50%")
  2. COUNT-DISAGREES-WITH-ITS-LIST
  3. PARTS-DO-NOT-SUM
  4. PERCENT-CONTRADICTED-BELOW
- **Adjacency is measured on real corpus, and is mostly noise — this is the honest state:**
  - COUNT-DISAGREES-WITH-ITS-LIST: ran over ~4,775 real agent reports. Before the
    plural-noun fix: 131 findings at ~8% precision. After: 34 findings at ~21% precision
    (adjacency.py:194-244, in-code comments).
  - PARTS-DO-NOT-SUM: 2 documented false positives on the real corpus (adjacency.py:258-262).
  - The other two shapes' real-corpus precision is UNMEASURED. So the honest gap is:
    "measured and mostly noise" for two shapes, "lexical and unmeasured on real corpus"
    for the other two. NOT a blanket "unmeasured."
- **The Twist demo fires** (verified by running, not asserted):
  ```
  $ printf '22 of 23 projects have a phase on disk\n21 no repo · 1 unknown\n' | python3 -m contract.gate
  [BLOCK] 1 composition finding(s) [DENOMINATOR-EXCLUDES-ITS-FAILURES] ...
  EXIT=1
  ```

## The cascade (patent ANGLE 1) — honest numbers

- `contract/deterministic.py` `classify_with_confidence` returns `(verdict, confident)`.
  Confident in 3 of 4 structural cells; DEFERS to the LLM only on the ONE provably-unique
  cell: disjoint objects + compatible intents (the synonym-suspect tail, "fix auth" vs
  "repair authentication").
- **The three numbers that together are the honest claim** (never 13/13 alone):
  - PRECISION on kept set: 13/13 correct (PROVISIONAL-SPEC-ANGLE1.md:242) — the confident
    set is never wrong on the frozen 24-item corpus.
  - COVERAGE: 13 of 24 pairs decided deterministically (~54%); the rest deferred.
  - HELD-OUT LIFT (ran `contract/prove_lift.py` today): deterministic 5/8 vs 3/8 no-signal
    baseline on a clean held-out set it never saw (in-sample 6/8). The two misses (T2, T8)
    are the zero-lexical-overlap SAME rows — the LLM's earned slot.
- `contract/` test suite: **17 passed** (`python3 -m pytest contract/ -q`).
- Cascade cost basis: cascades cut LLM spend up to ~90% by escalating only the
  low-confidence tail (arXiv:2502.09054, cited in deterministic.py:214).

## The authorship moat — THREE distinct numbers, each with its own provenance (DO NOT BLEND)

| Number | Meaning | Scope / provenance |
|---|---|---|
| **4.9% human** (95.1% not) | share of `type:user` records actually typed by the human | FLEET scale: 537 real prompts vs 10,866 records, one 3-day window (PITCH.md:59,73) |
| **7.1% human** (1,138 of 16,078) | same measure, different run | machine-wide, "today" (PITCH.md:73-79) |
| **~46% not-human** | share of `type:user` turns not the operator | SINGLE-TERMINAL day (PITCH.md:59; also MEMORY.md "46% of type:user turns are NOT Oscar") |
| 94.48% non-human | EYES panel cross-check | this machine, Aug 22 (CONTEXT.md:25) |

- **The moat is a function of fleet size and window** — injected traffic (tool results,
  skill bodies, sub-agent prompts, cross-session peer messages) scales; a person's typing
  does not. This is why the buyer is an org running agents AT SCALE, not a solo dev.
- **The hard-wedge traps** (PITCH.md:70-83): tool result arrives as `type:user` with
  `promptSource:null`; `type:queue-operation` carries text in top-level `content` not
  `message.content` (a naive parser returns EMPTY for 98.8% of real human turns);
  ≥13 record shapes with a trap in both directions (widen too far → corpus fills with the
  fleet's own words). The authorship gate is `fleet/human.py::is_human_turn`:
  `type==user` AND `promptSource in (typed,queued)` AND not isMeta/isSidechain AND
  toolUseResult is None.

## The propagation loop (Surface 5 — "the company")

- `fleet/propagate.py`: `find_best_prompt` (ranks human prompts by episode/outcome signal
  within a task class) → `propagate_prompt` (writes curated prompt text to org skill path;
  NEVER executes transcript text) → `witness_propagation` (ground truth: did the file land,
  VERIFIED-BY-REPO / MISSING / UNMEASURED).
- Law kept (CONTEXT.md:88): nothing extracted from a transcript is ever executed;
  propagation writes curated reviewed text to a named skill path, not raw replay.

## Two docs, two GTM framings of ONE product (reconciled by the two-axis frame)

- `docs/COMPANY.md`: the PR-BLOCKING gate (Stage 0 wedge = free GitHub Action; claim-vs-
  outcome; not code review, not observability). This is the COMPOSITION/authorship axis as
  a CI gate.
- `CONTEXT.md`: the FLEET-MANAGEMENT tool (5 surfaces; the propagation loop is the company).
  This is the AUTHORSHIP-to-outcome axis as an org product.
- Reconciliation: same product, two stages. Gate is the wedge (Stage 0); the corpus +
  propagation is the record (Stage 1+). `contract/gate.py` is where both axes now sit in
  one call.

## Market (web-verified 2026-08-24)

- **Zenity — $125M Series C** (Aug 2026, led by Norwest; SoftBank Vision Fund 2, Hitachi,
  LG, Qumra joined; ~$185M total). Secures/governs AI AGENT ACTIONS (allow/modify/block
  intent) across Copilot, ChatGPT Enterprise, Gemini, Claude, Cursor. Adjacent, not the
  same object: it governs what agents DO, not whether the agent's REPORT is honestly composed.
  Sources: securityweek.com/zenity-raises-125-million-in-series-c-funding/ ;
  businesswire.com/news/home/20260803963850/en/
- **Norm Ai — $120M Series C** (Jul 7 2026, led by Khosla; $1.2B valuation; ~$260M total).
  Agentic COMPLIANCE/law — flags missing disclosures, policy conflicts, checks claims vs
  approved sources, audit trail, built for M365 Copilot. Adjacent: compliance-of-content,
  not composition-honesty of an agent's own work report.
  Sources: techcrunch.com/2026/07/07/ai-law-startup-norm-raises-120m-hits-unicorn-valuation/ ;
  prnewswire.com (Norm Ai $120M at $1.2B).
- **White-space claim ("nobody productizes composition-honesty; authorship-to-outcome is
  the harder-to-copy moat")** is a FABLE market-scan NEGATIVE (Fable scan, Aug 2026; no
  product found), NOT a web-verified fact. An absence claim cannot be cited the way a
  funding round can. Treat it as an informed negative, not proof.

## Sources
- https://www.securityweek.com/zenity-raises-125-million-in-series-c-funding/
- https://www.businesswire.com/news/home/20260803963850/en/Zenity-Raises-$125-Million-to-Secure-the-Era-of-1-Billion-AI-Agents
- https://techcrunch.com/2026/07/07/ai-law-startup-norm-raises-120m-hits-unicorn-valuation/
- https://www.prnewswire.com/news-releases/norm-ai-raises-120-million-at-a-1-2-billion-valuation-led-by-khosla-ventures-to-deliver-the-full-stack-model-for-legal-ai-302819152.html
- arXiv:2502.09054 (LLM cascades; cited in deterministic.py)
