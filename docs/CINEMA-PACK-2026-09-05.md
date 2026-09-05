# Cinema pack — Agent Science · Agentic Cinema · 2026-09-05

**Deadline:** 2026-09-09 14:00 PDT · **Track:** Parallel  
**Repo @ pack write:** `ea05a10` (main) + this pack branch · **Event:** https://agentic-cinema.devpost.com/  
**Receipt:** `docs/CLOUD-RECEIPT-cinema-pack-2026-09-05.md`  
**Stop at Oscar doors:** key rotate · YouTube/Vimeo upload · Devpost submit · paid unbounded research · deploy secrets

This pack is agent-complete for paste + cold proof. Boxes below are ticked only when the named command was run on 2026-09-05.

---

## 0 · Measured truth (do not paste stale URLs)

| Object | Measured 2026-09-05 | Command |
|--------|---------------------|---------|
| Repo visibility | **public** · MIT · `private: false` | `curl -sS https://api.github.com/repos/Morkeeth/agent-science` |
| Repo created / public-since date | `2026-08-22T17:17:41Z` (matches prior PublicEvent record; PublicEvent absent from last-30 events API) | same + `created_at` field |
| Hosted `/health` | **200** · `ok: true` · `mode: private-workspaces` · `revision: agent-science-00026-zel` | `curl -sS …/health` |
| Hosted desk / visibility / registry / truths / popular / search / clear | **303 → login** (`Sign in · Agent Science`) | `curl -sS -D- -o/dev/null …/visibility/ui` |
| Hosted `/api/cases` | **401** `Workspace access key required.` | `curl -sS …/api/cases` |
| Video file | `demo/demo-final.mp4` = **179.675 s** (≤180) | `ffprobe … demo/demo-final.mp4` |
| Video URL on Devpost | **PLACEHOLDER** — `submission/VIDEO-URL.txt` still empty of a public URL | `cat submission/VIDEO-URL.txt` |
| Cold verify (this pack branch) | **exit 0** · compound A=**2**→B=**1** · corpus_hits B=**2** | `bash scripts/verify_cold_clone.sh` |
| Cold verify (public `main` @ `ea05a10` before this fix) | **exit 3** · A=2 B=3 corpus_hits=0 | same on fresh clone of main |
| NIGHTRUN live policy | **not approved** on a fresh case store | `research_policy.is_approved(…)` → `False` |

**Judge implication:** Devpost “Project URL” still points at the hosted Run.app hostname, but a logged-out stranger now hits a sign-in wall. Film from `docs/film/` screenshots + local cold demos until Oscar restores a public judge surface or submits with an authenticated workspace demo.

---

## 1 · Exact Devpost paste fields

Copy each cell into the matching Devpost form field. Do not invent a video URL.

| Field | Paste exactly |
|-------|----------------|
| **Project name** | Agent Science |
| **Tagline / elevator pitch** | The truth layer for what people believe and use: every checkable claim comes back as a verbatim quote with its source URL, or UNSOURCED with a named reason, and the shelf compounds so the second ask is free. |
| **Partner track** | Parallel |
| **Project URL (hosted)** | https://agent-science-568004190078.us-central1.run.app |
| **Hosted honesty note (put in description, not the URL field)** | Hosted revision `agent-science-00026-zel` is `mode: private-workspaces`. Logged-out `/`, `/visibility/ui`, `/truths/ui`, `/registry`, `/search`, `/clear` redirect to Sign in. `/health` remains public JSON. Stranger proof is the cold clone below. |
| **Open-source repository** | https://github.com/Morkeeth/agent-science |
| **License** | MIT |
| **Video URL** | *(Oscar — paste public YouTube/Vimeo after upload; leave blank until then)* |
| **Built with** | python, parallel-web (Parallel Search SDK), gemini (Vertex AI), google-cloud-run, google-adk, sqlite, google-cloud-storage |

**Long description:** paste `submission/DEVPOST-PASTE.md` § About through § What's next — then **edit** any sentence that claims an unauthenticated hosted desk / visibility UI works for strangers. Replace with the honesty note above + cold clone block.

**Sealed prediction (optional Devpost “what we predicted”):**

> On the hosted URL, a second `POST /clear` with the same `subject` and an overlapping claim returns `corpus_hits ≥ 1` and Run B `parallel_api_calls` ≤ Run A.  
> Sealed 2026-08-31: A=1 → B=0 Parallel, corpus_hits=1 — `docs/SEALED-PREDICTION-2026-08-31.md`.  
> Offline re-measure 2026-09-05 (this pack): A=2 → B=1 Parallel, corpus_hits B=2 — `python3 scripts/compound_exhibit_receipt.py`.

---

## 2 · Cold stranger path (no key, no network after clone)

Documented for a person who has never met this repo:

```bash
git clone https://github.com/Morkeeth/agent-science.git && cd agent-science
bash scripts/cinema_pack_gate.sh           # one command: pack docs + public repo + hosted wall + cold verify
# or piece-wise:
bash scripts/verify_cold_clone.sh          # must print: cold-clone verify OK
bash scripts/demo_truth_layer.sh           # local truth-layer panes; no key
python3 scripts/compound_exhibit_receipt.py
# Offline research plan (no live spend):
python3 -m clearance research start "When does persistent memory help coding agents?" --root .
```

**Hosted desk demo (expected BLOCKED while private-workspaces):**

```bash
bash scripts/demo_clearance_desk.sh
# expect exit 2 + BLOCKED message naming mode=private-workspaces
```

**Do not claim** `new_user_trial.sh` / `long_run_goal.sh` as stranger-no-key proofs — they hit hosted APIs that now require a workspace.

---

## 3 · Use-bar session template

Oscar fills after **one real search** (do not claim he did):  
→ `docs/USE-BAR-SESSION-TEMPLATE.md`

---

## 4 · Live field validation gap (re-derived from `NIGHTRUN-2026-09-05.md`)

Read at object: `NIGHTRUN-2026-09-05.md` § Needs operator + `clearance/research_policy.py`.

| Gap | Still needs | Why not closed tonight |
|-----|-------------|------------------------|
| **Six fresh-web investigations** | Operator-approved live aggregate policy + Parallel (and optional Perplexity/reasoner) keys | Overnight explicitly did **not** authorize research spending; saved-source replay ≠ live |
| **Resource policy approval** | `agent-science research policy --policy-file … --approve` on the case store that will run live | `is_approved` on a dummy aggregate → **False**; MCP cannot approve |
| **Provider auth** | Valid Parallel (and optional Perplexity / reasoner) credentials exercised | Keys unset on this VM; presence-only checks overnight; Perplexity was absent |
| **Matched-budget scientific quality** | Baseline vs candidate research quality under the same live budget | Workflow 3/3 protocol pass ≠ quality lift; no %-lift claimed |
| **Live retraction / prompt-injection / written-number** | Separate measurement | Named as unmeasured in NIGHTRUN |
| **Public launch of overnight research engine** | Oscar review of `e12ca6f`→candidate diff before treating research CLI as the Devpost front door | Publication not authorized by NIGHTRUN |

**Approved live policy is the blocking gate** for any “live field validation” claim. Until Oscar approves a bounded aggregate, agents must not mint spend.

---

## 5 · Oscar-only list (stop here)

| # | Act | Where | Status |
|---|-----|-------|--------|
| 1 | **Rotate keys** (console / Secret Manager) — never via `--set-env-vars` plaintext | GCP console | Oscar |
| 2 | **Upload video** ≤180s public YouTube/Vimeo | `demo/demo-final.mp4` (179.675s) or fresh record from `docs/FILM-PACK-2026-09-03.md` | Oscar |
| 3 | **Paste video URL** into `submission/VIDEO-URL.txt` + Devpost | after upload | Oscar |
| 4 | **Devpost submit** + sealed prediction + logged-out page check | https://agentic-cinema.devpost.com/ | Oscar |
| 5 | **Decide hosted judge surface** — keep private workspaces **or** restore a public film/demo path | Cloud Run | Oscar |
| 6 | **Approve live research policy** (if running NIGHTRUN six-topic live pass) | CLI only | Oscar |
| 7 | Paid unbounded research / key materialization into env deploy flags | — | **Forbidden** |

Film pack (already complete for recording): `docs/FILM-PACK-2026-09-03.md` · screenshots `docs/film/` · teleprompter `demo/FILM-AND-SUBMIT.md`.

---

## 6 · What this pack fixed so the stranger path is true

Same-subject corpus reuse (integrity `f61635e`) requires **exact assertion text**. Offline compound-mini Run B was still feeding paraphrased overlapping claims, so public `main` compound returned A=2→B=3 with corpus_hits=0 (watched red: `verify_cold_clone.sh` exit 3). This pack aligns Run B’s overlapping offline claims with Run A’s verbatim assertions; new third claim still searches. Re-run: A=2→B=1, corpus_hits=2, exit 0.

---

## 7 · Related artifacts

| Artifact | Path |
|----------|------|
| Devpost long paste | `submission/DEVPOST-PASTE.md` |
| Older field checklist | `docs/DEVPOST-READY.md` · `docs/SUBMISSION-PACK-2026-08-29.md` |
| Oscar submit checklist | `docs/OSCAR-SUBMIT-CHECKLIST-2026-08-31.md` |
| Overnight research receipt | `NIGHTRUN-2026-09-05.md` |
| Research quickstart | `docs/RESEARCH-QUICKSTART.md` |
| Use-bar session | `docs/USE-BAR-SESSION-TEMPLATE.md` |
| This run’s receipt | `docs/CLOUD-RECEIPT-cinema-pack-2026-09-05.md` |
