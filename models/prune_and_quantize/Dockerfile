# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the maintainer label
LABEL maintainer="jamesliounis@g.harvard.edu"

# Set environment variables to ensure Python output is sent to terminal
ENV PYTHONUNBUFFERED=1

# Create and set working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Expose any ports the app is expecting in the environment
EXPOSE 8080

# Automatically run the pruning script when the container starts:
CMD ["python", "scripts/prune_model.py"]
