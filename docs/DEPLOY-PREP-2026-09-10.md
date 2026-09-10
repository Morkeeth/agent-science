# Deploy prep — slice 1 (Oscar only) · 2026-09-10

**Script:** `deploy.sh` (45 lines) · **Do not run from cloud agent**

Pre-flight only. Deploy creates a **no-traffic candidate** tag (`workspace-candidate`) and
prints the revision for Oscar to promote after verify. It does not flip traffic by itself.

---

## What deploy.sh does now (read before click)

Measured at object: `wc -l deploy.sh` → **45**; tip commits
`0363a54` / `193c4d6` (private workspace runtime).

| Step | Action | Secret surface |
|------|--------|----------------|
| 1 | Require Secret Manager secrets already exist: `parallel-api-key`, `agent-science-workspace-access` | **no local key file upload in this script** |
| 2 | Ensure runtime SA `agent-science-workspace@…` + secretAccessor bindings | IAM |
| 3 | Ensure workspace bucket `gs://${PROJECT}-agent-science-workspaces` + objectUser | GCS |
| 4 | Pin **immutable** secret versions (latest ENABLED) | reproducibility |
| 5 | `gcloud run deploy … --no-traffic --tag=workspace-candidate` with `--set-secrets` only | Parallel + access config |
| 6 | Print `CANDIDATE_REVISION` + current traffic JSON | Oscar promotes later |

**Env set (no plaintext API keys):** `AGENT_SCIENCE_HOSTED=1`, public origin, allowed candidate origin, workspace bucket, daily/global research + mutation limits, research timeout 180s.

**Timeout:** **240s** (was 300s on older desk deploys — orphan-works full script still at risk of 504).

**Not in deploy.sh:** public repo flip · Devpost · video · npm publish · seeding local corpus/case DBs into cloud (comment in script: existing cloud state is never replaced).

---

## Diff vs DEPLOY-PREP-2026-09-03 (stale assumptions)

| 2026-09-03 prep said | 2026-09-10 object |
|----------------------|-------------------|
| Parallel key uploaded from `~/.config/keys/parallel.key` during deploy | Secrets must **already** exist; script only `secrets describe` + bind |
| `--clear-env-vars` then deploy with traffic | **No** clear-env; **no-traffic** candidate tag |
| Memory / desk shape implied | Explicit `--memory=512Mi --concurrency=1 --max-instances=3` |
| Hosted stranger `/search` public | Live health: `mode: private-workspaces` · `/search` → **sign-in** (303) |

---

## Pre-deploy (Oscar)

- [ ] Parallel + workspace-access secrets present and rotated if ever leaked in an old revision env
- [ ] `gcloud auth` + project `hack-fleet` (or `$GCP_PROJECT`)
- [ ] `AGENT_SCIENCE_PUBLIC_ORIGIN` set if service URL cannot be described yet
- [ ] Review `git log --oneline -5` on the branch you deploy
- [ ] Optional local gate: `bash scripts/full_gate.sh` (hosted long_run/stranger may fail under sign-in wall — expect that)

---

## Deploy command

```bash
cd agent-science
bash deploy.sh
```

Expected: `CANDIDATE_REVISION=…` and traffic JSON showing candidate with **0%** until you promote.

---

## Post-deploy verify (run each)

```bash
HOST=https://agent-science-568004190078.us-central1.run.app

curl -sf "$HOST/health" | python3 -m json.tool
# expect mode private-workspaces + revision bump

# Candidate origin (from deploy output):
# https://workspace-candidate---agent-science-….run.app
# Verify THERE before promoting traffic.
```

**Do not claim:** public logged-out `/search` compound until product mode restores a stranger path or workspace auth is in the film script.

**Do not claim:** full orphan-works script under 240s without a measured pass.

---

## Promotion (Oscar only — not in deploy.sh)

After candidate verify, promote the **exact** printed revision with gcloud traffic update. Do not redeploy “to promote.”
