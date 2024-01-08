# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Copy your secrets into the container (Make sure you don't expose sensitive data)
COPY secrets /usr/src/app/secrets

# Set the GOOGLE_APPLICATION_CREDENTIALS environment variable
ENV GOOGLE_APPLICATION_CREDENTIALS=/usr/src/app/secrets/generate_mcq_account_key.json

# Install any needed packages specified in requirements.txt
# If you have a requirements.txt, uncomment the next line
RUN pip install --no-cache-dir -r requirements.txt

# Install Ansible
RUN pip install --no-cache-dir ansible

# Copy over the generate_mcq.py script
COPY generate_mcq.py .

EXPOSE 8080


# Run the Gunicorn server
CMD ["gunicorn", "-b", "0.0.0.0:$PORT", "generate_test:app"]

#CMD ["python", "generate_test.py"]


