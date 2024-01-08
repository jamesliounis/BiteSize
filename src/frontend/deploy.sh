# Normal build command
docker build -t bitesize-app:latest .

# Tag the image with the GCR registry URL
docker tag bitesize-app:latest gcr.io/ ac215-bitesize/bitesize-app:latest

# Authenticate Docker to GCR
gcloud auth configure-docker

# Push container to GCR
docker push gcr.io/ ac215-bitesize/bitesize-app:latest

# Get credentials for existing cluster bitesize-backend
gcloud container clusters get-credentials bitesize-backend --region=us-central1 --project=ac215-bitesize

# Create namespace for the app
kubectl create namespace bitesize-frontend
kubectl config set-context --current --namespace=bitesize-frontend

# Create deployment
kubectl create deployment bitesize-app --image=gcr.io/ac215-bitesize/bitesize-app:latest

# Expose deployment to the internet, 3000 being the container, 80 being the host
kubectl expose deployment bitesize-app --type=LoadBalancer --port=80 --target-port=3000
