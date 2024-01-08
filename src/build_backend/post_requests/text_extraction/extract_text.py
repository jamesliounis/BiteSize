# Import necessary libraries
import requests  # For making HTTP requests
import json  # For working with JSON data
from google.cloud import storage  # For interacting with Google Cloud Storage
from io import BytesIO  # For handling file content as bytes
import os  # For miscellaneous operating system functions
from PyPDF2 import PdfReader  # For working with PDF files
from docx import Document  # For working with DOCX files
import tempfile  # For creating temporary files

import logging

logging.basicConfig(level=logging.DEBUG)

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_cors import cross_origin

app = Flask(__name__)
CORS(app, resources={r"*": {"origins": "*"}})

# Set up Google Cloud Storage Client
KEY_PATH = "secrets/generate_mcq_account_key.json"
storage_client = storage.Client.from_service_account_json(KEY_PATH)


class TextExtractor:
    """
    A utility class for extracting text from files and interacting with Google Cloud Storage.
    """

    @staticmethod
    def list_files_in_gcp_bucket(bucket_name, folder_name):
        """
        List files in a Google Cloud Storage bucket within a specific folder.

        Args:
            bucket_name (str): The name of the Google Cloud Storage bucket.
            folder_name (str): The name of the folder within the bucket.

        Returns:
            list: List of file names in the specified folder.
        """
        bucket = storage_client.bucket(bucket_name)
        blobs = bucket.list_blobs(prefix=folder_name)
        return [blob.name for blob in blobs if not blob.name.endswith("/")]

    @staticmethod
    def load_user_answers_from_gcp(bucket_name, answers_file_name):
        """
        Load user answers from a file in a Google Cloud Storage bucket.

        Args:
            bucket_name (str): The name of the Google Cloud Storage bucket.
            answers_file_name (str): The name of the user answers file.

        Returns:
            dict: User answers loaded from the file.
        """
        content = TextExtractor.get_file_from_gcp_bucket(bucket_name, answers_file_name)
        return json.loads(content.decode("utf-8"))

    @staticmethod
    def get_file_from_gcp_bucket(bucket_name, file_name):
        """
        Get a file from a Google Cloud Storage bucket.

        Args:
            bucket_name (str): The name of the Google Cloud Storage bucket.
            file_name (str): The name of the file to retrieve.

        Returns:
            bytes: The content of the file as bytes.
        """
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(file_name)
        return blob.download_as_bytes()

    @staticmethod
    def extract_text_from_pdf(pdf_file_content):
        """
        Extract text from a PDF file content.

        Args:
            pdf_file_content (bytes): The content of the PDF file as bytes.

        Returns:
            str: Extracted text from the PDF file.
        """
        pdf_reader = PdfReader(BytesIO(pdf_file_content))
        return "".join([page.extract_text() for page in pdf_reader.pages])

    @staticmethod
    def extract_text_from_docx(docx_file_content):
        """
        Extract text from a DOCX file content.

        Args:
            docx_file_content (bytes): The content of the DOCX file as bytes.

        Returns:
            str: Extracted text from the DOCX file.
        """
        doc = Document(BytesIO(docx_file_content))
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])
    
    
    @app.route("/extract-text", methods=["GET"])
    @cross_origin()
    def extract_text():
        try:
            # Get data from the request here, e.g., specific file names to process
            #data = request.get_json()
            # Assuming data contains 'files' which is a list of file names to process
            text_generator = TextExtractor()
            bucket_name = "bite-size-documents"
            folder_name = "documents_to_be_summarized"
            files = text_generator.list_files_in_gcp_bucket(bucket_name, folder_name)
            
            

            parsed_texts = []

            # Parsing different file formats and extracting text
            for file_name in files:
                _, extension = os.path.splitext(file_name)
                file_in_memory = BytesIO(text_generator.get_file_from_gcp_bucket(bucket_name, file_name))
                file_in_memory = file_in_memory.getvalue()

                if extension == ".pdf":
                    parsed_texts.append(text_generator.extract_text_from_pdf(file_in_memory))
                elif extension == ".docx":
                    parsed_texts.append(text_generator.extract_text_from_docx(file_in_memory))
                else:
                    app.logger.error(f"Unsupported file format: {extension}")
                    continue  # Skip unsupported files

            # Create a response with all parsed texts
            response = {"document_text": parsed_texts}
            return jsonify(response)

        except Exception as e:
            app.logger.error(f"An error occurred: {str(e)}")
            return jsonify({"error": str(e)}), 500



#if __name__ == "__main__":
    #port = os.environ.get("PORT", 8080)  # Use PORT if it's there.
    #app.run(debug=False, host="0.0.0.0", port=port)
