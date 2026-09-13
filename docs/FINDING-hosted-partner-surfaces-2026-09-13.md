# FINDING — Hosted partner verify was RED while docs said green · 2026-09-13

## Claim that failed

Prior receipts (`docs/RECEIPT-partner-night-2026-09-03.md`,
`docs/PARTNER-INTEGRATIONS-2026-08-30.md` last-verified 2026-09-03) stated all four
partners were live on the hosted URL with `engine_default: adk`.

## Object measured

```bash
curl -s https://agent-science-568004190078.us-central1.run.app/health | python3 -m json.tool
```

```json
{
  "ok": true,
  "service": "agent-science",
  "mode": "private-workspaces",
  "revision": "agent-science-00028-hed"
}
```

```bash
curl -s -o /dev/null -w '%{http_code}\n' \
  https://agent-science-568004190078.us-central1.run.app/partners
# 303
```

```bash
bash scripts/verify_partners_hosted.sh
# AssertionError: gemini: expected True, got None
```

## Mechanism

`cloud/service.py` routes **all** GET/POST to `WorkspaceHTTP` when `K_SERVICE` is set.
`WorkspaceHTTP` previously returned a minimal `/health` and treated `/partners` as an
unauthenticated GET → redirect to `/login`. Partner wiring still existed in code and in
the local desk path — but the **hosted judge surfaces** no longer proved it.

## Lesson (same family as PRIOR LOSS)

A nearer proxy (an old receipt, a local test suite, a PLAN checkbox) answered faster than
opening the live URL. Opening the URL was slower and was the only measurement that
mattered.

## Response shipped

Restore public partner `/health` + `/partners` under private-workspaces without reopening
unauthenticated `/clear` / `/search` (those stay local-only per AGENTS.md). Prove locally
tonight; Oscar deploy makes hosted match.
