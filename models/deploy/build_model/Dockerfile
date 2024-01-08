# Use CUDA base image
FROM nvidia/cuda:11.3.1-devel-ubuntu20.04

# Set the environment variable
ENV DEBIAN_FRONTEND=noninteractive

# Install nginx and python
RUN apt-get update && \
    apt-get install -y nginx python3 python3-dev python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy the requirements file first to leverage Docker cache
COPY requirements.txt ./

# Install any needed packages specified in requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container
COPY . .

# Expose port 8080
EXPOSE 8080

# Define environment variable
ENV NAME World

# Run main.py when the container launches
ENTRYPOINT [ "python3" ]
CMD ["main.py"]

