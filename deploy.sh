#!/usr/bin/env bash
# Deploy Agent Science to Cloud Run. OSCAR'S CLICK — this script does not run itself.
#
# SECRET HANDLING, and why this version looks different from the obvious one:
#
#   The first draft passed both API keys through --set-env-vars. That writes them into
#   the Cloud Run service config (readable by any project viewer), into this shell's
#   history, and into Cloud Build logs — three destinations we do not control and
#   cannot un-write once the command has run. A deploy flag is a destination.
#
#   Gemini needs NO KEY HERE AT ALL. Vertex is the primary path and Cloud Run's service
#   account provides Application Default Credentials, so the service authenticates as
#   itself. The fix is to remove the secret, not to protect it.
#
#   Parallel has no ADC equivalent, so it goes in Secret Manager and is referenced with
#   --set-secrets. The value is mounted at runtime; it never appears in config, in a
#   command line, or in a build log.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
GCLOUD="${GCLOUD:-$HOME/google-cloud-sdk/bin/gcloud}"
PROJECT="${GCP_PROJECT:-hack-fleet}"
REGION="${GCP_REGION:-us-central1}"
SERVICE="${GCP_SERVICE:-agent-science}"
SECRET="${PARALLEL_SECRET:-parallel-api-key}"

cd "$ROOT"

echo "1. Enabling services..."
"$GCLOUD" services enable run.googleapis.com cloudbuild.googleapis.com \
  artifactregistry.googleapis.com secretmanager.googleapis.com \
  --project="$PROJECT" --quiet

echo "2. Putting the Parallel key in Secret Manager (from the 0600 file, once)..."
if ! "$GCLOUD" secrets describe "$SECRET" --project="$PROJECT" >/dev/null 2>&1; then
  "$GCLOUD" secrets create "$SECRET" --project="$PROJECT" --replication-policy=automatic
fi
# The value is piped on stdin, never as an argument, so it cannot land in shell history
# or a process list.
"$GCLOUD" secrets versions add "$SECRET" --project="$PROJECT" \
  --data-file="$HOME/.config/keys/parallel.key"

RUNTIME_SA="$("$GCLOUD" projects describe "$PROJECT" --format='value(projectNumber)')-compute@developer.gserviceaccount.com"
"$GCLOUD" secrets add-iam-policy-binding "$SECRET" --project="$PROJECT" \
  --member="serviceAccount:${RUNTIME_SA}" --role=roles/secretmanager.secretAccessor --quiet
# The runtime service account also needs Vertex, which is how Gemini is reached with no key.
"$GCLOUD" projects add-iam-policy-binding "$PROJECT" \
  --member="serviceAccount:${RUNTIME_SA}" --role=roles/aiplatform.user --quiet

echo "3. Deploying from source (Cloud Build — no local container, no local daemon)..."
"$GCLOUD" run deploy "$SERVICE" \
  --source . \
  --project="$PROJECT" \
  --region="$REGION" \
  --platform=managed \
  --allow-unauthenticated \
  --memory=512Mi \
  --timeout=300 \
  --service-account="$RUNTIME_SA" \
  --set-env-vars="GEMINI_MODEL=gemini-3.5-flash-lite,GCP_PROJECT=${PROJECT},CORPUS_DB=/tmp/corpus.db" \
  --set-secrets="PARALLEL_API_KEY=${SECRET}:latest"

echo
echo "NOTE: --allow-unauthenticated makes this PUBLIC. The submission requires a hosted"
echo "URL a judge can open, so it is correct here — but it is an outward act and it is"
echo "Oscar's decision, not this script's."
