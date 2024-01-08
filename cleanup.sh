#!/bin/bash
# Function to stop and remove a Docker container
stop_and_remove_container() {
    local container_name=$1

    # Check if the container exists
    if docker ps -a --format '{{.Names}}' | grep -q "^$container_name$"; then
        # Container exists, stop it
        docker stop $container_name

        # Remove the container
        docker rm $container_name

        echo "Container $container_name stopped and removed."
    else
        echo "Container $container_name does not exist."
    fi
}

stop_and_remove_container "bitesize-backend-container"
stop_and_remove_container "bitesize-container"
