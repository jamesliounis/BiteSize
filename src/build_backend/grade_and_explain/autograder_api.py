#!/usr/bin/env python3

import PyPDF2
from docx import Document
import textract
import os
import tempfile
import re
import json
import warnings
from flask import Flask, request, jsonify
from infer_explanation import (
    ExplanationGenerator,
)  # Import the ExplanationGenerator class

# Imports for GCP
from google.cloud import storage
from io import BytesIO
from flask_cors import cross_origin, CORS

app = Flask(__name__)
CORS(app)


class Autograder:
    def __init__(self):
        """Initialize the Autograder and create an instance of ExplanationGenerator."""
        self.explanation_gen = (
            ExplanationGenerator()
        )  # Initialize the ExplanationGenerator

    @staticmethod
    def extract_text_from_pdf(pdf_file_content):
        """
        Extract text from a PDF file.

        Args:
            pdf_file_content (BytesIO): Content of the PDF file.

        Returns:
            str: Extracted text from the PDF file.
        """
        pdf_reader = PyPDF2.PdfReader(pdf_file_content)
        text = "".join([page.extract_text() for page in pdf_reader.pages])
        return text

    @staticmethod
    def extract_text_from_docx(docx_file_content):
        """
        Extract text from a DOCX file.

        Args:
            docx_file_content (BytesIO): Content of the DOCX file.

        Returns:
            str: Extracted text from the DOCX file.
        """
        doc = Document(docx_file_content)
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])

    @staticmethod
    def extract_text_from_other_formats(file_content):
        """
        Extract text from other file formats using textract.

        Args:
            file_content (BytesIO): Content of the file.

        Returns:
            str: Extracted text from the file.
        """
        with tempfile.NamedTemporaryFile(delete=True) as temp_file:
            temp_file.write(file_content.read())
            return textract.process(temp_file.name).decode("utf-8")

    def grade_user_answers(self, user_answers, llm_output):
        """
        Grade user's answers by comparing them to LLM explanations.

        Parameters:
        user_answers (dict): A dictionary containing user's selected options for each question.
        llm_output (dict): A dictionary containing LLM's explanations for correct answers.

        Returns:
        int: The user's grade as a percentage of correct answers.
        """

        # Initialize a counter for correct answers
        correct_answers_count = 0

        # Iterate through user answers and llm_output to compare them
        for question, user_answer in user_answers.items():
            # Find the correct answer using regex to locate the first occurrence of a letter option
            correct_answer_match = re.search(r"\b(a|b|c|d)\)", llm_output[question])

            # Check if there is a match and the user's answer is the same as the correct answer
            if (
                correct_answer_match
                and user_answer["selected_option"] == correct_answer_match.group(0)[0]
            ):
                correct_answers_count += 1

        return {"Grade": correct_answers_count / 10 * 100}

    def generate_mcq_explanations(self, text, user_answers):
        """
        Generate explanations for Multiple Choice Questions (MCQs) using the ExplanationGenerator.

        Args:
            text (str): The text containing MCQs.
            user_answers (dict): A dictionary containing user's selected options for each MCQ.

        Returns:
            dict: Explanations for each MCQ along with the user's grade.
        """
        return self.explanation_gen.generate_mcq_explanations(text, user_answers)

    def generate_sa_explanations(self, text, user_answers):
        """
        Generate explanations for Short Answer Questions (SA) using the ExplanationGenerator.

        Args:
            text (str): The text containing SA questions.
            user_answers (dict): A dictionary containing user's answers for each SA question.

        Returns:
            dict: Explanations for each SA question.
        """
        return self.explanation_gen.generate_short_answer_explanations(
            text, user_answers
        )

    def generate_mixed_explanations(self, text, user_answers):
        """
        Generate explanations for a mixed set of questions using the ExplanationGenerator.

        Args:
            text (str): The text containing mixed questions (MCQs and SA).
            user_answers (dict): A dictionary containing user's answers for each question.

        Returns:
            dict: Explanations for each question.
        """
        return self.explanation_gen.generate_mixed_explanations(text, user_answers)

    def generate_cp_explanations(self, text, user_answers):
        """
        Generate explanations for custom prompts using the ExplanationGenerator.

        Args:
            text (str): The text containing custom prompts.
            user_answers (dict): A dictionary containing user's answers for each custom prompt.

        Returns:
            dict: Explanations for each custom prompt.
        """
        return self.explanation_gen.generate_custom_prompt_explanations(
            text, user_answers
        )

    def format_short_answers(self, data):
        """
        Format short answer questions from raw data.

        Args:
            data (list): List of strings containing short answer questions.

        Returns:
            list: Formatted short answer questions with text and difficulty.
        """
        formatted_data = []
        # Split the string into individual questions
        questions = data[0].split("\n")

        for question in questions:
            # Extract the question text and difficulty using regex
            match = re.match(r"(\d+\..+?)\s\((Easy|Medium|Hard)\)", question)
            if match:
                question_text = match.group(1).strip()
                difficulty = match.group(2).strip()

                # Append to the formatted data list
                formatted_data.append(
                    {"question_text": question_text, "difficulty": difficulty}
                )

        return formatted_data

    @staticmethod
    def list_files_in_gcp_bucket(bucket_name, folder_name):
        """
        List all files in a GCP bucket within a specific folder.

        Args:
            bucket_name (str): Name of the GCP bucket.
            folder_name (str): Name of the folder within the bucket.

        Returns:
            list: List of file names in the specified folder.
        """
        KEY_PATH = "secrets/generate_mcq_account_key.json"
        storage_client = storage.Client.from_service_account_json(KEY_PATH)
        bucket = storage_client.bucket(bucket_name)
        blobs = bucket.list_blobs(prefix=folder_name)
        return [blob.name for blob in blobs if not blob.name.endswith("/")]

    @staticmethod
    def get_file_from_gcp_bucket(bucket_name, file_name):
        """
        Get a file from a GCP bucket.

        Args:
            bucket_name (str): Name of the GCP bucket.
            file_name (str): Name of the file to retrieve.

        Returns:
            bytes: Content of the file as bytes.
        """
        KEY_PATH = "secrets/generate_mcq_account_key.json"
        storage_client = storage.Client.from_service_account_json(KEY_PATH)
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(file_name)

        # Download as bytes
        content = blob.download_as_bytes()
        return content

    @staticmethod
    def load_user_answers_from_gcp(bucket_name, answers_file_name):
        """
        Load user answers from a JSON file in a GCP bucket.

        Args:
            bucket_name (str): Name of the GCP bucket.
            answers_file_name (str): Name of the JSON file containing user answers.

        Returns:
            dict: User answers as a dictionary.
        """
        content = Autograder.get_file_from_gcp_bucket(bucket_name, answers_file_name)
        return json.loads(content.decode("utf-8"))

    @app.route("/extract-text", methods=["GET"])
    @cross_origin()
    def extract_text():
        """
        Extracts text from files stored in a specified Google Cloud Storage bucket and folder.
    
        This endpoint processes files with '.pdf' and '.docx' extensions found within the specified
        folder in the bucket and returns the concatenated text from all processed files.
    
        Returns:
            A JSON response containing the extracted text or an error message.
        """
        try:
            text_generator = Autograder()
            bucket_name = "bite-size-documents"
            folder_name = "documents_to_be_summarized"
            files = text_generator.list_files_in_gcp_bucket(bucket_name, folder_name)
    
            parsed_texts = []
    
            # Parsing different file formats and extracting text
            for file_name in files:
                _, extension = os.path.splitext(file_name)
                file_content = text_generator.get_file_from_gcp_bucket(bucket_name, file_name)
                file_in_memory = BytesIO(file_content)  # Create a BytesIO object from the content
    
                # Pass the BytesIO object directly to the extraction functions
                if extension == ".pdf":
                    parsed_texts.append(text_generator.extract_text_from_pdf(file_in_memory))
                elif extension == ".docx":
                    parsed_texts.append(text_generator.extract_text_from_docx(file_in_memory))
                else:
                    app.logger.error(f"Unsupported file format: {extension}")
                    continue  # Skip unsupported files
    
            response = {"document_text": parsed_texts}
            return jsonify(response)
    
        except Exception as e:
            app.logger.error(f"An error occurred: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    
    @app.route("/get-user-answers", methods=["GET"])
    def get_user_answers():
        """
        Retrieves user answers from a specified Google Cloud Storage bucket and folder.
    
        This endpoint assumes that user answers are stored as JSON files and returns the content
        of the first file found in the specified folder.
    
        Returns:
            A JSON response containing user answers or an error message.
        """
        autograder = Autograder()
        bucket_name = "bite-size-documents"
        folder_name_answers = "user_answers"
    
        # Load user answers from GCP bucket
        answer_files = autograder.list_files_in_gcp_bucket(bucket_name, folder_name_answers)
        user_answers_file_name = answer_files[0]  # Assuming the first file is what you want
        user_answers = autograder.load_user_answers_from_gcp(bucket_name, user_answers_file_name)
        return jsonify(user_answers)


    @app.route("/generate-explanations", methods=["POST"])
    @cross_origin()
    def generate_explanations():
        """
        Generate explanations for user-submitted questions.

        Expects a JSON payload containing 'text' (the text with questions) and 'user_answers' (user's answers).
        Determines the type of questions (MCQ or SA) and generates explanations accordingly.

        Returns:
            dict: Explanations for the questions.
        """
        app.logger.debug("Request data: %s", request.data)
        data = request.get_json()
        text = data.get("text")
        answers = data.get("user_answers")

        if text and answers:
            autograder = Autograder()

            if list(answers.keys())[0] == "MCQ":
                explanation_data = autograder.explanation_gen.generate_mcq_explanations(
                    text, answers["MCQ"]
                )
                explanation_data.update(
                    autograder.grade_user_answers(answers["MCQ"], explanation_data)
                )
                explanation_type = "MCQ"
            elif list(answers.keys())[0] == "SA":
                explanation_data = (
                    autograder.explanation_gen.generate_short_answer_explanations(
                        text, answers["SA"]
                    )
                )
                explanation_type = "ShortAnswers"

            else:
                return jsonify({"error": "Invalid choice!"}), 400

            # Create a dynamic key in the response based on question_type
            response = {explanation_type: explanation_data}

            return jsonify(response)

        return jsonify({"error": "Missing text or choice parameter!"}), 400


    @app.route("/empty-bucket", methods=["POST"])
    def delete_bucket_contents():
        """
        Deletes all objects within a specified folder in a Google Cloud Storage bucket.
    
        This endpoint receives JSON content with 'bucket_name' and 'folder_name' specified.
        It will delete all objects within the specified folder of the given bucket, excluding
        the folder itself as a placeholder.
    
        Returns:
            A success message with a 200 status code if objects are found and deleted,
            or an error message with a 404 status code if no objects are found.
        """
        content = request.json
        bucket_name = content["bucket_name"]
        folder_name = content["folder_name"]
    
        if not folder_name.endswith("/"):
            folder_name += "/"
    
        # Initialize the GCP Storage client
        client = storage.Client(project="ac215-bitesize")
        bucket = client.bucket(bucket_name)
    
        # List all objects in the specified folder
        blobs = list(client.list_blobs(bucket, prefix=folder_name))
        blobs_to_delete = [
            blob for blob in blobs if blob.name != folder_name
        ]  # Exclude the folder placeholder
    
        if blobs_to_delete:
            # Delete the objects, excluding the folder placeholder
            bucket.delete_blobs(blobs_to_delete)
            return (
                f"Successfully deleted all objects in folder {folder_name} from bucket {bucket_name}",
                200,
            )
        else:
            return f"No objects found in folder {folder_name} in bucket {bucket_name}", 404



# if __name__ == "__main__":
#     port = os.environ.get("PORT", 80)  # Use PORT if it's there.
#     app.run(debug=False, host="0.0.0.0", port=port)
