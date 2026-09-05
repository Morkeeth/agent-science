#!/usr/bin/env bash
# Pre-deploy checklist — run before Oscar's `bash deploy.sh`.
# Exits non-zero on any hard failure.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
GCLOUD="${GCLOUD:-$HOME/google-cloud-sdk/bin/gcloud}"
PROJECT="${GCP_PROJECT:-hack-fleet}"
KEY="$HOME/.config/keys/parallel.key"

fail=0
ok() { echo "  OK  $*"; }
warn() { echo "  WARN  $*"; }
bad() { echo "  FAIL  $*"; fail=1; }

echo "=== Agent Science deploy prep ==="
echo "repo: $ROOT"
echo

echo "1. Required files in Docker context"
for f in Dockerfile requirements.txt agent_science.py ask_registry.py cloud/service.py \
         truth-dictionary/aliases.json clearance/dictionary.py; do
  [[ -e "$f" ]] && ok "$f" || bad "missing $f"
done

echo
echo "2. Control tests"
python3 tests/test_watch_it_go_red.py >/dev/null 2>&1 && ok "watch_it_go_red 72/72" || bad "watch_it_go_red"
python3 tests/test_partner_runtime.py >/dev/null 2>&1 && ok "partner_runtime 7/7" || bad "partner_runtime"
python3 tests/test_popular.py >/dev/null 2>&1 && ok "popular endpoint" || bad "popular"
python3 tests/test_stack_product.py >/dev/null 2>&1 && ok "stack product" || bad "stack"
python3 tests/test_dictionary.py >/dev/null 2>&1 && ok "dictionary" || bad "dictionary"

echo
echo "3. Dictionary boot state"
python3 -m clearance lookup "2012/28/EU" >/dev/null 2>&1 && ok "lookup 2012/28/EU (free tier)" || warn "lookup miss — run boot_registry + ingest"
st=$(python3 -m clearance stats 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('n',0))" 2>/dev/null || echo 0)
[[ "${st:-0}" -ge 100 ]] && ok "dictionary claims ($st)" || warn "dictionary small ($st) — run boot_registry.py"

echo
echo "4. GCP prerequisites (Oscar gate)"
if [[ -x "$GCLOUD" ]]; then ok "gcloud at $GCLOUD"; else bad "gcloud not found"; fi
if "$GCLOUD" auth list --filter=status:ACTIVE --format='value(account)' 2>/dev/null | grep -q .; then
  ok "gcloud authenticated"
else
  bad "gcloud not authenticated"
fi
if [[ -f "$KEY" ]]; then ok "Parallel key at ~/.config/keys/parallel.key"; else bad "Parallel key missing"; fi

echo
echo "5. Secret / bucket (dry describe)"
if "$GCLOUD" secrets describe parallel-api-key --project="$PROJECT" >/dev/null 2>&1; then
  ok "Secret Manager parallel-api-key exists"
else
  warn "parallel-api-key secret will be created on deploy"
fi
if "$GCLOUD" secrets describe agent-science-workspace-access --project="$PROJECT" >/dev/null 2>&1; then
  ok "Secret Manager agent-science-workspace-access exists"
else
  warn "workspace-access secret missing — deploy.sh will fail closed"
fi

echo
echo "6. Deploy will set (see deploy.sh + docs/DEPLOY-PREP-2026-09-05.md)"
cat <<EOF
  Candidate revision with --no-traffic --tag=workspace-candidate
  PARALLEL_API_KEY + AGENT_SCIENCE_ACCESS_CONFIG via Secret Manager only
  Workspace bucket gs://\${PROJECT}-agent-science-workspaces (no local seed)
  Hosted mode private-workspaces: /health public; /search /clear require login
  Prefer checklist: docs/DEPLOY-PREP-2026-09-05.md
EOF

echo
if [[ "$fail" -eq 0 ]]; then
  echo "=== READY — Oscar runs: bash deploy.sh ==="
  echo "Then verify compound A/B + video beats."
  exit 0
fi
echo "=== NOT READY — fix FAIL items above ==="
exit 1
