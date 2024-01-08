# Use an official Python runtime as the base image
FROM python:3.8-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the local directory contents into the container
COPY . .

# Install any needed packages specified in a requirements file (if any)
# This example assumes you have Google Cloud SDK dependencies and any Python dependencies in a requirements.txt file.
RUN pip install --no-cache-dir -r requirements.txt

# The command to run when the container starts
CMD ["./run_all.sh"]
