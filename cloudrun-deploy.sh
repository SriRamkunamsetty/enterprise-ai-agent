#!/bin/bash
# cloudrun-deploy.sh
SERVICE_NAME="enterprise-ai-agent"
IMAGE="gcr.io/$GOOGLE_CLOUD_PROJECT/$SERVICE_NAME:latest"
gcloud builds submit --tag "$IMAGE"
gcloud run deploy "$SERVICE_NAME" --image "$IMAGE" --platform managed --region "$CLOUD_RUN_REGION" --allow-unauthenticated