import requests
import json

# URL of your Cloud Run service
service_url = "https://bitesize-grading-jsrdxhl2pa-ue.a.run.app/empty-bucket"
#service_url = "http://10.250.146.64:80/empty-bucket"

# Replace these with the actual bucket and folder name
bucket_name = "bite-size-documents"
folder_name = "documents_to_be_summarized"

# Prepare the data for the POST request
data = {
    "bucket_name": bucket_name,
    "folder_name": folder_name
}

# Make the POST request
response = requests.post(service_url, json=data)

# Print the response
print(response.status_code)
print(response.text)

