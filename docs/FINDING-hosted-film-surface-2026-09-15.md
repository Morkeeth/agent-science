# FINDING — Hosted film surfaces ≠ local desk · 2026-09-15

## Object

```bash
curl -sL https://agent-science-568004190078.us-central1.run.app/visibility/ui?q=ralph+loop+agentic
curl -sL https://agent-science-568004190078.us-central1.run.app/truths/ui
curl -s  https://agent-science-568004190078.us-central1.run.app/health
curl -s  https://agent-science-568004190078.us-central1.run.app/partners
curl -sL https://agent-science-568004190078.us-central1.run.app/judge/demo
```

## What the objects say (revision `agent-science-00028-hed`)

| URL | Live result |
|-----|-------------|
| `/health` | Thin `{ok,service,mode,revision}` — **no partner fields** |
| `/partners` | Login HTML (not track JSON) |
| `/visibility/ui` | Public entry stub: **"local-only research route"** — no Transparency pane |
| `/truths/ui` | Same local-only notice — no truths dashboard |
| `/judge/demo` | Public read-only evidence example (works) |

## Why this matters

`docs/PITCH-TOMORROW.md` and `film/preflight.sh` (pre-fix) treated hosted `/visibility/ui` as the film WOW. Opening the URL shows that surface was retired when Cloud Run moved to private workspaces. Filming the hosted URL for "Transparency pane" would be a wrong-object demo.

## Naive arm vs shipping arm

- **Naive:** keep film preflight grepping `Transparency` on hosted → false film path; thin `/health` still "ok:true".
- **Shipping (this branch):** partner `/health`+`/partners` must be public JSON; film checks `/judge/demo` + local-only notices; restore partner fields in `cloud/case_http.py` for Oscar deploy.

## Film instruction (Oscar)

1. Partner proof: hosted `/health` after deploy (`engine_default: adk`, `parallel_sdk: true`).
2. Product story on camera: local desk `python3 cloud/service.py` → `/visibility/ui`, **or** hosted `/judge/demo`.
3. Do not claim hosted `/visibility/ui` still shows the transparency WOW.
