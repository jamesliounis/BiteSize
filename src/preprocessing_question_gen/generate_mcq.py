#!/usr/bin/env python3

import os
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

import PyPDF2
from docx import Document
import textract
import tempfile

# Imports for GCP
from google.cloud import storage
from google.cloud import aiplatform
from google.protobuf import json_format
from google.protobuf.struct_pb2 import Value
import asyncio

from io import BytesIO

# Custom
from testbank import TestBank
from gcp import Bucket


class MCQGenerator:
    def __init__(self):
        """Initialize the MCQGenerator."""
        # TestBank holds all the results from the inference model so it's only queried when needed
        # It's without text right now, but that'll change
        self.testBank = TestBank()

    def parse(self, bucket, filename):
        """
        Given a single file, calls the appropriate parser given the file extension.

        Args:
            bucket (Bucket): the instantiated custom GCP Bucket object
            filename (str): the full filename

        Returns: 
            str: parsed text from the file
        """
        print(f"Parsing file [{filename}] ...")

        # Don't care about the name, only the file extension like .pdf
        _, extension = os.path.splitext(filename)

        file_in_memory = BytesIO(bucket.get_file(filename))

        # Uses the appropriate parser for different file formats and extracts string representation of the text
        if extension == ".pdf":
            return self.extract_text_from_pdf(file_in_memory)

        elif extension == ".docx":
            return self.extract_text_from_docx(file_in_memory)

        else:
            # Warn the user the file isn't supported, but don't stop the execution
            print(f"Unsupported file format [{extension}] \nSkipping...")            

        print("\n" * 4)
    
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

    @staticmethod
    def print_formatted_questions(data):
        """Prints formatted MCQs.

        Args:
            data (list[str]): List of generated MCQs.
        """
        for idx, question_block in enumerate(data, 1):
            lines = question_block.split("\n")

            # Extract the actual question from the line.
            actual_question = lines[0].split(". ")[1]

            # Print the formatted question.
            print(f"Question {idx}: {actual_question}\n")
            for option in lines[1:-2]:
                print(option)
            print("\n" + lines[-1] + "\n")

    def mcq_test(self, text, num_questions = 10, repeats = False):
        """
        Use the right model to build the TestBank for the text (if not done previously) and output tests of user length

        Args:
            text (str): the parsed document text
            num_questions (int): the number of questions the user wants for this test, default 10
            repeats (bool): whether or not the user is okay with seeing repeats, default 10

        Returns:
            list[str]: List of multiple choice test questions.
        """
        # We need the textual information to make this at all, if this is the first call, create it
        if self.testBank is None:
            self.testBank.initalizeText(text)

        # Need to figure out if we have a question bank of MCQs already
        if self.testBank.mcqs is None:
            self.testBank.buildBank('mcq')

        # A question bank for the text exists, now we can make a multiple choice test
        return self.testBank.generate_mcq_test(text, num_questions, repeats)
    
    def short_answer_test(self, text, num_questions = 10, repeats = False):
        """
        Use the right model to build the TestBank for the text (if not done previously) and output test of user length

        Args:
            text (str): the parsed document text
            num_questions (int): the number of questions the user wants for this test, default 10
            repeats (bool): whether or not the user is okay with seeing repeats, default 10

        Returns:
            list[str]: List of short answer test questions.
        """
        # We need the textual information to make this at all, if this is the first call, create it
        if self.testBank is None:
            self.testBank.initalizeText(text)

        # Need to figure out if we have a question bank of MCQs already
        if self.testBank.short_answers is None:
            self.testBank.buildBank('short answer')

        # A question bank for the text exists, now we can make a short answer test
        return self.testBank.generate_short_answer_test(text, num_questions, repeats)     
        

    def mixed_question_test(self, text, num_questions = 10, repeats = False):
        """
        Use the right model to build the TestBank for the text (if not done previously) and output test of user length

        Args:
            text (str): the parsed document text
            num_questions (int): the number of questions the user wants for this test, default 10
            repeats (bool): whether or not the user is okay with seeing repeats, default 10

        Returns:
            list[str]: List of multiple choice and short answer test questions.
        """
        if self.testBank is None: 
            self.testBank.initalizeText(text)

        # Since mixed questions is just a mix of mcqs and short answers, we can use them in place of another inference call
        if self.testBank.mcqs is None:
            self.testBank.buildBank('mcq')

        if self.testBank.short_answers is None:
            self.testBank.buildBank('short answer')

         # A question bank for the text exists, now we can make a mixed format test
        return self.testBank.generate_mixed_test(text, num_questions, repeats)

    def custom_prompt_test(self, text, custom_prompt):
        # We need the textual information to make this at all, if this is the first call, create it
        if self.testBank is None:
            self.testBank.initalizeText(text)

        # Make the bank if nothing is there
        if self.testBank.custom is None:
            self.testBank.buildBank('custom')

        # A question bank for the text exists, now we can make a mixed format test
        return self.testBank.generate_custom_test(text, custom_prompt)        
        


        raise NotImplementedError('[custom_prompt_test] in [MCQGenerator] is not finished yet')

    

if __name__ == "__main__":
    
    async def main_async():
        generator = MCQGenerator()
        print("Initialized MCQGenerator")

        # Bucket setup
        key_path = "../../../secrets/generate_mcq_service_account_key.json"
        bucket_name = "bite-size-documents"
        folder_name = "documents_to_be_summarized"
        bucket = Bucket(key_path, bucket_name)
        print('Connected to Bucket')

        # Get all file names from the GCP bucket
        files = bucket.list_files(folder_name)
        print(f"Found {len(files)} files in the GCP bucket")

        # Parsing different file formats and extracting text
        parsed_texts = [generator.parse(bucket_name, file) for file in files]

        # Generating and printing MCQs for each parsed text
        for text in parsed_texts:
            print("Generating MCQs...")
            questions_data = generator.mcq_test(text)
            generator.print_formatted_questions(questions_data)
    
    asyncio.run(main_async())

