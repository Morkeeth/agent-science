#!/usr/bin/env bash
# Cinema pack gate — re-derive every pack claim at its object.
# No keys required for the local path. Hosted desk is expected BLOCKED while
# mode=private-workspaces. Usage: bash scripts/cinema_pack_gate.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
H="${HOSTED_URL:-https://agent-science-568004190078.us-central1.run.app}"
FAIL=0

pass() { echo "PASS  $*"; }
fail() { echo "FAIL  $*"; FAIL=1; }

echo "=== cinema pack gate ==="
echo "repo: $ROOT"
echo

echo "1. pack docs present"
for f in docs/CINEMA-PACK-2026-09-05.md docs/USE-BAR-SESSION-TEMPLATE.md docs/CLOUD-RECEIPT-cinema-pack-2026-09-05.md; do
  if [[ -f "$f" ]]; then pass "$f"; else fail "missing $f"; fi
done

echo
echo "2. public repo (GitHub API)"
GH="$(curl -sS --max-time 20 https://api.github.com/repos/Morkeeth/agent-science || true)"
python3 - "$GH" <<'PY' && pass "private:false MIT" || fail "github visibility"
import json,sys
d=json.loads(sys.argv[1] or "{}")
assert d.get("private") is False, d
assert (d.get("license") or {}).get("spdx_id")=="MIT", d.get("license")
print("  created_at", d.get("created_at"), "pushed_at", d.get("pushed_at"))
PY

echo
echo "3. hosted health + login wall"
HEALTH="$(curl -sS --max-time 30 "$H/health" || true)"
VIS_CODE="$(curl -sS -o /dev/null -w "%{http_code}" --max-time 20 "$H/visibility/ui?q=cinema-pack-gate" || echo 000)"
python3 - "$HEALTH" "$VIS_CODE" <<'PY' && pass "health 200 private-workspaces; visibility 303" || fail "hosted probe"
import json,sys
d=json.loads(sys.argv[1] or "{}")
code=sys.argv[2]
assert d.get("ok") is True, d
assert d.get("mode")=="private-workspaces", d
assert code=="303", code
print("  revision", d.get("revision"), "visibility_http", code)
PY

echo
echo "4. cold clone verify"
if bash scripts/verify_cold_clone.sh >/tmp/cinema-pack-cold.txt 2>&1; then
  pass "verify_cold_clone exit 0"
else
  fail "verify_cold_clone exit $?"
  tail -20 /tmp/cinema-pack-cold.txt || true
fi

echo
echo "5. compound exhibit"
if OUT="$(python3 scripts/compound_exhibit_receipt.py 2>&1)"; then
  echo "$OUT" | head -15
  pass "compound exit 0"
else
  fail "compound exit $?"
  echo "$OUT" | head -20
fi

echo
echo "6. hosted desk demo (expect BLOCKED exit 2)"
set +e
bash scripts/demo_clearance_desk.sh >/tmp/cinema-pack-desk.txt 2>&1
DESK=$?
set -e
if [[ "$DESK" -eq 2 ]] && grep -q "private-workspaces" /tmp/cinema-pack-desk.txt; then
  pass "demo_clearance_desk exit 2 BLOCKED private-workspaces"
else
  fail "demo_clearance_desk unexpected exit $DESK"
  cat /tmp/cinema-pack-desk.txt || true
fi

echo
echo "7. video duration ≤180s + URL placeholder"
DUR="$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 demo/demo-final.mp4 2>/dev/null || echo missing)"
python3 - "$DUR" <<'PY' && pass "demo-final.mp4 duration ≤180" || fail "video duration"
import sys
d=sys.argv[1]
assert d!="missing", d
assert 0 < float(d) <= 180.0, d
print("  duration_s", d)
PY
# Ignore # comment lines — the placeholder file cites youtu.be as an example only.
if grep -v '^[[:space:]]*#' submission/VIDEO-URL.txt 2>/dev/null | grep -Eq 'youtu\.|vimeo\.com'; then
  fail "VIDEO-URL.txt already has a public URL — confirm Oscar pasted it deliberately"
else
  pass "VIDEO-URL.txt still placeholder (Oscar upload pending)"
fi

echo
echo "8. secrets + privacy"
bash scripts/privacy_grep.sh >/tmp/cinema-pack-priv.txt 2>&1 && pass "privacy_grep" || fail "privacy_grep"
python3 tests/test_secret_surfaces.py >/tmp/cinema-pack-sec.txt 2>&1 && pass "secret_surfaces 6/6" || fail "secret_surfaces"
python3 tests/test_same_subject_integrity.py >/tmp/cinema-pack-ssi.txt 2>&1 && pass "same_subject_integrity 8/8" || fail "same_subject_integrity"

echo
echo "9. use-bar template blank (no false Oscar claim)"
if grep -q "this template is blank by design" docs/USE-BAR-SESSION-TEMPLATE.md; then
  pass "use-bar template declares empty-state honesty"
else
  fail "use-bar template missing empty-state honesty line"
fi

echo
if [[ "$FAIL" -eq 0 ]]; then
  echo "=== CINEMA PACK GATE OK ==="
  exit 0
fi
echo "=== CINEMA PACK GATE FAILED ==="
exit 1
