from google.cloud import aiplatform
from google.protobuf.struct_pb2 import Value
import json


class LlamaTextGenerator:
    """
    A class for generating text using a deployed Llama model on Vertex AI.

    Args:
        location (str, optional): The location where the Vertex AI endpoint is deployed. Default is "us-east1".
    """

    def __init__(self, location="us-east1"):
        """
        Initialize the LlamaTextGenerator with the Vertex AI endpoint ID.
        """
        # Configure the connection to the model
        CONFIG_PATH = (
            "../../../secrets/config.json"  # Update with your config file path
        )
        config = self.read_config(CONFIG_PATH)
        endpoint_id = config["endpointId"]
        project_id = config["projectId"]

        aiplatform.init(project=project_id, location=location)
        self.endpoint = aiplatform.Endpoint(endpoint_id)

    @staticmethod
    def read_config(file_path):
        """
        Read configuration from a JSON file.

        Args:
            file_path (str): Path to the JSON configuration file.

        Returns:
            dict: Configuration data as a dictionary.
        """
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

    def generate_questions(self, text, numQuestions):
        """
        Generates multiple-choice questions (MCQs) from a given text using the model.

        Args:
            text (str): The input text from which MCQs will be generated.
            numQuestions (int): The number of questions to generate from the text.

        Returns:
            list[str]: List of generated MCQs.
        """
        query = f"Generate {numQuestions} MCQs to help me study from this document exclusively, and each time tell me what you think the level of difficulty is: Easy, Medium, Hard."
        prompt = f"{text}\n{query}"

        # Send prediction request to Vertex AI
        output = self._send_prediction_request(prompt)

        # Extract and return the generated questions
        if output:
            questions = output.split("\n\n")
            return questions
        return []

    def generate_short_answers(self, text, numQuestions):
        """
        Generates short answer questions from a given text using the model.

        Args:
            text (str): The input text from which short answer questions will be generated.
            numQuestions (int): The number of questions to generate from the text.

        Returns:
            list[str]: List of generated short answer questions.
        """
        query = f"Generate {numQuestions} short answer questions based on the following text:"
        prompt = f"{text}\n{query}"

        # Send prediction request to Vertex AI
        output = self._send_prediction_request(prompt)

        if output:
            questions = output.split("\n\n")
            return questions
        return []

    def generate_custom_prompt_questions(self, text, custom_prompt):
        """
        Generates questions based on a custom prompt. Still tied to the text.

        Args:
            text (str): The input text from which short answer questions will be generated.
            custom_prompt (str): Custom prompt for generating questions.

        Returns:
            list[str]: List of generated questions.
        """
        prompt = f"{text}\n{custom_prompt}"
        output = self._send_prediction_request(prompt)

        if output:
            questions = output.split("\n\n")
            return questions
        return []

