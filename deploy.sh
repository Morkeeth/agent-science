#!/usr/bin/env bash
# Deploy Agent Science to Cloud Run. OSCAR'S CLICK — this script does not run itself.
#
# SECRET HANDLING:
#   Gemini needs NO KEY HERE. Vertex + Cloud Run SA = ADC.
#   Parallel goes in Secret Manager via --set-secrets.
#   Prior revisions leaked keys through --set-env-vars; this script REMOVES those
#   env vars on every deploy so a clean revision cannot keep the wound open.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
GCLOUD="${GCLOUD:-$HOME/google-cloud-sdk/bin/gcloud}"
PROJECT="${GCP_PROJECT:-hack-fleet}"
REGION="${GCP_REGION:-us-central1}"
SERVICE="${GCP_SERVICE:-agent-science}"
SECRET="${PARALLEL_SECRET:-parallel-api-key}"
BUCKET="${CORPUS_BUCKET:-hack-fleet-agent-science-corpus}"
CORPUS_OBJECT="${CORPUS_OBJECT:-corpus.db}"
REFUSAL_OBJECT="${REFUSAL_OBJECT:-refusal_log.db}"

cd "$ROOT"

echo "1. Enabling services..."
"$GCLOUD" services enable run.googleapis.com cloudbuild.googleapis.com \
  artifactregistry.googleapis.com secretmanager.googleapis.com storage.googleapis.com \
  aiplatform.googleapis.com \
  --project="$PROJECT" --quiet

echo "2. Parallel key → Secret Manager (stdin/file only)..."
if ! "$GCLOUD" secrets describe "$SECRET" --project="$PROJECT" >/dev/null 2>&1; then
  "$GCLOUD" secrets create "$SECRET" --project="$PROJECT" --replication-policy=automatic
fi
"$GCLOUD" secrets versions add "$SECRET" --project="$PROJECT" \
  --data-file="$HOME/.config/keys/parallel.key"

RUNTIME_SA="$("$GCLOUD" projects describe "$PROJECT" --format='value(projectNumber)')-compute@developer.gserviceaccount.com"
"$GCLOUD" secrets add-iam-policy-binding "$SECRET" --project="$PROJECT" \
  --member="serviceAccount:${RUNTIME_SA}" --role=roles/secretmanager.secretAccessor --quiet
"$GCLOUD" projects add-iam-policy-binding "$PROJECT" \
  --member="serviceAccount:${RUNTIME_SA}" --role=roles/aiplatform.user --quiet

echo "3. Corpus bucket (shared shelf across Cloud Run instances)..."
if ! "$GCLOUD" storage buckets describe "gs://${BUCKET}" --project="$PROJECT" >/dev/null 2>&1; then
  "$GCLOUD" storage buckets create "gs://${BUCKET}" --project="$PROJECT" --location="$REGION"
fi
"$GCLOUD" storage buckets add-iam-policy-binding "gs://${BUCKET}" \
  --member="serviceAccount:${RUNTIME_SA}" --role=roles/storage.objectAdmin --quiet

if [[ -f "$ROOT/cache/refusal_log.db" ]]; then
  echo "3b. Seed truth dictionary to GCS (if local shelf exists)..."
  "$GCLOUD" storage cp "$ROOT/cache/refusal_log.db" "gs://${BUCKET}/${REFUSAL_OBJECT}" \
    --project="$PROJECT" --quiet || true
fi
if [[ -f "$ROOT/cache/corpus.db" ]]; then
  "$GCLOUD" storage cp "$ROOT/cache/corpus.db" "gs://${BUCKET}/${CORPUS_OBJECT}" \
    --project="$PROJECT" --quiet || true
fi

echo "4. Deploy (replace env — no API keys in the clear; Parallel via secret; corpus via GCS)..."
# --set-env-vars and --remove-env-vars cannot be combined. Clear first so leaked
# GEMINI_API_KEY / PARALLEL_API_KEY plaintext cannot survive into the new revision.
if "$GCLOUD" run services describe "$SERVICE" --project="$PROJECT" --region="$REGION" >/dev/null 2>&1; then
  "$GCLOUD" run services update "$SERVICE" \
    --project="$PROJECT" --region="$REGION" \
    --clear-env-vars --quiet || true
fi
"$GCLOUD" run deploy "$SERVICE" \
  --source . \
  --project="$PROJECT" \
  --region="$REGION" \
  --platform=managed \
  --allow-unauthenticated \
  --memory=512Mi \
  --timeout=300 \
  --service-account="$RUNTIME_SA" \
  --set-env-vars="GEMINI_MODEL=gemini-3.5-flash,GCP_PROJECT=${PROJECT},CORPUS_DB=/tmp/corpus.db,CORPUS_GCS_URI=gs://${BUCKET}/${CORPUS_OBJECT},REFUSAL_LOG_DB=/tmp/refusal_log.db,REFUSAL_LOG_GCS_URI=gs://${BUCKET}/${REFUSAL_OBJECT},AGENT_BUILDER=1,GOOGLE_CLOUD_LOCATION=global" \
  --set-secrets="PARALLEL_API_KEY=${SECRET}:latest"

URL="$("$GCLOUD" run services describe "$SERVICE" --project="$PROJECT" --region="$REGION" \
  --format='value(status.url)')"
echo "HOSTED_URL=$URL"
echo "Post-deploy checks:"
echo "  curl -sf \"$URL/health\""
echo "  curl -sf \"$URL/stats\" | head"
echo "  curl -sf \"$URL/popular\" | head"
echo "  curl -sf -X POST \"$URL/clear\" -H 'Content-Type: application/json' \\"
echo "    -d '{\"script\":\"Directive 2012/28/EU.\",\"subject\":\"compound-prep\"}' | head -c 400"
curl -sf "$URL/health" | head -c 400
echo
echo "NOTE: rotate Parallel/Gemini keys if they were ever in plaintext env (Oscar)."
