#!/bin/bash
echo "Cleaning up previous session..."
bash cleanup.sh

echo "Building backend..."
docker build -t bitesize-app-backend:latest src/intermediary/.
docker run -dp 8080:8080 --name bitesize-backend-container bitesize-app-backend:latest
echo 'Container run successfully. Visit http://localhost:8080/docs'
echo "Backend built successfully"

echo "Building frontend..."
docker build -t bitesize-app:latest src/frontend/.
docker run -dp 8000:3000 --name bitesize-container bitesize-app:latest
echo 'Container run successfully. Visit http://localhost:8000'
echo "Frontend built successfully"
