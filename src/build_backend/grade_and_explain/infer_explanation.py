#!/usr/bin/env python3

from google.cloud import aiplatform
from google.protobuf import json_format
from google.protobuf.struct_pb2 import Value
import json


class ExplanationGenerator:
    def __init__(self, location="us-east1"):
        """
        Initialize the ExplanationGenerator with the Vertex AI endpoint ID.
        """
        # Configure the connection to the model
        CONFIG_PATH = "../../../secrets/config.json"
        config = self.read_config(CONFIG_PATH)
        endpoint_id = config["endpointId"]
        project_id = config["projectId"]

        aiplatform.init(project=project_id, location=location)
        self.endpoint = aiplatform.Endpoint(endpoint_id)

    @staticmethod
    def read_config(file_path):
        with open(file_path, "r") as file:
            config = json.load(file)
        return config

    def _send_prediction_request(self, prompt):
        """
        Sends a prediction request to the deployed model on Vertex AI.

        Args:
            prompt (str): The input prompt for text generation.

        Returns:
            str: Generated text.
        """
        instance = {"prompt": prompt}
        try:
            predictions = self.endpoint.predict(
                instances=[instance], timeout=120
            )  # Add a timeout of 30 seconds
            # Extract and return the generated text from the predictions
            if predictions.predictions and "response" in predictions.predictions[0]:
                return predictions.predictions[0]["response"]
        except Exception as e:
            print(f"Error while getting prediction: {e}")
        return ""

    def _generate_explanations_with_query(
        self, text, user_answers, explanation_type, query
    ):
        explanations = {}

        if explanation_type == "MCQ":
            for question, user_answer in user_answers.items():
                chat_history = (
                    []
                )  # This might need to be maintained outside the loop if context is important
                # COMMENTED OUT QUERY
                query = f"Explain why the answer '{user_answer}' to the question '{question}' is correct or incorrect based on the following text: {text}."
                input_data = {"question": query, "chat_history": chat_history}
                explanation = self._send_prediction_request(input_data)
                explanations[question] = explanation

        elif explanation_type == "ShortAnswers":
            for question, user_answer in user_answers.items():
                chat_history = (
                    []
                )  # This might need to be maintained outside the loop if context is important
                input_data = {"question": query, "chat_history": chat_history}
                explanation = self._send_prediction_request(input_data)
                explanations[question] = explanation

        return explanations

    def generate_mcq_explanations(self, text, user_answers):
        return self._generate_explanations_with_query(
            text, user_answers, "MCQ", query=None
        )

    def generate_short_answer_explanations(self, text, user_answers):
        explanations = {}
        for question, user_response in user_answers.items():
            selected_option = user_response["selected_option"]
            query = f"Explain why the answer '{selected_option}' to the question '{question}' is correct or incorrect based on the following text: {text}."
            explanation = self._generate_explanations_with_query(
                text, {question: user_response}, "ShortAnswers", query
            )
            explanations[question] = explanation
        return explanations

    def generate_mixed_explanations(self, text, user_answers):
        return self._generate_explanations_with_query(
            text, user_answers, "MixedAnswers"
        )

    def generate_custom_prompt_explanations(self, text, user_answers):
        return self._generate_explanations_with_query(
            text, user_answers, "CustomPrompt"
        )

