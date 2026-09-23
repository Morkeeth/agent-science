# BASELINE — PeriodCheck partner proof vs Agent Science · re-derived 2026-09-23

**Why this exists:** a number scored only against our own data answers "does it work".
It cannot answer "is it better than the alternative". PeriodCheck is the Parallel-track
entry that beat first-run UX narratives in our field notes — measured here at **their**
objects, not our summaries.

**Do not carry the 2026-09-20 row.** Re-open the objects.

## Objects opened tonight (2026-09-23)

| Object | Command / URL | Measured |
|--------|---------------|----------|
| PeriodCheck `live-evaluation.json` | `curl -sS -o /tmp/periodcheck-live-eval.json https://raw.githubusercontent.com/ahsan3274/periodcheck/main/live-evaluation.json` | summary + findings below |
| PeriodCheck hosted health | `curl -sS -w '%{http_code}' https://periodcheck-697827662390.us-central1.run.app/api/health` | **HTTP 500** HTML error page (was `ready` on 2026-09-20) |
| Our live `/health` | `curl -sS …/health` | stripped on `00028-hed` (unchanged) |
| Our live `/partners`, `/truths/ui` | curl `-w '%{http_code}'` no follow | **HTTP 303** each |
| Naive vs shipping | `python3 scripts/eval_hosted_partner_baseline.py` | naive **3/3**, shipping **0/3** |

## PeriodCheck live-evaluation.json (re-derived 2026-09-23)

Top-level keys are `summary`, `findings`, `failures`, … — not flat counters. From `summary`:

```text
successful_research: 14
research_failures: 0
gold_claims: 13
gold_claims_extracted: 13
correct_verdicts: 13
end_to_end_accuracy: 1.0
findings: 14
correct on findings: 13
parallel_search_id entries across findings: 14
unique search_[hex] ids in file: 25
search_[hex] substring count: 52
finding[0].parallel_search_ids: ['search_a944c285c2a2e3033f52acd555fa4ba8']
```

**What they still prove at object:** each finding carries `parallel_search_ids` from a live run.
Their public `/api/health` tonight does **not** prove readiness (500). The eval file remains
the stronger published Parallel-call artifact.

## Agent Science arms (re-derived 2026-09-23)

| Arm | Command | Result |
|-----|---------|--------|
| Shipping partner shape (local) | `bash scripts/prove_partner_health_local.sh` | `engine_default: adk`, callable gemini patched |
| Shipping call-proof (mocked Parallel) | `python3 scripts/prove_partner_calls_local.py` | `live_calls=1`, `search_id=search_prove_local_partner_calls` |
| Judge film surfaces (local) | `bash scripts/prove_judge_surfaces_local.sh` | truths+visibility+popular 200; registry 303; clear 401 |
| Hosted partner watch | `bash scripts/watch_hosted_partner_health.sh` | **RED** — stripped health |
| Hosted baseline eval | `python3 scripts/eval_hosted_partner_baseline.py` | **naive 3/3 beats shipping 0/3** |
| Durable Parallel receipts in tree | `last_verified_receipt()` | historical `verified_calls_logged=25` |

## Finding vs PeriodCheck

| Dimension | PeriodCheck (tonight) | Agent Science (tonight) |
|-----------|----------------------|-------------------------|
| Live Parallel search_ids on findings | **yes** (14 entries / 25 unique in eval JSON) | yes in `cache/search_receipts.jsonl` when live ran historically |
| Public health partner fields | health **500** (no partner fields either) | **intended yes**; live **stripped** until Oscar deploy |
| Public judge film UI | n/a | **303** on live; fixed in tree (`prove_judge_surfaces_local.sh`) |
| Offline stranger prove without keys | unclear from README | call-proof + judge-surface prove + cold-clone |
| Compound A→B Parallel drop | not their wedge | offline exhibit + hosted probes (token-gated) |

**Baseline arm we lose tonight on published live Parallel IDs:** PeriodCheck's
`live-evaluation.json` still beats our undeployed health/film fix.

**Baseline arm that beats us on our own hosted desk tonight:** naive `ok:true` /
HTTP&lt;500 — `eval_hosted_partner_baseline.py` exit 2. That is the finding worth more
than a green demo.

**Honest win if judged on "second script costs less + verbatim or refuse":** still our
wedge — but only if video/Devpost show it after Oscar deploy (Oscar).
