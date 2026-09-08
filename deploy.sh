#!/usr/bin/env bash
# Deploy Agent Science dual surface to Cloud Run. OSCAR'S CLICK — agents do not run this.
#
# Surfaces on one revision:
#   public desk  — /, /clear, /health, /partners, registry/visibility (partner track)
#   private      — /cases, /api/cases (workspace bearer / session)
#
# SECRET HANDLING:
#   Gemini needs NO KEY HERE. Vertex + Cloud Run SA = ADC.
#   Parallel + workspace access go in Secret Manager via --set-secrets.
#   Never --set-env-vars a plaintext API key.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
GCLOUD="${GCLOUD:-$HOME/google-cloud-sdk/bin/gcloud}"
PROJECT="${GCP_PROJECT:-hack-fleet}"
REGION="${GCP_REGION:-us-central1}"
SERVICE="${GCP_SERVICE:-agent-science}"
PARALLEL_SECRET="${PARALLEL_SECRET:-parallel-api-key}"
ACCESS_SECRET="${ACCESS_SECRET:-agent-science-workspace-access}"
WORKSPACE_BUCKET="${WORKSPACE_BUCKET:-${PROJECT}-agent-science-workspaces}"
CORPUS_BUCKET="${CORPUS_BUCKET:-hack-fleet-agent-science-corpus}"
CORPUS_OBJECT="${CORPUS_OBJECT:-corpus.db}"
REFUSAL_OBJECT="${REFUSAL_OBJECT:-refusal_log.db}"
cd "$ROOT"

# Secrets must already exist (no silent create from agent machines).
"$GCLOUD" secrets describe "$PARALLEL_SECRET" --project="$PROJECT" >/dev/null
"$GCLOUD" secrets describe "$ACCESS_SECRET" --project="$PROJECT" >/dev/null

RUNTIME_SA="${RUNTIME_SA:-agent-science-workspace@${PROJECT}.iam.gserviceaccount.com}"
if ! "$GCLOUD" iam service-accounts describe "$RUNTIME_SA" --project="$PROJECT" >/dev/null 2>&1; then
  "$GCLOUD" iam service-accounts create agent-science-workspace --project="$PROJECT" \
    --display-name='Agent Science private workspace'
fi
for SECRET_NAME in "$PARALLEL_SECRET" "$ACCESS_SECRET"; do
  "$GCLOUD" secrets add-iam-policy-binding "$SECRET_NAME" --project="$PROJECT" \
    --member="serviceAccount:${RUNTIME_SA}" --role=roles/secretmanager.secretAccessor --quiet >/dev/null
done
"$GCLOUD" projects add-iam-policy-binding "$PROJECT" \
  --member="serviceAccount:${RUNTIME_SA}" --role=roles/aiplatform.user --quiet >/dev/null || true

# Workspace object store (tenant cases) — private bucket.
if ! "$GCLOUD" storage buckets describe "gs://${WORKSPACE_BUCKET}" --project="$PROJECT" >/dev/null 2>&1; then
  "$GCLOUD" storage buckets create "gs://${WORKSPACE_BUCKET}" --project="$PROJECT" --location="$REGION" \
    --uniform-bucket-level-access --public-access-prevention
fi
"$GCLOUD" storage buckets add-iam-policy-binding "gs://${WORKSPACE_BUCKET}" \
  --member="serviceAccount:${RUNTIME_SA}" --role=roles/storage.objectUser --quiet >/dev/null

# Corpus / refusal shelf for public /clear compounding.
if ! "$GCLOUD" storage buckets describe "gs://${CORPUS_BUCKET}" --project="$PROJECT" >/dev/null 2>&1; then
  "$GCLOUD" storage buckets create "gs://${CORPUS_BUCKET}" --project="$PROJECT" --location="$REGION" \
    --uniform-bucket-level-access --public-access-prevention
fi
"$GCLOUD" storage buckets add-iam-policy-binding "gs://${CORPUS_BUCKET}" \
  --member="serviceAccount:${RUNTIME_SA}" --role=roles/storage.objectUser --quiet >/dev/null

# Immutable secret versions make a release reproducible; no implicit rotation.
PARALLEL_VERSION="$("$GCLOUD" secrets versions list "$PARALLEL_SECRET" --project="$PROJECT" --filter='state=ENABLED' --sort-by='~createTime' --limit=1 --format='value(name.basename())')"
ACCESS_VERSION="$("$GCLOUD" secrets versions list "$ACCESS_SECRET" --project="$PROJECT" --filter='state=ENABLED' --sort-by='~createTime' --limit=1 --format='value(name.basename())')"
URL="${AGENT_SCIENCE_PUBLIC_ORIGIN:-$("$GCLOUD" run services describe "$SERVICE" --project="$PROJECT" --region="$REGION" --format='value(status.url)')}"
[[ "$URL" == https://* ]] || { echo 'Set AGENT_SCIENCE_PUBLIC_ORIGIN to the HTTPS service origin.' >&2; exit 1; }
CANDIDATE_ORIGIN="https://workspace-candidate---${URL#https://}"

# Candidate revision without traffic. Promote only after verify_partners_hosted.sh.
"$GCLOUD" run deploy "$SERVICE" --source . --project="$PROJECT" --region="$REGION" \
  --platform=managed --allow-unauthenticated --memory=1Gi --timeout=300 --no-traffic --tag=workspace-candidate \
  --concurrency=1 --max-instances=3 --service-account="$RUNTIME_SA" \
  --set-env-vars="AGENT_SCIENCE_HOSTED=1,AGENT_SCIENCE_PUBLIC_ORIGIN=${URL},AGENT_SCIENCE_ALLOWED_ORIGINS=${CANDIDATE_ORIGIN},AGENT_SCIENCE_WORKSPACE_BUCKET=${WORKSPACE_BUCKET},AGENT_SCIENCE_DAILY_RESEARCH_LIMIT=10,AGENT_SCIENCE_GLOBAL_RESEARCH_LIMIT=50,AGENT_SCIENCE_DAILY_MUTATION_LIMIT=100,AGENT_SCIENCE_RESEARCH_TIMEOUT=180,GEMINI_MODEL=gemini-3.5-flash,GCP_PROJECT=${PROJECT},GOOGLE_CLOUD_LOCATION=global,AGENT_BUILDER=1,CORPUS_DB=/tmp/corpus.db,CORPUS_GCS_URI=gs://${CORPUS_BUCKET}/${CORPUS_OBJECT},REFUSAL_LOG_DB=/tmp/refusal_log.db,REFUSAL_LOG_GCS_URI=gs://${CORPUS_BUCKET}/${REFUSAL_OBJECT}" \
  --set-secrets="PARALLEL_API_KEY=${PARALLEL_SECRET}:${PARALLEL_VERSION},AGENT_SCIENCE_ACCESS_CONFIG=${ACCESS_SECRET}:${ACCESS_VERSION}"

REVISION="$("$GCLOUD" run services describe "$SERVICE" --project="$PROJECT" --region="$REGION" --format='value(status.latestReadyRevisionName)')"
printf 'CANDIDATE_REVISION=%s\n' "$REVISION"
printf 'Candidate is deployed without traffic. Verify before promoting this exact revision:\n'
printf '  bash scripts/verify_partners_hosted.sh %s\n' "$CANDIDATE_ORIGIN"
printf '  curl -sf %s/health | python3 -m json.tool\n' "$CANDIDATE_ORIGIN"
printf 'Expect: engine_default=adk · gemini=true · parallel=true · mode=private-workspaces+public-desk\n'
"$GCLOUD" run services describe "$SERVICE" --project="$PROJECT" --region="$REGION" --format='json(status.traffic)'
