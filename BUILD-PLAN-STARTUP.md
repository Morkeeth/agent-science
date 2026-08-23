---
date: 2026-08-23
status: ACTIVE — supersedes PLAN-30 as the ambition ceiling; PLAN-30 remains the near wedge
horizon: startup · full production clearance platform
rule: over-build toward the company; Oscar cuts. Hackathon is a checkpoint, not the product.
---

# BUILD PLAN — Agent Science as a production company

**Company sentence:** A production cannot ship (or insure, or license to AI) until every
fact is sourced and every asset is cleared — with a compounding corpus so the second
show on the same subject costs a fraction of the first.

**Not the product:** “AI googles your script.”  
**Is the product:** an **audit platform** — named probes, refuse-to-infer, durable memory,
exportable dossiers lawyers actually attach to E&O packs.

Sep 9 Agentic Cinema = **wedge proof** that strangers trust the desk. Everything below
assumes we keep building past the gallery whether or not we place.

---

## 0 · What already exists (do not rebuild)

| Capability | Receipt |
|---|---|
| Citation-guarded verdicts | `Verdict.__post_init__` · 70 controls |
| Live Gemini + Parallel + Vertex ADC | Cloud Run `/health` → `vertex:hack-fleet` |
| Compounding Desk + A→B exhibit | orphan A/B **43%** search avoided; live `live-smoke` 2→1 |
| Durable corpus shelf | GCS `hack-fleet-agent-science-corpus` |
| Refusal held-out set | `fixtures/refusal-correctness/` |
| Independence-as-set (engine) | `clearance/independence.assess` |

**Gap vs a startup:** one anonymous paste URL, no tenants, no workflow, no paid artifact
lifecycle, no asset leg in production, no API contract, no design partner.

---

## 1 · North-star product (full production app)

Imagine the day-two user opening **app.agentscience** (working name) Monday morning:

1. **Org / workspace** — studio or boutique clearance firm; SSO; roles (researcher,
   counsel, producer read-only).
2. **Subject shelves** — “orphan-works”, “dust-bowl”, “series-S02” — living corpora with
   remembered verdicts, owners, retention policy.
3. **Ingest** — script paste, Final Draft / Fountain / PDF / shared Drive folder;
   optional shot-list / asset CSV for the second noun.
4. **Clearance run** — async job with progress; Gemini extract → Parallel → locate →
   verify → independence assess → gap report. Queue, retries, spend meter per run.
5. **Dossier** — the paid object: attorney-scannable memo + machine JSON + PDF export +
   immutable run hash. Versioned when script revises.
6. **Workbench** — claim-level triage: assign, comment, override with reason (overrides
   never silent), re-run one claim, link to matter in Clio / NetDocuments later.
7. **Compounding dashboard** — Parallel spend A vs B, corpus hit rate, $/cleared claim;
   the unit-economics story as a first-class screen.
8. **Asset leg** — same engine, noun=ASSET: library items × instruments × use questions;
   second buyer without re-ingest.
9. **API + webhooks** — `POST /v1/runs`, `GET /v1/dossiers/{id}`, signed webhooks on
   complete; Agent Builder / ADK as one client among many.
10. **Trust plane** — audit log of every probe call, model id that answered, corpus hit
    vs live search; no silent model swap; kill #2 enforced in CI.

If a stranger screenshots one surface and it could be Perplexity, we failed.

---

## 2 · Who pays (production economics)

| Buyer | What they buy | Price shape (hypothesis) |
|---|---|---|
| Clearance / research lead | Dossier per production + shelf memory | Per-run + seat |
| Boutique firm | Multi-matter workbench + export | Seat + usage |
| Archive / library | Asset-leg library scan + second-question flips | Per-library / per-question |
| E&O underwriter (expansion) | Measurable unclearable % + named gaps | Per-submission / portfolio |
| AI lab / rights deal (expansion) | Provenance pack for diligence | Per-deal |

**Defensibility:** compounding corpus + refusal discipline + instrument graph.  
**Not defensibility:** nicer chat UI.

---

## 3 · Architecture of the production system

```
                 ┌─────────────┐
  Ingest ──────►│  Run engine  │──► Verdict store (Postgres)
  (script/asset)│  (clearance) │──► Document cache
                 └──────┬──────┘
                        │
         ┌──────────────┼──────────────┐
         ▼              ▼              ▼
   Corpus shelf    Probe meter     Dossier service
   (compounding)   (Parallel/      (PDF/JSON/memo)
                    Gemini spend)
         │
         ▼
   Independence graph (origins, not URL strings)
```

**Hard rules in production:**
- Multi-tenant isolation on every table (`org_id`).
- Secrets only via Secret Manager / Workload Identity — control already in suite.
- Models ladder + record **which model answered**.
- Corpus hits print `reused_from` when wording drifts.
- World’s gaps (`no_instrument`, `source_does_not_state_it`) must not be “optimized away.”

---

## 4 · Horizons (ambitious ceiling)

### H0 · Now → Sep 9 (wedge / checkpoint)
Prove the desk is real: compounding on URL, honest UNSOURCED, stranger paste.  
Packaging late. **Do not freeze product depth for film.**

### H1 · Sep 10 → Oct 31 (MVP that a firm could trial)
Multi-tenant workspace · async runs · dossier PDF · claim workbench · spend meter ·
one design-partner clearance lead on **their** script · independence UX on Desk ·
Agent Builder as first-class client · Postgres corpus (GCS sqlite was the bridge).

### H2 · Nov → Jan (production platform)
SSO · roles · audit log export · webhooks · script revision diffs · matter IDs ·
asset-leg library upload · second-question flips as a product feature · billing
(Stripe) · SLA / status page · EU data residency option.

### H3 · 2026 H1 (company)
E&O underwriter read-only portal · AI-licensing diligence packs · marketplace adapters
(read-only: “here is what you cannot clear”) · corroboration graph v1 · price book ·
first paid renewal.

---

## 5 · Near build queue — next 7 slices (execute in order)

These are the **ambitious next moves from today’s codebase**, each verifiable alone.
Oscar cuts; do not thin preemptively.

| # | Outcome | Done when | Size | Risk |
|---|---|---|---|---|
| **1** | **Independence workbench on the Desk** | Gap memo shows origin groups + corroboration basis per claim; Dust Bowl exhibit gains ≥1 PRIMARY-cleared row without Wikipedia round-trip | L | Primary sources for Dust Bowl are thin |
| **2** | **Async run + job status** | `POST /runs` returns `run_id`; poll/`GET /runs/{id}` shows progress; 5-min script doesn’t block HTTP | L | Cloud Run timeouts / worker shape |
| **3** | **Dossier export (the paid artifact)** | One button / `GET /dossier/{id}.pdf` + JSON with run hash; counsel can forward without the Desk UI | M | PDF fidelity vs memo HTML |
| **4** | **Org + subject shelves (multi-tenant skeleton)** | Two orgs cannot read each other’s corpus; subject shelf has owner + remembered count | L | Auth choice (Firebase / IAP / custom) |
| **5** | **Agent Builder proved as default client** | ADK agent on Agent Platform invokes `clear_script` / runs API; receipt with `env -u` | M | Platform unknowns |
| **6** | **Design partner loop** | One real clearance lead runs **their** (or NDA) script; CURSOR-LOG has verbatim friction list | M | Access / scheduling |
| **7** | **Asset leg revived in production path** | Same Desk accepts asset CSV + use question; second question flips ≥10% on held library with control | L | Kill #2 / invented contracts |

After slice 1 ships, re-plan 2–7 against reality.

---

## 6 · Full production backlog (do not start all at once)

**Product**
- [ ] Script revision diff → only re-clear changed claims
- [ ] Claim assignment, comments, override-with-reason
- [ ] DISPUTED as first-class when two primary sources conflict
- [ ] Parallel Task / deep research as stretch probe on one UNSOURCED claim
- [ ] Compounding dashboard (spend, hit rate, $/claim)
- [ ] Matter / production metadata (title, network, air date)

**Platform**
- [ ] Postgres + migrations (replace sqlite/GCS bridge)
- [ ] Worker pool (Cloud Run jobs / Cloud Tasks)
- [ ] Object storage for source PDFs with retention
- [ ] OpenAPI + versioned `/v1`
- [ ] Webhooks + idempotency keys
- [ ] Observability: structured logs, probe metrics, error budgets
- [ ] Staging + prod projects; preview deploys

**Trust & compliance**
- [ ] Append-only audit log (who saw which dossier)
- [ ] Data processing agreement template
- [ ] Model/provider allowlist in CI
- [ ] Expand refusal-correctness set quarterly
- [ ] Penetration pass before first paid logo

**GTM**
- [ ] Design partner LOI
- [ ] Price: per-production vs seat vs library
- [ ] Case study from orphan-works + dust-bowl (public domain only)
- [ ] “Audit layer not marketplace” one-pager vs Troveo/Veritone/Vermillio

**Company engine (shared method)**
- [ ] Keep clearance vertical primary
- [ ] Registry-054 / Helicon remains sibling unless Oscar rules shared-engine pitch

---

## 7 · Explicit non-goals (still)

- Invented contracts / fake RED for demo theatre (kill #2)
- E&O underwriter as **v1 demo persona** (expansion buyer only)
- Replacing counsel — we produce the dossier; humans bind risk
- Winning the hackathon by packaging while the workbench is hollow

---

## 8 · How this file relates to the others

| Doc | Job |
|---|---|
| **This file (`BUILD-PLAN-STARTUP.md`)** | Ambition ceiling — production company |
| `PLAN-30.md` | Near calendar / wedge hygiene |
| `NEXT-STEPS.md` | What to build **this session** |
| `docs/WEDGE.md` / `docs/AMBITION-AUDIT.md` | Idea lock |
| `docs/VALIDATION-*.md` | Claims checked against primary sources |

**Default stance:** when choosing between a thinner demo and a deeper production seam,
take the deeper seam — until Oscar stops you.
