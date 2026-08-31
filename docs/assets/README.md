# Visual assets — Agent Science

Architecture diagrams and hosted UI screenshots for judges, Devpost, and onboarding.

## Diagrams

| File | Description |
|------|-------------|
| [diagram-system-overview.png](./diagram-system-overview.png) | High-level system — users, Cloud Run, engine, partners, stores |
| [diagram-clearance-flow.png](./diagram-clearance-flow.png) | POST /clear per-claim pipeline |

Source-of-truth diagrams (editable): [ARCHITECTURE.md](../ARCHITECTURE.md) — Mermaid blocks render on GitHub.

## Screenshots (hosted)

Captured from https://agent-science-568004190078.us-central1.run.app

| File | Route | What it shows |
|------|-------|---------------|
| [screens/01-desk-home.png](./screens/01-desk-home.png) | `/` | Clearance desk — paste script form |
| [screens/02-front-wedge.png](./screens/02-front-wedge.png) | `/front` | Refusal wedge + compounding curve |
| [screens/03-registry-shelf.png](./screens/03-registry-shelf.png) | `/registry` | Browsable truth shelf |
| [screens/04-registry-search.png](./screens/04-registry-search.png) | `/registry?q=2012/28/EU` | EU directive registry hit |
| [screens/05-popular-ui.png](./screens/05-popular-ui.png) | `/popular/ui` | Dev query analytics |
| [screens/06-partners-json.png](./screens/06-partners-json.png) | `/partners` | Partner track manifest |

## Regenerate

```bash
# Screenshots (requires playwright + chromium)
python3 -m playwright install chromium
python3 scripts/capture_screens.py

# Optional: different host
python3 scripts/capture_screens.py http://localhost:8080
```

Diagram PNGs are generated for Devpost/README; update by re-running GenerateImage or exporting Mermaid from ARCHITECTURE.md.
