# Import necessary libraries
import requests  # For making HTTP requests
import json  # For working with JSON data
from google.cloud import storage  # For interacting with Google Cloud Storage
from io import BytesIO  # For handling file content as bytes
import os  # For miscellaneous operating system functions
import PyPDF2  # For working with PDF files
import textract  # For extracting text from other file formats
from docx import Document  # For working with DOCX files
import tempfile  # For creating temporary files

# Cloud Run service URL
questions_api_url = "https://bitesize-question-gen-jsrdxhl2pa-ue.a.run.app/generate-questions"
extract_text_api_url = "https://bitesize-question-gen-jsrdxhl2pa-ue.a.run.app/extract-text"
#extract_text_api_url  = "http://10.250.146.64:8080/extract-text"
#api_url = 'http://10.250.146.64:80/generate-questions'
#api_url = "http://172.17.0.2:80/generate-questions"



# Make a GET request to the extract-text endpoint
get_response = requests.get(extract_text_api_url)

# Check if the GET request was successful
if get_response.status_code == 200:
    # Extract the text data from the response
    parsed_texts = get_response.json().get('document_text', [])

    # Define the request payload using the extracted text
    payload = {
        "text": "\n".join(parsed_texts),  # Combine text from all files
        "choice": "1"  # '1' for MCQ, '2' for short-answer (modify as needed)
    }

    # Send the POST request to the Cloud Run service
    post_response = requests.post(questions_api_url, json=payload)

    # Check the response status code
    if post_response.status_code == 200:
        # Print the JSON response
        response_data = post_response.json()
        print(json.dumps(response_data, indent=4))
    else:
        print(f"Error in POST request: {post_response.status_code} - {post_response.text}")
else:
    print(f"Error in GET request: {get_response.status_code} - {get_response.text}")

