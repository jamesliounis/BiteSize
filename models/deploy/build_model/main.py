from flask import Flask, request, Response
from transformers import AutoTokenizer, AutoModelForCausalLM
import deepspeed
import os
import logging
from typing import Mapping, Any
import torch
from google.cloud import storage

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# Variables for GCS
BUCKET_NAME = 'hugging-face-models'
MODEL_DIR = 'hugging-face-models/llama-7b-pruned'  

llama_model = os.path.join("/tmp", MODEL_DIR)


class LLMBaseModel:
    """
    Class responsible for handling text generation using a specific model.

    Attributes:
        model_name (str): Name or path of the model.
        top_p (float): Nucleus sampling parameter.
        top_k (int): Top K sampling parameter.
        world_size (int): Number of available GPUs.
        num_tokens (int): Maximum number of tokens for the generated output.
        tokenizer: Tokenizer associated with the model.
        model: The actual model used for text generation.
    """

    def __init__(
        self,
        num_tokens: int = 200,
        top_p: float = 0.92,
        top_k: int = 50,
        model_name: str = llama_model,
    ):
        
        """
        Initialize the class by downloading the model and setting parameters.

        Args:
            num_tokens (int): Maximum number of tokens for the generated output.
            top_p (float): Nucleus sampling parameter.
            top_k (int): Top K sampling parameter.
            model_name (str): Name or path of the model.
        """

        self.download_model_from_gcs()
        self.model_name = model_name
        self.top_p = top_p
        self.top_k = top_k
        self.world_size = torch.cuda.device_count()
        self.num_tokens = num_tokens
        logging.info(f"Using {self.world_size} gpus")
        
        # Initialize the tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)

        try:
            logging.info(f"Loading model: {self.model_name}")

            # Construct model with fake meta tensors
            with deepspeed.OnDevice(dtype=torch.float16, device="meta"):
                self.model = AutoModelForCausalLM.from_pretrained(self.model_name)

            # Since we already downloaded the model, no need for snapshot_download

            # Initialize with DeepSpeed for inference
            self.model = deepspeed.init_inference(
                self.model,
                mp_size=self.world_size,
                dtype=torch.float16
            )
            self.model = self.model.module
            logging.info("model_loaded!")

        except Exception:
            raise ValueError(f"Failed to load the model from: {self.model_name}")

    def download_model_from_gcs(self):
        """
        Downloads the model and its configuration from Google Cloud Storage.
        """

        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)
        
        model_files = ['pytorch_model.bin', 'config.json']  # Add other required files if needed
        
        for file_name in model_files:
            blob = bucket.blob(os.path.join(MODEL_DIR, file_name))
            blob.download_to_filename(os.path.join(llama_model, file_name))
        logging.info("Model downloaded from GCS!")

    def generator(self, form: Mapping[str, Any]) -> str:

        """
        Generate text based on the input form data.

        Args:
            form (Mapping[str, Any]): Contains input data for text generation.

        Returns:
            str: Generated text response.
        """

        logging.info(f'this is the form: {form}')
        prompt = form["instances"][0]["prompt"]
        input_tokens = self.tokenizer.encode_plus(prompt, return_tensors="pt", padding=True)
        response = self.model.generate(**input_tokens, max_length=self.num_tokens, top_k=self.top_k, top_p=self.top_p)
        response = self.tokenizer.decode(response[0], skip_special_tokens=True)
        return {"response": response}

writer = LLMBaseModel()

@app.route("/isalive")
def isalive():
    
    """
    Endpoint to check if the service is alive.

    Returns:
        Response: HTTP response with status code.
    """

    print("/isalive request")
    status_code = Response(status=200)
    return status_code

@app.route('/predict', methods = ['POST'])
def predict():
    """
    Endpoint to generate text based on input.

    Returns:
        Union[dict, Tuple[dict, int]]: Generated text or error message.
    """
    try:
        form = request.get_json()
        return writer.generator(form)
    except Exception as e:
        logging.error(f"Error generating response: {e}")
        return {"error": str(e)}, 500

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=True, host='0.0.0.0', port=port, use_reloader=False)
