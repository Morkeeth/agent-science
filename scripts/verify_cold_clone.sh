#!/usr/bin/env bash
# Stranger cold-clone verification — no keys, no network after clone.
# Run from any directory: bash scripts/verify_cold_clone.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=== Agent Science cold-clone verify ==="
echo "repo: $ROOT"
echo

echo "1. Seed offline document cache..."
python3 scripts/seed_document_cache.py

echo
echo "2. Mutation controls (watch_it_go_red)..."
python3 tests/test_watch_it_go_red.py 2>&1 | tail -1

echo
echo "3. ADK default path..."
python3 tests/test_adk_default_path.py 2>&1 | tail -1

echo
echo "4. Partner runtime wiring..."
python3 tests/test_partner_runtime.py 2>&1 | tail -1

echo
echo "5. SUBMISSION-PACK doc gate..."
python3 scripts/bench_check_docs.py 2>&1 | tail -1

echo
echo "6. Holdout freeze gate..."
python3 scripts/eval_verify_holdout.py 2>&1 | tail -1

echo
echo "7. Registry surface (stranger block)..."
python3 tests/test_registry_surface.py -q 2>&1 | tail -1

echo
echo "8. Offline compound receipt..."
# Avoid `cmd | grep | head` under pipefail — head closes early → SIGPIPE aborts the script
# (watched 2026-09-16: steps 9–10 never ran). Write then sample.
python3 scripts/compound_exhibit_receipt.py > /tmp/compound-exhibit.out 2>&1
grep -E 'parallel_calls|corpus_hits|Mode:' /tmp/compound-exhibit.out | sed -n '1,8p' || true
if grep -q 'corpus_hits B ≥ 1: \*\*NO\*\*' /tmp/compound-exhibit.out; then
  echo "NOTE: offline compound corpus_hits B was NO — receipt written; partner wiring still checked in steps 3–4/10."
fi

echo
echo "9. Eval gate (baseline + ablation + scorer symmetry)..."
python3 scripts/eval_refusal_baseline.py 2>&1 | tail -3
python3 scripts/eval_refusal_ablation.py 2>&1 | tail -2
python3 scripts/eval_scorer_symmetry.py 2>&1 | tail -3

echo
echo "10. Private-workspaces partner health (local, no network)..."
# Cold clone may lack google-adk (no pip after clone). Patch is allowed only
# here, and prove stamps prove_mode=adk-patched + FINDING — not a silent green.
# For a real ADK prove: pip install -r requirements.txt && bash scripts/prove_partner_health_local.sh
PROVE_ALLOW_ADK_PATCH=1 bash scripts/prove_partner_health_local.sh 2>&1 | tail -8

echo
echo "=== cold-clone verify OK ==="
