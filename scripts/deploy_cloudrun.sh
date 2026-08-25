#!/bin/bash
set -e

PROJECT_ID="${1:-gemeni-workshop}"
SERVICE_NAME="gecx-text-streaming-bff"
REGION="us-central1"
SA_EMAIL="gecx-bff-sa@${PROJECT_ID}.iam.gserviceaccount.com"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "================================================================="
echo "🚀 Deploying $SERVICE_NAME to Google Cloud Run ($REGION)"
echo "👉 Project: $PROJECT_ID"
echo "================================================================="

cd "$ROOT_DIR"

gcloud run deploy "$SERVICE_NAME" \
    --source="." \
    --platform=managed \
    --region="$REGION" \
    --project="$PROJECT_ID" \
    --service-account="$SA_EMAIL" \
    --allow-unauthenticated \
    --cpu=2 \
    --memory=2Gi \
    --min-instances=1 \
    --max-instances=10 \
    --concurrency=80 \
    --timeout=60m \
    --set-env-vars="GCP_PROJECT_ID=${PROJECT_ID},GCP_LOCATION=us,LOG_LEVEL=INFO,MOCK_MODE=false"

echo "================================================================="
echo "✅ Cloud Run deployment complete!"
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" --region="$REGION" --project="$PROJECT_ID" --format="value(status.url)")
echo "👉 Live Cockpit Web URL: $SERVICE_URL"
echo "================================================================="
