import PyPDF2
from docx import Document
import textract
import os
import tempfile
import re
import json
import logging

logging.basicConfig(level=logging.DEBUG)

from flask import Flask, request, jsonify

app = Flask(__name__)

from infer import LlamaTextGenerator

# Defining a dictionary to store the answers:


class QuestionGenerator:
    def __init__(self, api_key_file_path):
        """Initialize the QuestionGenerator with the given LlamaTextGenerator instance."""
        self.text_generator = LlamaTextGenerator()

    @staticmethod
    def extract_text_from_pdf(pdf_file_content):
        """
        Extracts text from a PDF file content.

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
        Extracts text from a DOCX file content.

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
        Extracts text from other file formats using textract.

        Args:
            file_content (BytesIO): Content of the file.

        Returns:
            str: Extracted text from the file.
        """
        with tempfile.NamedTemporaryFile(delete=True) as temp_file:
            temp_file.write(file_content.read())
            return textract.process(temp_file.name).decode("utf-8")

    def format_questions(self, data):
        formatted_data = []
        # We expect that each question is followed by its difficulty, hence the step of 2
        for i in range(0, len(data), 2):
            question_item = data[i].replace("\\n", "\n")
            difficulty_item = data[i + 1]  # Assuming the next item is the difficulty

            # Extract the question text
            question_text_search = re.search(
                r"^\d+\..+?(?=\na\))", question_item, re.DOTALL
            )
            if question_text_search:
                question_text = question_text_search.group(0).strip()
            else:
                print("No question text found for item:", question_item)  # Debug print
                continue

            # Extract the options
            options_search = re.findall(r"\b[a-d]\) .+?(?=\n|$)", question_item)
            if options_search:
                options = [option.strip() for option in options_search]
            else:
                print("No options found for item:", question_item)  # Debug print
                continue

            # Extract the difficulty
            difficulty_search = re.search(
                r"Difficulty:\s*(.+)", difficulty_item, re.IGNORECASE
            )
            if difficulty_search:
                difficulty = difficulty_search.group(1).strip()
            else:
                print("No difficulty found for item:", difficulty_item)  # Debug print
                continue

            # Append the formatted question to the list
            formatted_data.append(
                {
                    "difficulty": difficulty,
                    "options": options,
                    "question_text": question_text,
                }
            )

        return formatted_data

    def format_short_answers(self, data):
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

    def generate_mcqs(self, text):
        """Generate MCQs using the Llama model."""
        num_questions = 10  # Define the number of MCQs to generate
        return self.text_generator.generate_questions(text, num_questions)

    def generate_short_answers(self, text):
        """Generate short answer questions using the Llama model."""
        num_questions = 10  # Define the number of short answer questions to generate
        return self.text_generator.generate_short_answers(text, num_questions)

    def generate_mix(self, text):
        """Generate a mix of MCQs and short answer questions using the Llama model."""
        return self.text_generator.generate_mixed_questions(text)

    def generate_custom_prompt(self, text, custom_prompt):
        """Generate questions based on a custom prompt using the Llama model."""
        return self.text_generator.generate_custom_prompt_questions(text, custom_prompt)

    @staticmethod
    def list_files_in_gcp_bucket(bucket_name, folder_name):
        """List all files in a GCP bucket within a specific folder."""
        KEY_PATH = "secrets/generate_mcq_account_key.json"
        storage_client = storage.Client.from_service_account_json(KEY_PATH)
        bucket = storage_client.bucket(bucket_name)
        blobs = bucket.list_blobs(prefix=folder_name)
        return [blob.name for blob in blobs if not blob.name.endswith("/")]

    @staticmethod
    def get_file_from_gcp_bucket(bucket_name, file_name):
        """Get a file from GCP bucket."""
        KEY_PATH = "secrets/generate_mcq_account_key.json"
        storage_client = storage.Client.from_service_account_json(KEY_PATH)
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(file_name)

        # Download as bytes
        content = blob.download_as_bytes()
        return content

    def write_to_gcp(self, data, bucket_name, destination_file_name):
        """
        Writes the given data to a Google Cloud Storage bucket.

        Args:
            data (dict): The data to write.
            bucket_name (str): The name of the GCP bucket.
            destination_file_name (str): The destination file name in the bucket.
        """
        # Convert the dictionary to JSON
        data_json = json.dumps(data)

        # Initialize the GCP Storage client
        storage_client = storage.Client()

        # Get the bucket object
        bucket = storage_client.bucket(bucket_name)

        # Specify the Blob path in the bucket
        blob = bucket.blob(destination_file_name)

        # Upload the JSON data
        blob.upload_from_string(data_json, content_type="application/json")
        print()
        print(f"Your answers have been recorded!")

    def return_text(self, bucket_name, folder_name):
        generator = QuestionGenerator()

        bucket_name = "bite-size-documents"

        folder_name = "documents_to_be_summarized"

        # Get files from GCP Bucket
        files = generator.list_files_in_gcp_bucket(bucket_name, folder_name)
        parsed_texts = []

        # Parsing different file formats and extracting text
        for file in files:
            _, extension = os.path.splitext(file)

            file_in_memory = BytesIO(
                generator.get_file_from_gcp_bucket(bucket_name, file)
            )

            if extension == ".pdf":
                parsed_texts.append(generator.extract_text_from_pdf(file_in_memory))
            elif extension == ".docx":
                parsed_texts.append(generator.extract_text_from_docx(file_in_memory))
            else:
                print(f"Unsupported file format: {extension}")
                continue

            print("\n" * 4)

            # Process each parsed text and print questions based on the user's choice
            for text in parsed_texts:
                _, extension = os.path.splitext(file)
                file_in_memory = BytesIO(
                    generator.get_file_from_gcp_bucket(bucket_name, file)
                )

                if extension == ".pdf":
                    text = generator.extract_text_from_pdf(file_in_memory)
                elif extension == ".docx":
                    text = generator.extract_text_from_docx(file_in_memory)
                else:
                    print(f"Unsupported file format: {extension}")
                    continue

                print("\n" * 4)

        return text

    @app.route("/extract-text", methods=["GET"])
    @cross_origin()
    def extract_text():
        try:
            # Get data from the request here, e.g., specific file names to process
            # data = request.get_json()
            # Assuming data contains 'files' which is a list of file names to process
            text_generator = MCQGenerator()
            bucket_name = "bite-size-documents"
            folder_name = "documents_to_be_summarized"
            files = text_generator.list_files_in_gcp_bucket(bucket_name, folder_name)

            parsed_texts = []

            # Parsing different file formats and extracting text
            # Parsing different file formats and extracting text
            for file_name in files:
                _, extension = os.path.splitext(file_name)
                file_content = text_generator.get_file_from_gcp_bucket(
                    bucket_name, file_name
                )
                file_in_memory = BytesIO(
                    file_content
                )  # Create a BytesIO object from the content

                # Pass the BytesIO object directly to the extraction functions
                if extension == ".pdf":
                    parsed_texts.append(
                        text_generator.extract_text_from_pdf(file_in_memory)
                    )
                elif extension == ".docx":
                    parsed_texts.append(
                        text_generator.extract_text_from_docx(file_in_memory)
                    )
                else:
                    app.logger.error(f"Unsupported file format: {extension}")
                    continue  # Skip unsupported files

            # print("PARSED TEXTS", parsed_texts)
            # Create a response with all parsed texts
            response = {"document_text": parsed_texts}
            return jsonify(response)

        except Exception as e:
            app.logger.error(f"An error occurred: {str(e)}")
            return jsonify({"error": str(e)}), 500

    @app.route("/generate-questions", methods=["POST"])
    def generate_questions():
        app.logger.debug("Request data: %s", request.data)
        data = request.get_json()
        text = data.get("text")
        choice = data.get("choice")

        if text and choice:
            generator = LlamaTextGenerator()

            if choice == "1":
                questions_data = generator.generate_mcqs(text)
                formatted_questions = generator.format_questions(questions_data)
                question_type = "MCQ"
            elif choice == "2":
                short_answer_data = generator.generate_short_answers(text)
                formatted_questions = generator.format_short_answers(short_answer_data)
                question_type = "ShortAnswer"
            else:
                return jsonify({"error": "Invalid choice!"}), 400

            # Create a dynamic key in the response based on question_type
            response = {question_type: formatted_questions}

            return jsonify(response)

        return jsonify({"error": "Missing text or choice parameter!"}), 400


# if __name__ == "__main__":
#     port = os.environ.get("PORT", 80)  # Use PORT if it's there.
#     app.run(debug=False, host="0.0.0.0", port=port)
