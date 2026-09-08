# Deploy prep — slice 1 (Oscar only) · refreshed 2026-09-08

**Script:** `deploy.sh` · **Do not run from cloud agent**

Pre-flight only. Deploy flips a live revision and touches Secret Manager — Oscar's click.

---

## What live hosted is NOW (measured, not remembered)

```bash
curl -sS https://agent-science-568004190078.us-central1.run.app/health | python3 -m json.tool
# {"ok": true, "service": "agent-science", "mode": "private-workspaces",
#  "revision": "agent-science-00026-zel"}
```

| Path | Unauthenticated result (2026-09-08) |
|------|-------------------------------------|
| `/health` | **200** JSON |
| `/search`, `/clear`, `/registry`, `/popular/ui`, `/visibility/ui`, `/truths/ui`, `/partners`, `/stats` | **303** → sign-in HTML |
| `/api/cases` | **401** workspace key required |
| `/cases` | sign-in form (access token) |

`deploy.sh` deploys the **private workspace** runtime (no local corpus seed, Secret Manager for Parallel + workspace access, candidate tag then promote). It does **not** restore the old public clearance desk.

---

## What deploy.sh does (read before click)

| Step | Action | Secret surface |
|------|--------|----------------|
| 1 | Require existing secrets `parallel-api-key` + `agent-science-workspace-access` | Oscar-rotated versions |
| 2 | Ensure runtime SA + workspace GCS bucket | IAM only |
| 3 | Deploy **no-traffic** candidate tag `workspace-candidate` | `--set-secrets` only — no plaintext env keys |
| 4 | Print candidate revision + traffic JSON | Oscar promotes after acceptance |

**Not in deploy.sh:** public repo flip · Devpost · video · npm publish · restoring public `/search`.

---

## Pre-deploy (Oscar)

- [ ] Parallel + workspace-access secret versions are the rotated ones (old plaintext Cloud Run env is historical)
- [ ] `gcloud auth` + project `hack-fleet` (or `$GCP_PROJECT`)
- [ ] Decide **submit narrative**:
  - **A.** Keep private workspaces — film cold-clone + signed-in `/cases` (matches current main)
  - **B.** Restore a public judge desk — separate product decision; current `deploy.sh` will not do it alone
- [ ] Review `git log --oneline -10` on `main` and `docs/BUILD-HOSTED-CASES-2026-09-04.md`

---

## Deploy command (candidate only)

```bash
cd agent-science   # local clone with gcloud
bash deploy.sh
# Expect: CANDIDATE_REVISION=… and traffic JSON showing candidate without 100% traffic
# Oscar promotes the exact revision after acceptance checks in BUILD-HOSTED receipt
```

---

## Post-deploy verify (private workspace path)

```bash
HOST=https://agent-science-568004190078.us-central1.run.app

curl -sf "$HOST/health" | python3 -m json.tool
# ok=true · mode=private-workspaces

# Expect 303/401 without token — do NOT treat as outage
curl -sS -o /dev/null -w '%{http_code}\n' "$HOST/search?q=test&live=false"
curl -sS -o /dev/null -w '%{http_code}\n' "$HOST/api/cases"

# With Oscar's workspace bearer (never put token in a URL):
# curl -sf -H "Authorization: Bearer $TOKEN" "$HOST/api/cases?page=1"
```

**Offline compound (always, keys optional):**

```bash
python3 scripts/seed_document_cache.py
python3 scripts/compound_exhibit_receipt.py
# A=2 → B=1 Parallel · corpus_hits B=2
```

**Do not claim:** unauthenticated hosted `/visibility/ui` or orphan-works full-script compound on public `/clear`.

---

## Diff notes (2026-09-08 night wave)

This wave fixes CELEX document-cache key collision (`%3A` vs `:`), restores offline compound under exact-claim integrity, refreshes SUBMISSION-PACK hosted truth, and adds `scripts/eval_artifact_claims.py`. Runtime change in `clearance/instruments.py` affects any deployment that serves document cache lookups — safe and corrective.

---

## If deploy fails

| Symptom | Check |
|---------|-------|
| Secret access denied | Runtime SA `secretAccessor` on both secrets |
| Candidate never promoted | Oscar must shift traffic to the printed revision |
| Judges hit sign-in on old desk URLs | Expected on `private-workspaces` — update Devpost links |
| 504 on research | `AGENT_SCIENCE_RESEARCH_TIMEOUT` (180s in deploy.sh) |
