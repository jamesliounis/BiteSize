# Use an official Python runtime as the base image
FROM python:3.8-slim

# Set the working directory inside the container
WORKDIR /app

# Install Google Cloud SDK
RUN apt-get update -y && apt-get install -y curl && \
    export CLOUD_SDK_REPO="cloud-sdk-$(lsb_release -c -s)" && \
    echo "deb http://packages.cloud.google.com/apt $CLOUD_SDK_REPO main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - && \
    apt-get update -y && apt-get install -y google-cloud-sdk

# Copy the local directory contents into the container
COPY . .

# Install any needed packages specified in a requirements file (if any)
RUN pip install --no-cache-dir -r requirements.txt

# Set the entry point as your deployment script
ENTRYPOINT ["./deploy_container.sh"]

