#!/bin/bash
echo "Building image (if needed)..."
docker build -t bitesize-app-backend:latest .
echo "Built!"

echo "Stopping and removing the previous bitesize-backend-container (if it exists)..."
docker stop bitesize-backend-container
docker rm bitesize-backend-container

docker run -p 8080:8080 --name bitesize-backend-container bitesize-app-backend:latest

echo "Container run successfully. Visit http://localhost:8080/docs to check"