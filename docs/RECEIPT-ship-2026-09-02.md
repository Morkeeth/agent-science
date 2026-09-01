# Ship receipt — 2026-09-02

---

## AS-SHIP-2 · COLD-SCRIPTS · public documentary cold runs

**Branch:** `cursor/cold-scripts-cfca`  
**Deliverable:** `docs/COLD-SCRIPTS.md`

### Shipped

- Three public documentary transcripts in `cold-scripts/` (Apollo ALSJ, PBS NOVA, EUR-Lex orphan works)
- Live clearance receipts for subjects `cold-script-1` … `cold-script-3`
- `scripts/run_cold_scripts.py` — batch hosted runner
- `scripts/audit_cold_wrong.py` — wrong-case audit at source URLs
- `docs/COLD-SCRIPTS.md` — full doc with counts, wrong rows, cost, commands

### Verified (command → object)

| Claim | Command |
|-------|---------|
| All three scripts cleared | `python3 scripts/run_cold_scripts.py` → 3/3 ok, 433.8s wall |
| Wrong count = 6 | `python3 scripts/audit_cold_wrong.py` → `wrong_count=6` |
| Privacy clean | `bash scripts/privacy_grep.sh` → `PRIVACY OK` |
| Hosted health | `curl -s …/health` → `parallel: true`, `gemini: true` |
| Sourced spans on script 1 C1/C2 | `curl -sL …/a11.postland.html \| rg 'Noun 43 displays'` → HIT |
| False refusal C3 script 1 | same URL `rg 'Ground Elapsed Time of 102:54'` → HIT |
| PBS false refusals script 2 | `curl -sL …/3310_sun.html \| rg '22 percent drop'` → HIT |
| EUR-Lex false refusals script 3 | `curl -sL …/orphan-works.html \| rg 'public-interest missions'` → HIT |

### Wrong / honest limits

- **6 false refusals** where primary source URL contains the passage (see `docs/COLD-SCRIPTS.md` wrong tables)
- **0 false positives** among 6 SOURCED rows — cited spans verified at object
- Science script **0% sourced** on hosted path — honest refuse demo, but 3/4 claims are wrong refusals vs transcript
- Script 1 ADK path fell back to `engine: direct` with `adk_error: NoKey` — hosted container Gemini key path issue, not cleared locally
- Parallel cost is **estimated** from README band, not billing export
- Did **not** tune `clearance/verify.py` (per task — measure first)

### Totals

| | Script 1 | Script 2 | Script 3 | Total |
|--|----------|----------|----------|-------|
| SOURCED | 2 | 0 | 4 | 6 |
| REFUSED | 1 | 4 | 4 | 9 |
| WRONG | 1 | 3 | 2 | 6 |
| Parallel API | 2 | 5 | 6 | 13 |
