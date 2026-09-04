# RECEIPT — Partner honesty night · 2026-09-04

**Slice:** Partner integrations proved at runtime + compound honesty exhibit that can go RED.  
**Branch:** `cursor/partner-ambition-night-6515`  
**Hosted:** https://agent-science-568004190078.us-central1.run.app

---

## Commands run (at object)

```bash
python3 tests/test_watch_it_go_red.py                 # 72/72
bash scripts/verify_partners_hosted.sh                # 4/4 partners · clear engine=adk · Parallel≥1
python3 scripts/partner_honesty_exhibit.py            # shipping vs naive · sealed class
python3 scripts/bench_check_docs.py                   # 127/127
python3 scripts/eval_refusal_baseline.py              # baseline 5/6 vs shipping 6/6
python3 scripts/eval_refusal_ablation.py              # ablation 5/6 vs shipping 6/6
python3 scripts/eval_scorer_symmetry.py               # 5/6 vs 6/6 on delivered labels
python3 scripts/eval_verify_holdout.py                # HOLDOUT OK · 4 files
curl -s …/health | python3 -m json.tool               # engine_default: adk
curl -s …/stats | python3 -m json.tool                # shelf n re-derived
gh repo view Morkeeth/agent-science --json visibility # PUBLIC
```

Raw JSON from the final honesty run: `docs/RECEIPT-partner-honesty-exhibit-raw-2026-09-04.json`

---

## Partners (all four · runtime)

| Partner | Object | Measured 2026-09-04 |
|---------|--------|---------------------|
| Gemini / Vertex | `/health` `gemini_path` | `vertex:hack-fleet` |
| Parallel | `POST /clear` `parallel_calls` | ≥1 on fresh claim · SDK 1.3.2 |
| Google Cloud | hosted desk | Cloud Run URL responds `/health` 200 |
| Agent Builder / ADK | `/health` + `/clear` | `engine_default: adk` · `engine: adk` · `adk_tool_calls: ["clear_script_tool"]` · adk 2.7.1 |

---

## Honesty exhibit — three runs tonight

| Stamp (UTC) | Shipping class | A→B Parallel | B hits | Sealed (B\<A) | Soft (B≤A) | Naive | Winner |
|-------------|---------------|-------------:|-------:|:-------------:|:----------:|-------|--------|
| 00:10:24 | STRICT_DROP | 1→0 | 1 | yes | yes | contaminated (same tokens) | shipping_strict* |
| 00:12:42 | STRICT_DROP | 2→1 | 1 | yes | yes | A=2→B=1 hits=0 (log_hits not yet printed) | shipping_on_corpus_hits_only† |
| 00:15:26 | **SOFT_PASS_FLAT** | 1→1 | 1 | **no** | yes | A=1→B=1 hits=0 | **shipping_soft_only** |
| 00:22:38 | **SOFT_PASS_FLAT** | 1→1 | 1 | **no** | yes | A=2→B=1 hits=0 **log_hits=2** · API 2→1 | **shipping_soft_only** |

\*First naive arm reused shipping claim text.  
†00:12 blamed search cache; **00:22 corrected** — mechanism is cross-subject `log_hits`.

### FINDING_RED (publishable embarrassment)

1. **Soft verify can green while sealed prediction fails.** Runs 00:15 and 00:22: `SOFT_PASS_FLAT` — soft PASS, sealed `B < A` FAIL. Mechanism: Run B extracted an extra claim; Parallel stayed flat while overlap hit corpus/log.
2. **Naive Parallel drop = cross-subject `log_hits`, not search cache.** Run 00:22: naive A=2→B=1 Parallel with `corpus_hits=0` and **`log_hits=2`**. An earlier draft blamed search cache (nearer proxy); corrected at object. Search cache is still real (`SHIP_B parallel_api_calls=0` with `parallel_calls=1`) but was not the naive claim-path mechanism.
3. **First naive arm was contaminated** (same claim text as shipping → Parallel 0 on A). Fixed with distinct tokens before clean runs.

**Pitch correction:** film **corpus_hits** for same-subject compound; read **log_hits** before calling a Parallel drop "compound"; never claim Parallel always drops.

**WRONG (this agent):** diagnosed search-cache first without printing `log_hits` on the gap report. Fixed in exhibit + finding doc.

---

## Live shelf (re-derived · do not carry older docs)

```bash
curl -s https://agent-science-568004190078.us-central1.run.app/stats
```

At honesty final run: **n=312** · hit rate **0.627** · queries_logged **279** · reuses **138**.

---

## Qwen eval gate (re-run 2026-09-04)

| Arm | Result |
|-----|--------|
| Baseline (substring) | **5/6 = 0.833** CI [0.436, 0.970] |
| Ablation (verify off) | **5/6 = 0.833** |
| Shipping | **6/6 = 1.000** CI [0.610, 1.000] |
| Delta | **+1** · McNemar p=1.0000 (b=0 c=1) · RC5 discordant |
| Scorer symmetry | baseline 5/6 vs shipping 6/6 on delivered labels |
| Holdout | 4 files pinned |

---

## BLOCKED

| Item | Exact missing / failure |
|------|-------------------------|
| Local live orphan A/B | `PARALLEL_API_KEY` unset · `~/.config/keys/parallel.key` absent · `GEMINI_API_KEY` unset on this VM |
| Hosted orphan-works full script | Still **504 @ 300s** — `docs/FINDING-orphan-works-timeout-2026-09-03.md` (not re-hammered tonight; prior finding stands) |
| `git push origin main` | Oscar outward / cloud agent ships PR branch |

---

## Docs touched tonight

- `scripts/partner_honesty_exhibit.py` — new
- `scripts/verify_partners_hosted.sh` — prints `COMPOUND_CLASS` soft vs sealed
- `docs/PARTNER-INTEGRATIONS-2026-08-30.md` — last-verified stamp
- `docs/SUBMISSION-PACK-2026-08-29.md` — public repo + shelf counts
- `docs/DESIGN-PARTNER-LOOP.md` — measured latencies + friction
- `README.md` · `docs/PITCH-TOMORROW.md` — track brief first screen
- `hack.md` — NOW + LOG
