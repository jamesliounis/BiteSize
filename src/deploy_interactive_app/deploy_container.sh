# Build container
docker build -t gcr.io/ac215-bitesize/bitesize-app:latest .

#Push container
gcloud auth configure-docker
docker push gcr.io/ac215-bitesize/bitesize-app:latest

# Deploy container
gcloud run deploy bitesize \
--image gcr.io/ac215-bitesize/bitesize-app:latest \
--platform managed \
--region us-east1


gcloud run services add-iam-policy-binding bitesize \
--region=us-east1 \
--member=allUsers \
--role=roles/run.invoker

