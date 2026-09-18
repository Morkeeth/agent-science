# FINDING — "265+ claims" was stale · 2026-09-18

**Claim in circulation:** Devpost paste / STATUS / overnight receipts say the shelf holds
**265** claims (hit rate ~0.80).

**Object measured tonight:**

```bash
python3 scripts/boot_registry.py
python3 -c 'from clearance import refusal_log as r; print(r.stats(r.connect(r.DB))["n"])'
# → 239
```

`boot_registry.py` backfill: verified SOURCED **25** · UNSOURCED **215** · UNKNOWN **72** of
**312** corpus rows → registry **239** claims (25 sourced · 214 refused).

**Hosted `/stats` and `/truths/ui`:** both **HTTP 303** (auth wall under private-workspaces) —
cannot re-read the Sept 1 hosted 265 figure from the public URL tonight.

**Correction:** treat **239** as the cold-clone / boot_registry denominator on this tree.
The "265+" line in the Devpost paste was a carried number from
`docs/RECEIPT-overnight-2026-09-01.md` (hosted shelf that day), not re-derived at submit pack
refresh. Fixed in `docs/SUBMISSION-PACK-2026-08-29.md` and `docs/STATUS.md` on 2026-09-18.
