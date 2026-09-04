# QWEN EVAL GATE — artifact claims · 2026-09-04

**Gate item (PRIOR LOSS unchecked row):** Every artifact claim measured at the
submitted commit.

**Also shipped this wave:** always-UNKNOWN null arm steelman on the held-out set.

---

## Arms (artifact claims)

| Arm | Description |
|-----|-------------|
| **Baseline** | Trust-doc — every quantified pack/STATUS claim is assumed accurate (two-hour submit craft) |
| **Shipping** | Re-derive at object: run suites, reject "Private until submit", require `@ main` or HEAD SHA, match hosted `/stats`, confirm GitHub `private=false` |

```bash
python3 scripts/eval_artifact_claims.py          # full (needs network for AC7/AC8)
python3 scripts/eval_artifact_claims.py --offline  # AC1–AC6 only
python3 tests/test_artifact_claims.py            # RED control: planted 26/13 must fail
```

---

## Pre-fix finding (measured 2026-09-04 before pack edit)

Shipping found **4 stale claims** the baseline would have shipped:

| id | Stale claim | Object |
|----|-------------|--------|
| AC4 | pack said "Private until submit" | repo public since 2026-08-22 |
| AC5 | Devpost paste `@ e6793ab` | HEAD was `740a60e` |
| AC7 | Public repo row unchecked | GitHub `private=false` |
| AC8 | STATUS **265 claims / hit rate ~0.80** | live `/stats` **n≈306 / hr=0.627** |

```
Baseline:  4/8 = 0.500
Shipping:  8/8 = 1.000
Delta (shipping - baseline): +4
McNemar:   p=0.1250 (b=0 c=4 discordant)
FINDING: 4 stale artifact claim(s) — baseline would ship them.
```

**This is the embarrassment the gate exists to catch.** Numbers were not carried from a prompt — they were wrong at `/stats` and GitHub.

---

## Post-fix (same commands after SUBMISSION-PACK + STATUS edit)

```
Baseline:  8/8 = 1.000
Shipping:  8/8 = 1.000
FINDING: zero stale artifact claims at object.
```

RED control still watches green distrust:

```bash
python3 tests/test_artifact_claims.py
# PASS  planted watch_it_go_red **26/13** → eval exit ≠ 0
```

---

## Null arm (steelman)

```bash
python3 scripts/eval_null_arm.py
```

```
Null:      3/6 = 0.500
Baseline:  5/6 = 0.833
Shipping:  6/6 = 1.000
Delta (shipping - null): +3
FINDING: shipping beats always-UNKNOWN null.
```

If null ever beats shipping, that finding is the report — do not publish a win table.

---

## Checklist status (PRIOR LOSS gate) — this row only

- [x] **Every artifact claim measured at the submitted commit** — `eval_artifact_claims.py` · pre-fix delta +4 · RED control on planted 26/13
- [ ] **Cost from billing** — still open; no Parallel/Gemini billing console on this VM (Oscar)
- [ ] **Track brief on first screen / video attached** — Oscar outward acts

Full checklist: `hack.md` §PRIOR LOSS.
