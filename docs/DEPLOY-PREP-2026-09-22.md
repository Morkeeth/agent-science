# DEPLOY PREP — partner admissibility + private-workspaces · 2026-09-22

**Script:** `deploy.sh` (45 lines) · **Do not run from cloud agent** · Oscar click only

Measured live before this note:

```bash
curl -sS https://agent-science-568004190078.us-central1.run.app/health | python3 -m json.tool
```

→ revision `agent-science-00028-hed`, keys only `ok/service/mode/revision` — partner fields still stripped
(`docs/FINDING-hosted-health-partner-strip-2026-09-16.md`). Fix is in tree; live stays RED until deploy.

---

## What deploy.sh actually does (read the file — do not trust older prep)

| Step | Action |
|------|--------|
| 1 | Require Secret Manager secrets `parallel-api-key` + `agent-science-workspace-access` already exist |
| 2 | Ensure runtime SA `agent-science-workspace@…` + IAM on secrets + workspace bucket |
| 3 | Pin **immutable** secret versions (no implicit rotation) |
| 4 | `gcloud run deploy … --no-traffic --tag=workspace-candidate` with `AGENT_SCIENCE_HOSTED=1` + workspace bucket env |
| 5 | `--set-secrets` only for Parallel + access config — **no** `--set-env-vars` plaintext keys |
| 6 | Print `CANDIDATE_REVISION` — traffic is **not** flipped automatically |

**Not in deploy.sh:** public repo · Devpost · video · npm · promoting candidate to 100% traffic.

Diff vs `docs/DEPLOY-PREP-2026-09-03.md`: that note described `--clear-env-vars` + corpus seed. Current `deploy.sh` is private-workspaces candidate deploy with no local corpus seed (comment: "No local corpus/case data is seeded").

---

## Pre-deploy (Oscar)

- [ ] Key rotation done if any old revision held plaintext Parallel/Gemini (`AS-KEYS-ROTATE`)
- [ ] `gcloud auth` + project `hack-fleet` (or `$GCP_PROJECT`)
- [ ] Secrets `parallel-api-key` and `agent-science-workspace-access` ENABLED versions exist
- [ ] Merge/push the partner `health_payload()` restore on the branch you deploy from
- [ ] Local prove already green: `bash scripts/prove_partner_health_local.sh`

---

## Deploy command (Oscar)

```bash
cd agent-science
bash deploy.sh
# expect: CANDIDATE_REVISION=… and "without traffic"
# then promote that exact revision when verified
```

---

## Post-deploy verify (run each at the object)

```bash
HOST=https://agent-science-568004190078.us-central1.run.app

curl -sS "$HOST/health" | python3 -m json.tool
# must include: engine_default, gemini, parallel, agent_builder

curl -sSL "$HOST/partners" | python3 -m json.tool
# JSON manifest, not Sign-in HTML

bash scripts/verify_partners_hosted.sh
# fail if health still stripped

python3 scripts/eval_artifact_claims.py
# AC1/AC2/AC3 gold may need re-label after deploy succeeds — that is the point
```

**Do not claim:** anonymous `/visibility/ui` panel or `/stats` claim counts until those routes are public again; private-workspaces intentionally gates research surfaces.

---

## Why this deploy matters for Sep 9 submit path

Artifact-claims gate (`scripts/eval_artifact_claims.py`, 2026-09-22) measured: trusting STATUS/SUBMISSION-PACK without opening hosted objects scored **4/10**; always-refuse null scored **6/10**. Partner health strip is one of those false-HELD docs. Deploy is the object-level fix; docs refresh alone is not.
