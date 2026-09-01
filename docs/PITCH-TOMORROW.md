# Pitch tomorrow · Agent Science

**For Oscar · 2026-09-01 morning**  
**Deadline:** Agentic Cinema · 2026-09-09 14:00 PDT · **8 days**

---

## 30-second pitch (say this first)

> **You get:** every checkable claim back as a verbatim quote with its source URL, or
> UNSOURCED with a named reason — plus a truth shelf that compounds so the second ask is free.
>
> **Proof:** hosted compound exhibit — **A=1 → B=0** Parallel calls with
> `corpus_hits=1` on repeat. Four partners wired at runtime: Vertex, Parallel, Cloud Run, ADK.
>
> **Constraint:** if the document does not contain the exact passage, refuse — never paraphrase,
> never infer. We refused our own pitch headline on camera because of this rule.
>
> Clearance and EU regulation? One vertical on the same layer — not the whole product.

---

## 60-second judge pitch

**Hook:** Every agentic coder asks the same questions — RAG vs Obsidian, Ralph loop, memory, context windows. Today they get one summarized answer with footnotes. They cannot see what was skipped.

**Product:** Agent Science websearch returns a **full visibility panel** — primary verdict, transparency (angles searched, shallow-route warning, imbalance), field adoption (★), blogs, fleet peers, and **stack-fit**: does this truth fit *your* repo, and what improves if you adopt it?

**Proof on camera:**
1. **Hosted** `/visibility/ui?q=ralph+loop+agentic` — transparency pane + CONTRARY stamp (no CLI needed) · live: primary `CONTRARY_TO_RESEARCH`, transparency keys `angles_searched`, `shallow_route`, `imbalance`
2. `/truths/ui` — ranked queries, **284 claims** (live 2026-09-01; was 265+ at seal)
3. Compound: same subject twice → `parallel_calls` drop, `corpus_hits` rise — `docs/SEALED-PREDICTION-2026-08-31.md` (A=1→B=0)

**Moat:** Positive truths + negative truths (named refusal) + popularity → self-tuning dictionary. Competitors prove the first script. We prove the **second costs less** — and we show *how we searched*.

**Hosted:** https://agent-science-568004190078.us-central1.run.app  
**Film URL:** https://agent-science-568004190078.us-central1.run.app/visibility/ui?q=ralph+loop+agentic  
**Revision:** deployed with `/visibility` + `/truths/ui`

---

## What changed overnight (verified)

| Shipped | Evidence |
|---------|----------|
| Truth layer code on `main` | `clearance/visibility.py`, `contrary.py`, `stack_fit.py` |
| **284 claims** on shelf (live) | hosted `/truths/ui` · `curl -s …/truths/ui` |
| **Deployed** | `GET /health` → `engine_default: adk`, `parallel_sdk: true` |
| `/truths/ui` live | `curl …/truths/ui` → dashboard HTML |
| 52 inbox ingests | `python3 scripts/auto_ingest_inbox.py` → receipt `docs/RECEIPT-agent-science-shape-2026-09-01.md` |
| Film scout | `docs/FILM-SCOUT-COMMANDS.md` |
| Full gate | `bash scripts/full_gate.sh` OK |

---

## Your morning (30 min)

| # | Action | Time |
|---|--------|------|
| 1 | Scout film — `docs/FILM-SCOUT-COMMANDS.md` beats 1–3 in terminal | 10 min |
| 2 | Record ≤180s — lead **transparency WOW**, then one non-EU SOURCED, one refuse | 15 min |
| 3 | Devpost paste — `docs/DEVPOST-READY.md` (elevator pitch updated below) | 5 min |

**Do not lead with:** EU-only demos · flywheel metrics as headline · orphan-works full compound (B 503)

---

## Elevator pitch (Devpost — paste this)

> **The truth layer for agentic builders** — transparent websearch that shows what your agent searched, what the field believes and uses, and whether a claim is sourced, refused, or **contrary to research**. Verbatim evidence or named cause. The registry compounds: ask once, free forever. Clearance and E&O are one customer on the same shelf.

---

## One-liner unfair advantage

> Only Agent Science **finds the latest truths across the agentic stack and shows how it got there** — not a verified badge, a full visibility panel.

---

## Demo commands (copy-paste)

```bash
# WOW beat
python3 -m clearance.stack_cli visibility "ralph loop agentic" --full --no-personal | head -40

# Contrary stamp
python3 -m clearance.stack_cli lookup "ralph loop agentic practice"

# Stack-fit
python3 -m clearance.stack_cli stack-fit "science_lookup MCP fleet"

# Hosted dashboard
open https://agent-science-568004190078.us-central1.run.app/truths/ui
```

---

## Still Oscar-only

- [ ] Record video · upload to Devpost
- [ ] Devpost submit button
- [ ] Logged-out verify video on entry page

---

## If a judge pushes back

| Objection | Answer |
|-----------|--------|
| "Another fact-checker" | We refuse without cause; we stamp CONTRARY when field outruns papers; we show search angles — not one answer |
| "Clearance is crowded" | Clearance is one vertical. Product is daily agentic websearch + truth dictionary |
| "Where's the compound proof?" | Sealed A=1→B=0 Parallel, corpus_hits=1 on hosted — `SEALED-PREDICTION-2026-08-31.md` |
| "PeriodCheck wins UX" | They win first-run. We win **economics + transparency + agentic truth layer** |

---

*Overnight receipt: `docs/RECEIPT-overnight-2026-09-01.md`*
