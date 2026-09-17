# Deploy prep — 2026-09-17 (Oscar only · do not run from cloud agent)

**Script:** `deploy.sh` (45 lines) · **Live revision now:** `agent-science-00028-hed`  
**Do not deploy from this agent.** Outward act = Oscar's click.

---

## What current deploy.sh actually does (read the file)

Diff vs older prep docs: this is **not** the `--clear-env-vars` + public desk flow anymore.

| Step | Action | Risk |
|------|--------|------|
| 1 | Require Secret Manager secrets `parallel-api-key` + `agent-science-workspace-access` already exist | Fail closed if missing — good |
| 2 | Ensure runtime SA `agent-science-workspace@…` + secret accessor IAM | |
| 3 | Ensure GCS bucket `$PROJECT-agent-science-workspaces` + objectUser | **No local corpus seed** (comment in script) |
| 4 | Pin **enabled** secret versions by createTime | Immutable versions — no implicit rotation |
| 5 | `gcloud run deploy … --no-traffic --tag=workspace-candidate` | Candidate only — **does not flip live traffic** |
| 6 | Print `CANDIDATE_REVISION` + traffic JSON | Oscar must promote separately |

Env set on candidate: `AGENT_SCIENCE_HOSTED=1`, public origin, allowed origins, workspace bucket, research/mutation limits, timeout 180s research.  
Secrets: `PARALLEL_API_KEY`, `AGENT_SCIENCE_ACCESS_CONFIG` only — **no plaintext `--set-env-vars` keys**.

**Timeout note:** Cloud Run `--timeout=240` on the service. Prior orphan-works full script hit **504 @ 300s** on older revs — do not film full orphan-works until measured under this budget; use compound-fresh / compound-mini.

---

## Why deploy matters tonight (measured live)

```bash
curl -sS https://agent-science-568004190078.us-central1.run.app/health
# revision agent-science-00028-hed — keys: ok, service, mode, revision ONLY
# gemini / parallel / engine_default ABSENT  → partner verify RED
# Finding: docs/FINDING-hosted-health-partner-strip-2026-09-16.md
# Fix already on main tree (cloud.partners.health_payload) — not on live traffic
```

`/partners`, `/stats`, `/search` return **303** (private-workspaces). Public partner proof lands only after a revision that restores `/health` + `/partners` before auth is **promoted**.

---

## Pre-deploy checklist (Oscar)

- [ ] Parallel + Gemini keys rotated in console if any old revision ever held plaintext (`AS-KEYS-ROTATE`)
- [ ] Secret Manager versions for `parallel-api-key` and `agent-science-workspace-access` are the rotated ones
- [ ] `gcloud auth` + project `hack-fleet` (or `$GCP_PROJECT`)
- [ ] Review `git log --oneline origin/main -10` — confirm partner-health commit is on the tip you deploy
- [ ] Read `deploy.sh` end-to-end once — candidate tag, no traffic flip

---

## Deploy + promote (Oscar clicks)

```bash
cd agent-science
bash deploy.sh
# Expect: CANDIDATE_REVISION=…  and traffic JSON showing workspace-candidate with 0% or tagged

# After manual verify on the candidate URL:
#   gcloud run services update-traffic agent-science --region=us-central1 \
#     --to-revisions=<CANDIDATE_REVISION>=100
# (exact promote command is Oscar's — do not paste secrets)
```

---

## Post-promote verify (each command)

```bash
HOST=https://agent-science-568004190078.us-central1.run.app

curl -sf "$HOST/health" | python3 -m json.tool
# MUST show engine_default / gemini / parallel (or equivalent partner payload)

bash scripts/verify_partners_hosted.sh
# fail closed if health still stripped

# With WORKSPACE_TOKEN only:
# python3 scripts/compound_fresh_hosted_probe.py
```

**Do not claim:** full orphan-works hosted A/B until a timed run completes under the service timeout.

---

## Diff notes (tree vs live `00028-hed`)

In tree, not yet on live traffic (re-check with `git log` before click):

- Partner health payload restore (`cloud/case_http.py` + `cloud.partners`)
- Offline compound exact-assertion fix
- Tonight: cost-from-billing gate · compound receipt sourced-count fix · pack refresh

Safe to deploy as docs + controls + prior partner fix; still Oscar-only.
