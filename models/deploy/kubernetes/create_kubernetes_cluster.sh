#!/bin/bash

# Set variables
CLUSTER_NAME="gpu-cluster"
ZONE="us-central1-c"
MACHINE_TYPE="n1-standard-4"
DISK_SIZE="50"
NUM_GPUS="1"
GPU_TYPE="nvidia-tesla-t4"
NUM_NODES="1" # Adjust this as needed

# Create GKE cluster
gcloud container clusters create $CLUSTER_NAME \
    --zone $ZONE \
    --machine-type $MACHINE_TYPE \
    --disk-size $DISK_SIZE \
    --accelerator type=$GPU_TYPE,count=$NUM_GPUS \
    --num-nodes $NUM_NODES \
    --enable-autoscaling \
    --preemptible


