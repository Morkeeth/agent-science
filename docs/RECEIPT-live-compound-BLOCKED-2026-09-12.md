# RECEIPT — live compound exhibit BLOCKED · 2026-09-12

**Attempted:** orphan-works A/B on hosted or local with Gemini + Parallel  
**Outcome:** **BLOCKED** — missing keys; hosted public search retired

---

## Keys at object

```bash
test -n "$PARALLEL_API_KEY" && echo set || echo PARALLEL=missing
test -n "$GEMINI_API_KEY" && echo set || echo GEMINI=missing
test -f ~/.config/keys/parallel.key && echo parallel.key=exists || echo parallel.key=missing
test -f ~/.config/keys/gemini.key && echo gemini.key=exists || echo gemini.key=missing
```

**Result (this VM, 2026-09-12):** `PARALLEL=missing` · `GEMINI=missing` · both key files missing.

---

## Hosted probe (no auth)

```bash
curl -sf https://agent-science-568004190078.us-central1.run.app/health
# → {"ok": true, "service": "agent-science", "mode": "private-workspaces",
#     "revision": "agent-science-00028-hed"}

curl -sI https://agent-science-568004190078.us-central1.run.app/search
# → HTTP/2 501
curl -sI https://agent-science-568004190078.us-central1.run.app/partners
# → HTTP/2 501
```

Unauthenticated `/search`, `/clear`, `/ingest`, `/partners` are **local-only** under the private-workspaces runtime. A live compound POST from this agent without a workspace bearer token is not available.

---

## Authoritative offline stand-in

```bash
python3 scripts/compound_exhibit_receipt.py
# A=2 → B=1 Parallel (claims-searched), corpus_hits B=2, exit 0
python3 scripts/eval_compound_cost_arms.py
# EXACT pass · PARAPHRASE/NAIVE fail · price card 2026-09-12
```

Receipt: `docs/COMPOUND-EXHIBIT-2026-08-29.md` · arms: `docs/RECEIPT-night-wave-2026-09-12.md`

---

## Oscar unlock

1. Place rotated keys in `~/.config/keys/` (console rotation — never commit)
2. Either run local live `scripts/compound_exhibit.py`, or POST `/api/cases` with workspace bearer + `request_id`
3. Do not claim orphan-works full-script hosted compound until timeout/504 is re-measured under current timeout (deploy.sh `--timeout=240`)
