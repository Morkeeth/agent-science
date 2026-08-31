# Deploy click list · 2026-09-01

**Oscar only.** Cloud agents do not run this.

## Pre-flight

```bash
cd ~/CODE/cleared
git checkout main && git pull
bash scripts/full_gate.sh
```

## Deploy

```bash
./deploy.sh
```

Script: `deploy.sh` — Cloud Run `agent-science` in `hack-fleet` / `us-central1`.

## Post-deploy verify (logged-out or curl)

```bash
BASE=https://agent-science-568004190078.us-central1.run.app
curl -s "$BASE/health" | python3 -m json.tool
curl -s "$BASE/truths/ui" | head -20
curl -s "$BASE/popular/ui" | head -20
python3 -m clearance.stack_cli visibility "ralph loop" --full  # local CLI unchanged
```

## New routes this shape

| Route | Purpose |
|-------|---------|
| `/truths/ui` | Popular truths + field ★ strip |
| `/popular/ui` | Fleet query rank (existing) |

Desk nav now links `/truths/ui` from home.

## Do not

- Put API keys in `--set-env-vars` (use Secret Manager per `deploy.sh`)
- Deploy without `full_gate.sh` OK on the commit being deployed
