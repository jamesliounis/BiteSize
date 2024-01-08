#!/bin/bash

# Set your GCP project ID and region
PROJECT_ID="ac215-bitesize"
REGION="us-east1"

# List all Vertex AI endpoints and delete them
for ENDPOINT_ID in $(gcloud ai endpoints list --region=$REGION --project=$PROJECT_ID --format="value(endpointId)")
do
    echo "Deleting endpoint: $ENDPOINT_ID"
    gcloud ai endpoints delete $ENDPOINT_ID --region=$REGION --project=$PROJECT_ID --quiet
done

