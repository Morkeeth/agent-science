# BASELINE — PeriodCheck partner proof vs Agent Science · 2026-09-20

**Why this exists:** a number scored only against our own data answers "does it work".
It cannot answer "is it better than the alternative". PeriodCheck is the Parallel-track
entry that beat first-run UX narratives in our field notes — measured here at **their**
objects, not our summaries.

## Objects opened (not titles)

| Object | Command / URL | Measured |
|--------|---------------|----------|
| PeriodCheck README | `curl …/ahsan3274/periodcheck/main/README.md` | Claims 13/13 gold, 14 Parallel searches on hosted upload |
| PeriodCheck `live-evaluation.json` | `curl …/main/live-evaluation.json` → `/tmp/periodcheck-live-eval.json` | See summary below |
| PeriodCheck hosted health | `curl https://periodcheck-697827662390.us-central1.run.app/api/health` | `{"status":"ready","service":"periodcheck"}` — **no partner fields** |
| Our live `/health` | `curl …agent-science…/health` | stripped on `00028-hed` (known) |
| Our receipts log | `python3 -c 'from clearance import search; print(search.last_verified_receipt())'` | durable `search_id` present in tree |

## PeriodCheck live-evaluation.json (re-derived)

```text
successful_research: 14
research_failures: 0
gold_claims: 13
gold_claims_extracted: 13
correct_verdicts: 13
end_to_end_accuracy: 1.0
findings: 14
search_id substring count in file: 36
finding[0].parallel_search_ids: ['search_a944c285c2a2e3033f52acd555fa4ba8']
```

**What they prove at object:** each finding carries `parallel_search_ids` from the live run.
Their public `/api/health` does **not** expose partner wiring — the eval file is the proof.

## Agent Science arms (re-derived tonight)

| Arm | Command | Result |
|-----|---------|--------|
| Shipping partner shape (local) | `bash scripts/prove_partner_health_local.sh` | `engine_default: adk`, gemini+parallel fields |
| Shipping call-proof (mocked Parallel HTTP) | `python3 scripts/prove_partner_calls_local.py` | `live_calls=1`, `search_id=search_prove_local_partner_calls` |
| Hosted partner watch | `bash scripts/watch_hosted_partner_health.sh` | **RED** — stripped health on `00028-hed` |
| Durable Parallel receipts in tree | `last_verified_receipt()` | `verified_calls_logged=25`, id `search_d70c5003…` (historical) |
| Naive baseline (env presence only) | old `resolve_gemini_path` + hardcoded checklist | **beats nothing honest** — greened without token (finding doc) |

## Finding vs PeriodCheck

| Dimension | PeriodCheck | Agent Science (tonight) |
|-----------|-------------|-------------------------|
| Live Parallel search_ids on findings | **yes** (36 in eval JSON) | yes in `cache/search_receipts.jsonl` when live ran historically |
| Public health partner fields | **no** (ready only) | **intended yes**; live **stripped** until Oscar deploy |
| Default ADK engine stamp on clear | claimed in README | local path selects `engine: adk` (tests 5/5 + call prove) |
| Offline stranger prove without keys | unclear from README | `prove_partner_calls_local.py` + cold-clone path |
| Compound A→B Parallel drop | not their wedge | offline exhibit + hosted probes (token-gated) |

**Baseline arm we would lose tonight on first-run live Parallel evidence:** PeriodCheck's
`live-evaluation.json` is a stronger **published** runtime-call artifact than our undeployed
health fix. Our counter is compound economics + refuse pole + receipt-backed health once
deployed — not presence-only `/health`.

**Honest loss if judged only on "live Parallel IDs in a public eval file today":** they win.
**Honest win if judged on "second script costs less + verbatim or refuse":** still our wedge —
but only if video/Devpost show it (Oscar).
