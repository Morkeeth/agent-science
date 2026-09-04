# BLOCKED — live compound exhibit · 2026-09-04

**Probe:** orphan-works A/B on hosted or local with Parallel + Gemini keys  
**Verdict:** **BLOCKED** — keys missing on this VM

---

## Key check (run at object)

```bash
test -n "${PARALLEL_API_KEY:-}" && echo PARALLEL=set || echo PARALLEL=missing
test -f ~/.config/keys/parallel.key && echo parallel.key=exists || echo parallel.key=missing
test -n "${GEMINI_API_KEY:-}" && echo GEMINI=set || echo GEMINI=missing
test -n "${GOOGLE_APPLICATION_CREDENTIALS:-}" && echo ADC=set || echo ADC=missing
```

**Output (2026-09-04T00:05Z, this VM):**

```
PARALLEL=missing
parallel.key=missing
GEMINI=missing
ADC=missing
```

---

## What was run instead (offline, no keys)

```bash
python3 scripts/compound_exhibit_receipt.py
# offline A=2 → B=1 Parallel · B corpus_hits=2
# writes docs/COMPOUND-EXHIBIT-2026-08-29.md
```

Hosted health (no key required for `/health`):

```bash
curl -sf https://agent-science-568004190078.us-central1.run.app/health | python3 -m json.tool
# ok=true · engine_default=adk · parallel=true · gemini=true on the service
```

Hosted service **has** keys; this agent VM does **not**. A live A/B from here would need Oscar's local keys or a deploy-side probe.

---

## Also blocked on hosted (even with keys)

Full orphan-works script: **504 Gateway Timeout @ 300s** — `docs/FINDING-orphan-works-timeout-2026-09-03.md`.  
`deploy.sh` line 73: `--timeout=300`. Oscar: raise timeout or film `compound_fresh_hosted_probe.py`.

---

## Unblock path (Oscar)

1. Place rotated Parallel key at `~/.config/keys/parallel.key`
2. ADC or `GEMINI_API_KEY` for local clearance
3. `python3 scripts/compound_fresh_hosted_probe.py` or local `POST /clear` A/B
4. Paste receipt numbers into `docs/RECEIPT-live-compound-exhibit-*.md`

Until then: offline compound receipt is authoritative for this wave.
