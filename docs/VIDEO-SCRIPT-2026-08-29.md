# VIDEO SCRIPT — Agent Science · Agentic Cinema

**Target:** ≤ 180 seconds · **Beats below sum to 178 s**  
**Capture:** screen record hosted URL + local registry UI · voiceover reads bold lines  
**Do not:** stage claims — use real `/clear` output and `ask_registry.py --serve`  
**EYES pass 2026-08-31:** refuse + E&E lead; compound is secondary. See `docs/EYES-HACK-PASS-2026-08-31.md`.

---

## Pre-roll (before timer)

- Browser tab 1: https://agent-science-568004190078.us-central1.run.app/
- Browser tab 2: hosted `/registry` and `/popular/ui`
- Script file ready: `fixtures/scripts/compound-mini-A.txt` (fresh subject for compound)
- **Non-EU demos ready** (pick two — see `docs/USE-CASES-2026-08-31.md`):
  - `fixtures/scripts/demo-arxiv-attention.txt` (science)
  - `fixtures/scripts/demo-rights-cne.txt` (archive rights)
  - `fixtures/scripts/demo-dust-bowl-mini.txt` (US history)
  - `fixtures/scripts/demo-us-orphan-policy.txt` (US copyright policy)
- `fixtures/shift-ai-training-vs-noncommercial.md` for buyer flip

**Anti-monoculture:** Do not let every SOURCED beat be EUR-Lex. At least one of arXiv / CNE / dust-bowl must appear on camera.

---

## WOW transparency beats (film — insert after 0:36 SOURCED demo)

| Time | Sec | Beat | On screen | Voiceover |
|------|----:|------|-----------|-----------|
| 0:36+ | 15 | **Transparency** | `python3 -m clearance.stack_cli visibility "ralph loop agentic" --full` — pane **1b** angles + SHALLOW_ROUTE | "I finally know what my agent searched — not just verified. Every tier, every alias route." |
| +15 | 12 | **Not just verified** | Same panel — primary `CONTRARY_TO_RESEARCH` stamp | "When the field outruns the paper, we stamp CONTRARY TO RESEARCH — with why." |
| +27 | 10 | **Truths easy to find** | `/truths/ui` or `/popular/ui` — ranked queries + ★ strip | "The most-asked truths get cheaper — and you see what the field actually runs." |
| +37 | 8 | **Stack-fit** | `stack-fit "science_lookup MCP"` — fit=fits | "Magnet asks: does this truth fit *your* stack — and how does it improve you?" |

*Reorder into timed beats as needed; total still ≤180s.*

## Timed beats (EYES order)

| Time | Sec | Beat | On screen | Voiceover |
|------|----:|------|-----------|-----------|
| 0:00 | 10 | **Hook — truth layer** | Title: *Agent Science — truth layer for what builders believe and use* | "Your agent websearches. You get one answer and a green check. You never see what was skipped. We built the layer that shows the full search — and stamps when the field outruns the paper." |
| 0:10 | 14 | **Problem** | E&O checklist · provenance stall | "Studios and AI labs stall on the same thing: nobody can prove provenance at asset level. Humans do this by hand." |
| 0:24 | 12 | **Rule** | Constructor rejects uncited verdict (3 s) | "Cite the document, or print that you could not. No citation — no verdict. Enforced in code." |
| 0:36 | 22 | **Demo — SOURCED (non-EU first)** | Prefer `/clear` on `demo-arxiv-attention.txt` **or** dust-bowl mini — **verbatim span**. EU lookup only as backup. | "Same desk. A paper id, a film history claim — we return the exact sentence from the source, not a summary." |
| 0:58 | 18 | **Demo — refuse (second domain)** | `demo-rights-cne.txt` or registry UNKNOWN + `cause` | "Archive code CNE — copyright never evaluated. That is not permission. We refuse with a named cause." |
| 1:16 | 14 | **Honest marketing** | C5: *search_found_no_admissible_source* on "94% of film archives" | "We pointed the product at our own pitch. It refused our headline. The number was fine — the object was not." |
| 1:30 | 20 | **Compound** (secondary) | Fresh subject A→B: `corpus_hits` ≥ 1 · `parallel_calls` drop if visible | "Run the same subject twice. The shelf remembers — fewer search calls, same honest verdicts." |
| 1:50 | 18 | **Second buyer** | `shift-ai-training-vs-noncommercial.md`: **247 / 600 flip** | "One index, two buyers. Forty-one percent of the library changes verdict when the use case changes." |
| 2:08 | 12 | **Dictionary** | `/popular/ui` — top queries · hit rate | "The most-asked truths get cheaper for everyone — a truth dictionary, not a chat log." |
| 2:20 | 10 | **Close** | Hosted URL + repo + MIT | "Agent Science — link in description." |

**Total: 178 s**

---

## B-roll inserts (optional, inside beats above)

- `docs/COMPOUND-EXHIBIT-2026-08-29.md` table: A=2 Parallel, B=1, corpus hits=2
- `docs/SECOND-SUBJECT-RECEIPT-2026-08-29.md` — dust-bowl reuses orphan log at 0 Parallel
- Health check: `"engine_default"` field (note ADK ⬜ until Oscar runs `deploy.sh` — do not claim ✅ on video)

---

## Post-production checklist

- [ ] Total runtime ≤ 3:00 (re-cut if over)
- [ ] At least one **SOURCED** verbatim span visible on screen
- [ ] At least one **UNKNOWN** with named cause visible
- [ ] Hosted URL readable in final frame
- [ ] No API keys, no Secret Manager values in frame
- [ ] Upload to Devpost (Oscar — not in this slice)
