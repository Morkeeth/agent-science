# Deploy prep — 2026-09-11 (Oscar only)

**Script:** `deploy.sh` · **Do not run from cloud agent**

This checklist matches the **current** `deploy.sh` on `main` (private workspace runtime). It supersedes `docs/DEPLOY-PREP-2026-09-03.md` for the deploy click; that older note described a public desk deploy that is no longer what the script does.

---

## What deploy.sh does now (read before click)

| Step | Action | Secret / risk |
|------|--------|----------------|
| 1 | Require existing Secret Manager secrets `parallel-api-key` and `agent-science-workspace-access` | Secrets must already exist — script does **not** upload from `~/.config/keys` |
| 2 | Ensure runtime SA `agent-science-workspace@…` + secret accessor IAM | |
| 3 | Ensure workspace bucket `gs://${PROJECT}-agent-science-workspaces` with public-access-prevention | **No local corpus/case seed** — existing cloud state is never replaced |
| 4 | Deploy **candidate** revision with `--no-traffic --tag=workspace-candidate` | Atomic; does not clear live traffic |
| 5 | Pin immutable secret versions into `--set-secrets` | Parallel + access config only |
| 6 | Print `CANDIDATE_REVISION` + traffic JSON | Oscar promotes traffic only after verify |

**Env set by deploy:** `AGENT_SCIENCE_HOSTED=1`, public/allowed origins, workspace bucket, daily research/mutation limits, research timeout 180s. **Timeout on service:** 240s (orphan-works full script previously 504 @ 300s — still not claimed).

**Not in deploy.sh:** public repo flip · Devpost · video · npm publish · promoting traffic · seeding local DBs.

---

## Diff vs last desk-era deploy notes

- Old prep assumed `--clear-env-vars` + public `/search` `/clear` desk. **Gone.**
- Live `/health` (2026-09-11): `{"ok": true, "mode": "private-workspaces", "revision": "agent-science-00028-hed"}` — no `engine_default` / partner flags on the anonymous health body.
- Anonymous stranger routes (`/search`, `/partners`, `/registry`, `/popular/ui`) → workspace **login**. Film and Devpost must not claim otherwise.

---

## Pre-deploy (Oscar)

- [ ] Confirm Secret Manager has rotated Parallel key if any old revision ever had plaintext env
- [ ] Confirm `agent-science-workspace-access` secret is the intended access-config version
- [ ] `gcloud auth` + project `hack-fleet` (or `$GCP_PROJECT`)
- [ ] Set `AGENT_SCIENCE_PUBLIC_ORIGIN` if `gcloud run services describe` URL is wrong
- [ ] Review `git log --oneline -10` on the commit you deploy
- [ ] Read `docs/RECEIPT-night-wave-2026-09-11.md` — hosted claim failures already measured

---

## Deploy command (candidate only)

```bash
cd agent-science   # local clone with gcloud
bash deploy.sh
```

Expected: `CANDIDATE_REVISION=…` and a note that the candidate has **no traffic** until you promote that exact revision.

---

## Post-candidate verify (before traffic)

```bash
HOST=https://agent-science-568004190078.us-central1.run.app
# or the workspace-candidate tagged URL printed by Cloud Run

curl -sS "$HOST/health" | python3 -m json.tool
# expect mode=private-workspaces

# With a workspace bearer token (never in a URL):
#   curl -sS -H "Authorization: Bearer $TOKEN" "$HOST/api/cases" …

python3 scripts/eval_artifact_claims.py
# shipping must still refuse anonymous /search /partners pack claims if those stay gated
```

**Do not claim:** anonymous hosted compound, `/visibility/ui` CONTRARY desk, or orphan-works full-script A/B under 240s timeout.

---

## If deploy fails

- Missing secret → create/rotate in console (Oscar), re-run
- Wrong origin → set `AGENT_SCIENCE_PUBLIC_ORIGIN`
- Do not remove generation preconditions or seed from local user data to "fix" a conflict
