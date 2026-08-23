# NEXT STEPS — read this first, every session

**PRODUCT:** Agent Science — clearance audit platform (startup ceiling)  
**Checkpoint:** Agentic Cinema Sep 9 · Parallel track

## Ambition

> Over-build toward the **production company**. Hackathon is a wedge, not the product.
> Ceiling: `BUILD-PLAN-STARTUP.md`. Near calendar: `PLAN-30.md`. Oscar cuts.

## State
- Hosted Desk + Vertex ADC + GCS corpus + live compounding ✅  
- Orphan A/B 43% search avoided · 70 controls · refusal set ✅  
- **Not yet a startup app:** no tenants, async jobs, dossier PDF, design partner

## This session’s head of queue (from STARTUP §5)

| # | Slice | Why |
|---|-------|-----|
| **1** | Independence workbench on the Desk | Dust Bowl failed primary; corroboration must be visible |
| 2 | Async runs + job status | Production scripts ≠ sync HTTP |
| 3 | Dossier PDF/JSON export | The paid artifact |
| 4 | Org + subject shelves (multi-tenant skeleton) | Two customers |
| 5 | Agent Builder proved as client | Platform requirement + real agent path |
| 6 | Design partner on their material | Day-two user ≠ judge |
| 7 | Asset leg in production path | Second noun / second buyer |

Video / Devpost / public — parked.

---

## 2026-08-23 — Agent Builder wired onto the default path (GM run, Oscar away)

**The board's #1 "ONLY YOU" item was stale.** SLASK/ACTIONS/PITCH/BUILD-PLAN all said
Agent Builder was blocked on "Oscar provisions GCP + billing". Verified live this
morning: project `hack-fleet`, `billingEnabled: true`, `aiplatform` + `agentregistry`
enabled, ADC on disk. Nothing was blocked. The slice was executable and is now done,
minus the deploy.

- ADK now runs `/clear` by default; every gap report stamps `engine: adk|direct`.
- Proved with keys stripped, not merely absent. Receipt: `docs/RECEIPT-agent-builder.md`.
- 72 controls still pass.
- Defect found: the ADK client 404s on any regional Vertex endpoint. Only `global`
  publishes these models — `clearance/gemini.py:51` already knew, `deploy.sh` now sets it.

**LEFT FOR OSCAR (one command):** `bash deploy.sh` in `~/CODE/cleared`. It writes a
Secret Manager version, edits IAM and ships a billed public revision, so it is his click
by the script's own header. Rotate the Parallel/Gemini keys first if that is still open.
Then: `curl -s <hosted>/health | grep '"engine_default": "adk"'` → 3/3.
