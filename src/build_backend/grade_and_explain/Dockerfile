# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the secrets into the container
COPY secrets/ /etc/secrets/

# Set environment variables for the secrets
# Make sure to replace <your-secrets> with the actual secrets
ENV GOOGLE_APPLICATION_CREDENTIALS=/etc/secrets/generate_mcq_account_key.json


# Make port 80 available to the world outside this container
# This is optional and depends on if your app needs a port
EXPOSE 80

# Define environment variable
# This is optional and depends on if your app uses environment variables
ENV NAME World

# Run the Gunicorn server
CMD ["gunicorn", "-b", ":80", "autograder_api:app"]

#CMD ["python", "autograder_api.py"]


