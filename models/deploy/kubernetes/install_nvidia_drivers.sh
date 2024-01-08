gcloud config set compute/zone us-central1-c
gcloud container clusters get-credentials gpu-cluster
kubectl apply -f <https://raw.githubusercontent.com/GoogleCloudPlatform/container-engine-accelerators/master/nvidia-driver-installer/cos/daemonset-preloaded.yaml>
