# Deploy prep — 2026-09-16 (Oscar only)

**Script:** `deploy.sh` · **Do not run from cloud agent**  
**Live today:** rev `agent-science-00028-hed` · `mode=private-workspaces` ·
canonical URL https://agent-science-568004190078.us-central1.run.app
(redirects app pages to `https://agent-science-33kamss2jq-uc.a.run.app/…`)

This is a pre-flight checklist. Deploy creates a **candidate revision with no
traffic** (`--no-traffic --tag=workspace-candidate`). Promote is a separate Oscar click.

---

## What deploy.sh does now (read before click)

Diff vs older desk-style deploys (measured by reading `deploy.sh` on this branch):

| Step | Action | Secret surface |
|------|--------|----------------|
| 1 | Require existing Secret Manager secrets `parallel-api-key` + `agent-science-workspace-access` | no local key file read |
| 2 | Ensure runtime SA `agent-science-workspace@…` + secret accessor IAM | |
| 3 | Ensure workspace bucket with public-access-prevention | GCS |
| 4 | `gcloud run deploy … --no-traffic --tag=workspace-candidate` | `--set-secrets` only |
| 5 | Print `CANDIDATE_REVISION` + current traffic JSON | **does not promote** |

**Not in deploy.sh:** public repo flip · Devpost · video · npm publish · traffic promote · key rotation.

---

## Pre-deploy (Oscar)

- [ ] Parallel key rotated if any old revision ever had plaintext `PARALLEL_API_KEY` env
- [ ] Secret Manager versions for `parallel-api-key` and `agent-science-workspace-access` are the intended ones
- [ ] `gcloud auth` + project `hack-fleet` (or `$GCP_PROJECT`)
- [ ] Confirm `AGENT_SCIENCE_PUBLIC_ORIGIN` or existing Cloud Run URL
- [ ] Review `git log --oneline origin/main..HEAD` / PR diff — tonight's wave is docs + offline evals + compound-mini-B exact-match text; no hosted Python path change required for compound truth alone

---

## Deploy command (candidate only)

```bash
cd agent-science   # local clone with gcloud
bash deploy.sh
```

Expected: `CANDIDATE_REVISION=…` and a reminder that traffic is unchanged.

**Promote (separate Oscar command — not in deploy.sh):** only after candidate health + login + judge/demo checks.

---

## Post-candidate verify (run each)

```bash
HOST=https://agent-science-568004190078.us-central1.run.app

curl -sf "$HOST/health" | python3 -m json.tool
# expect mode private-workspaces

curl -sL -o /dev/null -w "%{http_code} %{url_effective}\n" "$HOST/judge/demo"
# 200 …/judge/demo

curl -sL -o /dev/null -w "%{http_code} %{url_effective}\n" "$HOST/search"
# expect …/login while unauthenticated
```

Live compound still needs keys + workspace auth — see
`docs/RECEIPT-live-compound-blocked-2026-09-16.md`.

---

## Diff notes (2026-09-16 night wave)

Safe without deploy for submit-path docs/evals:

- `scripts/compound_exhibit_receipt.py` · `fixtures/scripts/compound-mini-B.txt`
- `scripts/eval_compound_paraphrase.py` · `scripts/eval_cost_gate.py`
- `docs/SUBMISSION-PACK-2026-08-29.md` · findings · receipts · `hack.md`

Deploy only if Oscar needs a new candidate for video/hosting reasons.
