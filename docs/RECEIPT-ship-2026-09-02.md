# RECEIPT — ship lane 2026-09-02

## AS-SHIP-2 · COLD-SCRIPTS

**Deliverable:** `docs/COLD-SCRIPTS.md`

**What:** Three public documentary transcripts (Ken Burns *Civil War* ep1 captions, NOVA *What's Up with the Weather?*, FRONTLINE *South Korea's Adoption Reckoning*) run through hosted `POST /clear` on fresh subjects. Sourced/refused/wrong counts recorded; wrong cases quoted.

**Measured (hosted, 2026-09-01 UTC):**

| Script | Claims | SOURCED | Refused | Wrong | Wall (s) | Parallel API |
|--------|--------|---------|---------|-------|----------|--------------|
| 1 Civil War | 10 | 1 | 9 | 9 | 268 | 11 |
| 2 NOVA climate | 3 | 0 | 3 | 3 | 164 | 2 |
| 3 Korea adoption | 3 | 0 | 3 | 3 | 114 | 5 |
| **Total** | **16** | **1** | **15** | **15** | **546** | **18** |

**Commands run:**

```bash
python3 cold-runs/run_clear.py cold-runs/scripts/script1-civil-war-historical-run.txt as-ship2-cold-hist-f4a1 cold-runs/receipts/script1.json
python3 cold-runs/run_clear.py cold-runs/scripts/script2-nova-climate-science-run.txt as-ship2-cold-sci-e2b7 cold-runs/receipts/script2.json
python3 cold-runs/run_clear.py cold-runs/scripts/script3-korea-adoption-policy-run.txt as-ship2-cold-pol-d3c8 cold-runs/receipts/script3.json
python3 cold-runs/audit_wrong.py
bash scripts/privacy_grep.sh
```

**Finding:** 15/16 extracted claims wrong for documentary clearance — transcript states the fact but product refused (web search miss or `no_independent_source` on PBS circular). Only C8 (Civil War last veteran 1959) sourced; span verified at citation object.

**Not done:** Product tuning (`clearance/verify.py` untouched per spec). Local `agent_science.py` not run (no keys in cloud agent VM; hosted path used).
