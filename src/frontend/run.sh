#!/bin/bash
echo "Building image (if needed)..."
docker build -t bitesize-app:latest .
echo "Built!"

echo "Stopping and removing the previous bitesize-container (if it exists)..."
docker stop bitesize-container
docker rm bitesize-container

# React apps run on port 3000, map it to the port 8000 on host machine
docker run -dp 8000:3000 --name bitesize-container bitesize-app:latest

echo "Container run successfully. Visit http://localhost:8000 to check"