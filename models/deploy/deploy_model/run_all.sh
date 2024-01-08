#!/bin/bash

# Ensure the script stops if there's any error
set -e

# Navigate to the build_model directory
cd ../build_model

# 1. Build and push Docker image
echo "Building and pushing Docker image..."
chmod +x build_and_push.sh
./build_and_push.sh

# Navigate to the deploy_model directory
cd ../deploy_model

# 2. Deploy the model to Vertex AI
echo "Deploying model to Vertex AI..."
python3 deploy_to_vertex.py

# Note: Starting the Flask API server is not included here since the server should be started by Vertex AI upon deployment.