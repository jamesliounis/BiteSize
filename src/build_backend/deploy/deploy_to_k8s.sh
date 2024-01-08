# Authenticate with GCP
gcloud auth login


# Build application containers

# For generate_mcq
cd generate_mcq
docker build -t gcr.io/ac215-bitesize/generate-test:v1 .
docker push gcr.io/ac215-bitesize/generate-test:v1

# For grade_and_explain
cd ../grade_and_explain
docker build -t gcr.io/ac215-bitesize/grade-and-explain:v1 .
docker push gcr.io/ac215-bitesize/grade-and-explain:v1

# Build Kubernetes cluster

gcloud container --project "ac215-bitesize" clusters create-auto "bitesize-backend" \\
                 --region "us-central1" --release-channel "regular" \\
                 --network "projects/ac215-bitesize/global/networks/default" --subnetwork "projects/ac215-bitesize/regions/us-central1/subnetworks/default" \\
                 --cluster-ipv4-cidr "/17"

# Get cluster credentials

gcloud container clusters get-credentials bitesize-backend --zone us-central1-c --project ac215-bitesize

# Deploy the containers to the cluster using Ansible playbook

ansible-playbook deploy_to_k8s.yml




