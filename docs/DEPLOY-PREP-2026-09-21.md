# Deploy prep — slice 1 (Oscar only) · 2026-09-21

**Script:** `deploy.sh` (45 lines) · **Do not run from cloud agent**

This is a pre-flight checklist. Deploy creates a **no-traffic** candidate revision tagged
`workspace-candidate` and touches Secret Manager — Oscar's click only.

---

## Live object (probed 2026-09-21, before deploy)

```bash
curl -sS https://agent-science-568004190078.us-central1.run.app/health | python3 -m json.tool
```

```json
{
  "ok": true,
  "service": "agent-science",
  "mode": "private-workspaces",
  "revision": "agent-science-00028-hed"
}
```

**Missing on live:** `gemini`, `parallel`, `engine_default` — stripped health. Fix is already
in tree (`cloud.partners.health_payload`); it is not on this revision.
See `docs/FINDING-hosted-health-partner-strip-2026-09-16.md`.

`POST /clear` without workspace bearer → **401**. `/partners` and `/stats` → **303**.

---

## What deploy.sh does now (read the file — do not trust older prep docs)

| Step | Action | Secret surface |
|------|--------|----------------|
| 1 | `gcloud secrets describe` Parallel + workspace-access secrets | must already exist |
| 2 | Ensure runtime SA `agent-science-workspace@…` + secretAccessor | IAM |
| 3 | Ensure GCS bucket `${PROJECT}-agent-science-workspaces` + objectUser | IAM |
| 4 | Pin **enabled** secret versions (immutable) | Secret Manager versions |
| 5 | `gcloud run deploy --source .` · `--memory=512Mi` · **`--timeout=240`** · **`--no-traffic`** · `--tag=workspace-candidate` | |
| 6 | `--set-secrets=PARALLEL_API_KEY=…,AGENT_SCIENCE_ACCESS_CONFIG=…` | **no plaintext keys** |
| 7 | `--set-env-vars` for hosted mode, origins, bucket, rate limits, research timeout 180 | no API keys |
| 8 | Print `CANDIDATE_REVISION` + current traffic JSON | Oscar promotes manually |

**Diff vs DEPLOY-PREP-2026-09-03 (stale — do not follow that file):**

- No `--clear-env-vars`
- No seeding local `cache/*.db` into the service
- No plaintext `GEMINI_API_KEY` / `PARALLEL_API_KEY` via `--set-env-vars`
- Timeout is **240s** (orphan-works full script previously **504 @ 300s** — still may need a higher timeout + traffic promote after candidate verify)
- Candidate ships **without traffic**; promotion is a separate Oscar step

**Not in deploy.sh:** public repo flip (already public) · Devpost · video · npm publish · key rotation at aistudio/parallel console.

---

## Pre-deploy (Oscar)

- [ ] Rotate Parallel + Gemini keys at provider consoles if any old Cloud Run revision ever had plaintext (`AS-KEYS-ROTATE`)
- [ ] Confirm Secret Manager secrets `parallel-api-key` and `agent-science-workspace-access` hold the rotated values
- [ ] `gcloud auth` + project `hack-fleet` (or `$GCP_PROJECT`)
- [ ] Review `git log --oneline origin/main -10` includes partner-health fix + tonight's cost/artifact gates
- [ ] Decide timeout: keep 240, or raise before film of full orphan-works script
- [ ] Optional: export Parallel invoice → `fixtures/billing/invoice.json` so cost gate billing row can go GREEN

---

## Deploy command (candidate only)

```bash
cd agent-science   # local clone with gcloud
bash deploy.sh
```

Expected: `CANDIDATE_REVISION=…` and traffic JSON still pointing at the previous live revision.

---

## Post-candidate verify (before promote)

```bash
HOST=https://agent-science-568004190078.us-central1.run.app
CAND=https://workspace-candidate---agent-science-568004190078.us-central1.run.app

curl -sf "$CAND/health" | python3 -m json.tool
# expect: gemini, parallel, engine_default: adk, mode: private-workspaces

curl -sf "$CAND/partners" | python3 -m json.tool

# With WORKSPACE_TOKEN only:
bash scripts/verify_partners_hosted.sh
```

## Promote (Oscar — separate click)

Only after candidate health shows partner fields:

```bash
# exact gcloud traffic update for the printed CANDIDATE_REVISION — Oscar runs it
```

Then:

```bash
curl -sf "$HOST/health" | python3 -m json.tool   # partner fields on live
bash scripts/new_user_trial.sh "$HOST"
python3 scripts/eval_artifact_claims.py          # AC1–AC5 golds may flip TRUE after deploy
```

**Do not claim:** full orphan-works script compound on hosted until Run A/B complete under the deployed timeout.

---

## Why this prep exists tonight

Night wave 2026-09-21 did **not** deploy. It re-probed live `00028-hed` (still stripped),
confirmed `deploy.sh` still matches the 2026-09-19 prep shape, and left promotion to Oscar.
