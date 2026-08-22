"""Review-lane: scan tests for literals that mirror shipping constants without import."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from clearance import verify as vmod

TEST = ROOT / "tests" / "test_watch_it_go_red.py"


def main():
    src = TEST.read_text()
    issues = []

    if 'REAL_INC = "http://rightsstatements.org/vocab/InC/1.0/"' in src:
        issues.append(("MEDIUM", "REAL_INC",
                       "Hardcoded InC URI; engine._RULES uses same URI but exports no constant"))

    if "assert moved / len(a) > 0.10" in src:
        issues.append(("LOW", "0.10 threshold",
                       "Shift threshold is test-local acceptance criterion, not engine rule"))

    if "assert checked >= 3" in src:
        issues.append(("LOW", ">= 3 GREEN",
                       "Minimum GREEN count for chrome control is arbitrary floor"))

    if "assert len(locate._CHROME) >= 5" in src:
        issues.append(("OK", "_CHROME length", "Imports locate._CHROME live"))

    if "set(CITED_UNKNOWN_CAUSES) == {NOT_EVALUATED, SOURCE_SILENT}" in src:
        issues.append(("OK", "CITED_UNKNOWN_CAUSES", "Imported constants on both sides"))

    if 'INC_URL = "https://rightsstatements.org/vocab/InC/1.0/"' in src:
        issues.append(("LOW", "INC_URL vs REAL_INC", "Duplicate URI constant names in same file"))

    if "from check_pitch import CLAIMS" in src and "from clearance.locate import _CHROME" in src:
        issues.append(("OK", "t_green_evidence", "Live CLAIMS + live _CHROME"))

    if "from clearance import locate, verify" in src:
        issues.append(("OK", "t_verifier_chrome_grep", "Chrome list read from locate module"))

    if "for use in engine.USES:" in src:
        issues.append(("OK", "t_second_question tripwire", "Uses engine.USES from shipping module"))

    if "assert checked >=" in src and "MIN_WORDS" in src:
        issues.append(("OK", "MIN_WORDS", "t_green imports verify.MIN_WORDS (drift fixed)"))
    elif "q.count(\" \") >= 6" in src:
        issues.append(("MEDIUM", "MIN_WORDS drift",
                       "t_green still uses literal 6; verify.MIN_WORDS may differ"))

    print("=== Live-object binding audit ===\n")
    for sev, name, msg in issues:
        print(f"  [{sev:6}] {name}")
        print(f"           {msg}\n")


if __name__ == "__main__":
    main()
