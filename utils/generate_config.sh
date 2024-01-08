#!/bin/bash

# Set the path for the config file
CONFIG_PATH="../../../secrets/config.json"

# Get project ID
PROJECT_ID=$(gcloud config get-value project)

# List the available endpoints and take the first one (modify as needed)
ENDPOINT_ID=$(gcloud beta ai endpoints list --region=us-east1 --format="value(ENDPOINT_ID)" | head -n 1)

# Check if we have both the project ID and the endpoint ID
if [[ -z "$PROJECT_ID" || -z "$ENDPOINT_ID" ]]; then
    echo "Error: Couldn't retrieve the project ID and/or endpoint ID."
    exit 1
fi

# Create the directory if it doesn't exist
mkdir -p $(dirname $CONFIG_PATH)

# Create the config.json file
echo "{
  \"project_id\": \"$PROJECT_ID\",
  \"endpoint_id\": \"$ENDPOINT_ID\"
}" > $CONFIG_PATH

echo "config.json has been written to $CONFIG_PATH"
