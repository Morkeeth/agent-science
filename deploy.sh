#!/usr/bin/env bash
# Deploy the reviewed private workspace runtime. Secrets must already exist.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
GCLOUD="${GCLOUD:-$HOME/google-cloud-sdk/bin/gcloud}"
PROJECT="${GCP_PROJECT:-hack-fleet}"
REGION="${GCP_REGION:-us-central1}"
SERVICE="${GCP_SERVICE:-agent-science}"
PARALLEL_SECRET="${PARALLEL_SECRET:-parallel-api-key}"
ACCESS_SECRET="${ACCESS_SECRET:-agent-science-workspace-access}"
BUCKET="${WORKSPACE_BUCKET:-${PROJECT}-agent-science-workspaces}"
cd "$ROOT"
# No local corpus/case data is seeded. Existing cloud state is never replaced here.
"$GCLOUD" secrets describe "$PARALLEL_SECRET" --project="$PROJECT" >/dev/null
"$GCLOUD" secrets describe "$ACCESS_SECRET" --project="$PROJECT" >/dev/null
RUNTIME_SA="${RUNTIME_SA:-agent-science-workspace@${PROJECT}.iam.gserviceaccount.com}"
if ! "$GCLOUD" iam service-accounts describe "$RUNTIME_SA" --project="$PROJECT" >/dev/null 2>&1; then
  "$GCLOUD" iam service-accounts create agent-science-workspace --project="$PROJECT" --display-name='Agent Science private workspace'
fi
for SECRET_NAME in "$PARALLEL_SECRET" "$ACCESS_SECRET"; do
  "$GCLOUD" secrets add-iam-policy-binding "$SECRET_NAME" --project="$PROJECT" \
    --member="serviceAccount:${RUNTIME_SA}" --role=roles/secretmanager.secretAccessor --quiet >/dev/null
done
if ! "$GCLOUD" storage buckets describe "gs://${BUCKET}" --project="$PROJECT" >/dev/null 2>&1; then
  "$GCLOUD" storage buckets create "gs://${BUCKET}" --project="$PROJECT" --location="$REGION" \
    --uniform-bucket-level-access --public-access-prevention
fi
"$GCLOUD" storage buckets add-iam-policy-binding "gs://${BUCKET}" \
  --member="serviceAccount:${RUNTIME_SA}" --role=roles/storage.objectUser --quiet >/dev/null
# Immutable secret versions make a release reproducible; no implicit rotation.
PARALLEL_VERSION="$("$GCLOUD" secrets versions list "$PARALLEL_SECRET" --project="$PROJECT" --filter='state=ENABLED' --sort-by='~createTime' --limit=1 --format='value(name)')"
ACCESS_VERSION="$("$GCLOUD" secrets versions list "$ACCESS_SECRET" --project="$PROJECT" --filter='state=ENABLED' --sort-by='~createTime' --limit=1 --format='value(name)')"
URL="${AGENT_SCIENCE_PUBLIC_ORIGIN:-$("$GCLOUD" run services describe "$SERVICE" --project="$PROJECT" --region="$REGION" --format='value(status.url)')}"
[[ "$URL" == https://* ]] || { echo 'Set AGENT_SCIENCE_PUBLIC_ORIGIN to the HTTPS service origin.' >&2; exit 1; }
# A single atomic revision update; no clearing configuration on the live revision.
"$GCLOUD" run deploy "$SERVICE" --source . --project="$PROJECT" --region="$REGION" \
  --platform=managed --allow-unauthenticated --memory=512Mi --timeout=240 --no-traffic --tag=workspace-candidate \
  --concurrency=1 --max-instances=3 --service-account="$RUNTIME_SA" \
  --set-env-vars="AGENT_SCIENCE_HOSTED=1,AGENT_SCIENCE_PUBLIC_ORIGIN=${URL},AGENT_SCIENCE_WORKSPACE_BUCKET=${BUCKET},AGENT_SCIENCE_DAILY_RESEARCH_LIMIT=10,AGENT_SCIENCE_GLOBAL_RESEARCH_LIMIT=50,AGENT_SCIENCE_DAILY_MUTATION_LIMIT=100,AGENT_SCIENCE_RESEARCH_TIMEOUT=180" \
  --set-secrets="PARALLEL_API_KEY=${PARALLEL_SECRET}:${PARALLEL_VERSION},AGENT_SCIENCE_ACCESS_CONFIG=${ACCESS_SECRET}:${ACCESS_VERSION}"
REVISION="$("$GCLOUD" run services describe "$SERVICE" --project="$PROJECT" --region="$REGION" --format='value(status.latestReadyRevisionName)')"
printf 'CANDIDATE_REVISION=%s\n' "$REVISION"
printf 'Candidate is deployed without traffic. Verify it before promoting this exact revision.\n'
"$GCLOUD" run services describe "$SERVICE" --project="$PROJECT" --region="$REGION" --format='json(status.traffic)' 
