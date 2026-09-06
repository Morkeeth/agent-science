# FINDING — hosted stranger path RED · 2026-09-06

**Object opened:** live URL in pitch / SUBMISSION-PACK / `new_user_trial.sh`  
`https://agent-science-568004190078.us-central1.run.app`

**Not opened first (nearer proxies that would have lied):** STATUS.md claim of public desk, prior long-run receipts, Devpost "Try it" paste.

---

## What the object said

```bash
curl -sS https://agent-science-568004190078.us-central1.run.app/health
# {"ok": true, "service": "agent-science", "mode": "private-workspaces",
#  "revision": "agent-science-00026-zel"}

python3 scripts/probe_hosted_stranger_path.py
# HOSTED STRANGER PATH RED
# - mode=private-workspaces (legacy public /search /clear not exposed)
# - /search?q=2012/28/EU&live=false → HTTP 303 → …33kamss2jq…/search… (then /login)
# - /truths/ui, /visibility/ui, /registry, /popular/ui, /partners, /stats → same 303 pattern
```

`bash scripts/new_user_trial.sh` fails at step 1 (`KeyError: engine_default` before the honest BLOCKED patch; after patch → exit 2 BLOCKED).

Unauthenticated `POST /clear` on the canonical host returns **401** HTML error page (probe via curl 2026-09-06).

---

## Why this matters for Sep 9

Judge / stranger surfaces in the pack still say:

- Try `/visibility/ui?q=ralph+loop+agentic`
- Truths dashboard `/truths/ui` · 265+ claims
- `new_user_trial.sh` / `long_run_goal.sh` against the hosted URL

Those paths require **Sign in · Agent Science** on revision `agent-science-00026-zel`. A logged-out judge cannot run the killer demo from the pasted URL.

This matches the product ruling in `AGENTS.md` (Cloud Run serves private `/cases`; earlier `/search`/`/clear` are local-only) — but the **submit pack and pitch were not re-measured at the object** after that deploy.

---

## Control

`python3 scripts/probe_hosted_stranger_path.py --self-test` watches RED on planted private-workspaces + login, RED on outage/empty, GREEN only on planted public-desk JSON. Live probe exit 1 is the intended RED.

---

## What Oscar can do (outward / deploy — not this agent)

1. Film and paste **CLI / cold-clone** stranger path (no hosted try-it), **or**
2. Deploy a separate public exhibit surface (Oscar click; not this slice), **or**
3. Issue a judge workspace token and document sign-in — never put the token in a URL.

Do **not** claim hosted compound / free `/search` on the public URL until the probe goes GREEN.
