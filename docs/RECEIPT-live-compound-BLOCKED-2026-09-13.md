# BLOCKED — live compound exhibit · 2026-09-13

**Status:** BLOCKED · **Owner:** needs Oscar keys or hosted workspace bearer  
**Not a pass. Do not claim live A/B on video from this receipt.**

---

## What was attempted

```bash
test -n "${PARALLEL_API_KEY:-}" && echo PARALLEL=set || echo PARALLEL=missing
test -n "${GEMINI_API_KEY:-}" && echo GEMINI=set || echo GEMINI=missing
ls ~/.config/keys/ 2>/dev/null || echo 'no ~/.config/keys'
python3 -c "from scripts.compound_exhibit_receipt import _has_keys; print('has_keys', __import__('scripts.compound_exhibit_receipt', fromlist=['_has_keys']))" 2>/dev/null || true
```

**Result (this VM, 2026-09-13):** `PARALLEL_API_KEY` unset · `GEMINI_API_KEY` unset · no `~/.config/keys/` · `_has_keys()` → false → offline path only.

---

## Hosted surface (measured, not assumed)

```bash
HOST=https://agent-science-568004190078.us-central1.run.app
curl -sf "$HOST/health"
# {"ok": true, "service": "agent-science", "mode": "private-workspaces",
#  "revision": "agent-science-00028-hed"}

curl -sS -o /dev/null -w "%{http_code}\n" "$HOST/search"
# 303

curl -sS -L "$HOST/search" | head -c 120
# <!doctype html>… <title>Sign in · Agent Science</title>
```

Unauthenticated `/search`, `/partners`, `/registry`, `/visibility/ui` all **303 → Sign-in**.  
Earlier night receipts that said **501** were **wrong at today's object**.

Live orphan-works A/B on hosted therefore requires a workspace bearer (never in URL) and is out of scope for this keyless VM.

---

## Authoritative stand-in

Offline compound (no keys):

```bash
python3 scripts/compound_exhibit_receipt.py
# A=2 → B=1 Parallel · corpus_hits B=2 · exit 0
```

Baseline arms proving why paraphrase fails:

```bash
python3 scripts/eval_compound_cost_arms.py
# NAIVE NO · PARAPHRASE NO · EXACT YES
```

---

## Unblock (Oscar)

1. Provide rotated Parallel + Gemini keys on a machine that may hold them, **or**
2. Authenticated hosted workspace session with bearer for `/cases` research clear path
3. Re-run live compound; replace this BLOCKED file with a dated PASS receipt
4. Do not paste keys into the public repo
