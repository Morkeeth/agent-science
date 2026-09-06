# DEPLOY PREP — 2026-09-06 (Oscar only · do not run from cloud agent)

**Script:** `deploy.sh` (current tree)  
**Live revision probed:** `agent-science-00026-zel` · `mode=private-workspaces`  
**Canonical URL:** https://agent-science-568004190078.us-central1.run.app  
**Legacy alias:** https://agent-science-33kamss2jq-uc.a.run.app (303 target for non-health paths)

This checklist replaces assumptions in `docs/DEPLOY-PREP-2026-09-03.md` that still describe a public desk (`engine_default` on `/health`, unauthenticated `/search`, corpus seed). Diff the script before any click.

---

## What `deploy.sh` does now (read the file)

| Step | Action |
|------|--------|
| 1 | Require Secret Manager secrets `parallel-api-key` + `agent-science-workspace-access` |
| 2 | Ensure runtime SA `agent-science-workspace@…` + secret accessor IAM |
| 3 | Ensure GCS workspace bucket with **public-access-prevention** (no public corpus seed) |
| 4 | Deploy **no-traffic** candidate tag `workspace-candidate` with `--set-secrets` + workspace env |
| 5 | Print candidate revision + traffic JSON — **does not auto-promote** |

**Not in script:** `--clear-env-vars`, local `cache/*.db` upload, public `/search` restore, Devpost, video, npm publish.

Env set on deploy (names only): `AGENT_SCIENCE_HOSTED`, `AGENT_SCIENCE_PUBLIC_ORIGIN`, `AGENT_SCIENCE_ALLOWED_ORIGINS`, `AGENT_SCIENCE_WORKSPACE_BUCKET`, daily/global research + mutation limits, `AGENT_SCIENCE_RESEARCH_TIMEOUT`.

Secrets mounted: `PARALLEL_API_KEY`, `AGENT_SCIENCE_ACCESS_CONFIG`.

---

## Pre-click (Oscar)

- [ ] Read `deploy.sh` end-to-end — confirm no plaintext `--set-env-vars` for API keys
- [ ] Confirm Parallel + workspace-access secrets rotated if ever leaked in an old revision
- [ ] Decide **exhibit posture for Sep 9**:
  - **A.** Keep private-workspaces; film CLI/cold-clone; update Devpost try-it (already in FINDING)
  - **B.** Separate public exhibit service (new work — not this prep)
- [ ] `gcloud auth` + project `hack-fleet` (or `$GCP_PROJECT`)
- [ ] Set `AGENT_SCIENCE_PUBLIC_ORIGIN` if the describe URL is wrong

---

## Deploy command (Oscar machine only)

```bash
cd agent-science
bash deploy.sh
# Expect: CANDIDATE_REVISION=… and "without traffic"
# Promote only after acceptance — exact revision, Oscar click
```

---

## Post-deploy verify (do not tick without running)

```bash
HOST=https://agent-science-568004190078.us-central1.run.app

curl -sS "$HOST/health" | python3 -m json.tool
# expect mode=private-workspaces on current product spine

python3 scripts/probe_hosted_stranger_path.py --url "$HOST"
# expect RED while public stranger desk is absent — that is truth, not failure of the probe

bash scripts/new_user_trial.sh "$HOST"
# expect exit 2 BLOCKED on private-workspaces

# Workspace path (token required — never in URL):
# sign in at /login · exercise /cases — see docs/BUILD-HOSTED-CASES-2026-09-04.md
```

---

## Diff vs 2026-09-03 prep (stale claims)

| 2026-09-03 prep claimed | Object 2026-09-06 |
|-------------------------|-------------------|
| Post-deploy `/health` shows `engine_default: adk` | `/health` has `mode=private-workspaces` only |
| `new_user_trial.sh` should pass | BLOCKED / RED |
| `verify_partners_hosted.sh` / public compound | `/clear` unauthenticated → 401; paths 303→login |
| deploy clears env + seeds corpus | current `deploy.sh` does neither |

---

## If you need the old public killer demo on camera

That is a **product decision**, not a checklist tick. Options: film offline/cold-clone compound receipt, or build/promote a public exhibit revision. Do not paste try-it URLs that `probe_hosted_stranger_path.py` marks RED.
