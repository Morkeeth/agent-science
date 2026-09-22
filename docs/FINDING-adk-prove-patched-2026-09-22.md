# FINDING — local ADK prove was patched green · 2026-09-22

**Object:** `bash scripts/prove_partner_health_local.sh` (pre-fix tree on `main` @ `d56aeb8`)

**Command that exposed it:**

```bash
# Before install: real import is false
python3 -c "from cloud import agent; print(agent.adk_available(), agent.adk_version())"
# → False None

# Old prove still printed PROVE_PARTNER_HEALTH_LOCAL OK with engine_default=adk
# because it wrapped the server in:
#   patch("cloud.agent.adk_available", return_value=True)
#   patch("cloud.agent.adk_version", return_value="2.7.1")
```

**Why this is a false-green class defect:** the done-when for slice 5 / partner
admissibility said "local prove → engine_default=adk". A patched prove answers
"does the HTTP shape look right if ADK were present?", not "is Agent Builder on
the path in this checkout?". Cold clone + `verify_cold_clone.sh` step 10 inherited
the silent patch.

**Related live defect (still RED):** hosted revision `agent-science-00028-hed`
`/health` returns only `ok/service/mode/revision`. Measured:

```bash
curl -sS https://agent-science-568004190078.us-central1.run.app/health | python3 -m json.tool
# keys: mode, ok, revision, service — no gemini/parallel/engine_default
```

`/partners` returns **HTTP 303** to the run.app alias (then login), not the track
manifest. Measured without following redirects.

**External baseline (PeriodCheck, opened at object — not their README):**

```bash
curl -sS https://periodcheck-697827662390.us-central1.run.app/api/health | python3 -m json.tool
# {"status": "ready", "service": "periodcheck"}
```

Their health is also liveness-only. They win first-run UX + `live-evaluation.json`
(13/13 gold at their repo object). Health partner fields are **our** bar, not
theirs — and we currently fail our own bar on the live URL.

**Fix in tree (this session):**

1. `prove_partner_health_local.sh` — real ADK import by default; exit 3 if missing;
   `PROVE_ALLOW_ADK_PATCH=1` only for cold-clone shape, stamps `prove_mode`.
2. `scripts/partner_admissibility_gate.py` — three arms (naive / fields / unpatched)
   + PeriodCheck baseline; exit 2 while hosted RED and local OK.
3. `verify_partners_hosted.sh` — fail on non-200 `/partners` (no redirect follow).
4. `tests/test_partner_admissibility_gate.py` — watches A-pass/B-fail on stripped body.

**Still Oscar:** `deploy.sh` then `bash scripts/verify_partners_hosted.sh` and
`python3 scripts/partner_admissibility_gate.py` expecting exit 0.
