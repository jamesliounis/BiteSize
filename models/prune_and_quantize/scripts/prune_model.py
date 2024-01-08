# Import necessary libraries
import torch
import psutil
from transformers import AutoTokenizer, AutoModelForCausalLM
import os
from google.cloud import storage
from google.oauth2.service_account import Credentials
import gc
import matplotlib.pyplot as plt
import json

# Determine path for GCP credentials and load them
key_path = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "secrets", "gcp_key.json"
)
credentials = Credentials.from_service_account_file(key_path)

bucket_name = "hugging_face_models"


# Function to get the current memory usage in MB
def get_memory_usage():
    """
    Get the current memory usage in MB.

    Returns:
        float: The current memory usage in MB.
    """
    process = psutil.Process()
    mem_info = process.memory_info()
    return mem_info.rss / 1024**2  # Convert bytes to MB


# Load the tokenizer and model without accumulating gradients
# to save memory
with torch.no_grad():
    model_path = "openlm-research/open_llama_7b_v2"
    TOKENIZER = AutoTokenizer.from_pretrained(model_path)
    MODEL = AutoModelForCausalLM.from_pretrained(model_path)
    MODEL.eval()  # Set model to evaluation mode

# Display the initial memory usage
print(f"Initial Memory usage: {get_memory_usage():.2f} MB")


# Function to get a nested attribute from an object
def nested_getattr(obj, attr):
    """
    Retrieve a nested attribute from an object.

    Args:
        obj (object): The object to retrieve the attribute from.
        attr (str): The nested attribute string.

    Returns:
        object: The retrieved attribute.
    """
    for a in attr.split("."):
        obj = getattr(obj, a)
    return obj


# Function to set a value to a nested attribute in an object
def nested_setattr(obj, attr, value):
    """
    Set a value to a nested attribute in an object.

    Args:
        obj (object): The object to set the attribute on.
        attr (str): The nested attribute string.
        value (Any): The value to set.
    """
    attrs = attr.split(".")
    for a in attrs[:-1]:
        obj = getattr(obj, a)
    setattr(obj, attrs[-1], value)

# Extract unique layer types from the computational graph
def get_unique_layer_types_from_graph(graph_path):
    """
    Extract unique layer types from a computational graph JSON file.

    Args:
        graph_path (str): Path to the computational graph JSON file.

    Returns:
        list: List of unique layer types.
    """
    with open(graph_path, 'r') as f:
        graph_data = json.load(f)

    # Extract unique layer types based on the structure of your JSON file
    weight_map = graph_data['weight_map']
    unique_layers = set()
    for layer_name in weight_map:
        # Extract only those entries that have the format "model.layers.<layer_num>.<layer_type>.<attr>"
        if layer_name.startswith("model.layers.") and ".weight" in layer_name:
            # Extract the layer type and add it to the unique_layers set
            layer_type = layer_name.split(".")[3]
            unique_layers.add(layer_type)
    return list(unique_layers)

# Path to the computational graph
graph_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "configs", "llama_computational_graph.json")

# Get the unique layer types
unique_layer_types = get_unique_layer_types_from_graph(graph_path)

# construct the layers_to_prune list using these unique layer types
num_layers = len(MODEL.model.layers)
layers_to_prune = []

# for layer_type in unique_layer_types:
#     for i in range(num_layers):
#         layers_to_prune.append(f"model.layers.{i}.{layer_type}.weight")


###### The code above generates the list below we simply chose to use a hardcoded version for debugging purposes. 

# List of layers to prune
layers_to_prune = [
    "model.layers.{}.input_layernorm.weight",
    "model.layers.{}.mlp.down_proj.weight",
    "model.layers.{}.mlp.gate_proj.weight",
    "model.layers.{}.mlp.up_proj.weight",
    "model.layers.{}.post_attention_layernorm.weight",
    "model.layers.{}.self_attn.k_proj.weight",
    "model.layers.{}.self_attn.o_proj.weight",
    "model.layers.{}.self_attn.q_proj.weight",
    "model.layers.{}.self_attn.rotary_emb.inv_freq",
    "model.layers.{}.self_attn.v_proj.weight"
]


# Function to upload files to GCP bucket
def upload_to_gcs(bucket_name, source_folder, destination_folder, credentials):
    """
    Upload files from a local folder to a Google Cloud Storage bucket.

    Args:
        bucket_name (str): The name of the GCP bucket.
        source_folder (str): Path to the local source folder.
        destination_folder (str): The destination folder in the GCP bucket.
        credentials (Credentials): GCP authentication credentials.
    """
    storage_client = storage.Client(credentials=credentials)
    bucket = storage_client.bucket(bucket_name)

    # Walk through all the files in the source folder
    for root, _, files in os.walk(source_folder):
        for file in files:
            local_file = os.path.join(root, file)
            destination_blob_name = os.path.join(destination_folder, file)
            blob = bucket.blob(destination_blob_name)
            blob.upload_from_filename(local_file)
            print(f"Uploaded {file} to {destination_blob_name}")


# Create a tensor of zeros for pruning
zero_tensor = torch.tensor(0.0, device=MODEL.device)


# Determine the number of layers in the model
num_layers = len(MODEL.model.layers)

# List to store memory usages after pruning each layer
memory_usages = []

# Prune each layer of the model
for layer_format in layers_to_prune:
    for i in range(num_layers):
        layer_name = layer_format.format(i)

        # Perform pruning without accumulating gradients
        with torch.no_grad():
            weights = nested_getattr(MODEL, layer_name)
            mask = torch.abs(weights) >= 0.01

            # Prune weights that are smaller than a threshold
            pruned_weights = torch.where(mask, weights, zero_tensor)
            nested_setattr(MODEL, layer_name, torch.nn.Parameter(pruned_weights))

            # Free up memory
            del weights, mask, pruned_weights

        # Collect garbage to free up more memory
        gc.collect()
        torch.cuda.empty_cache()

        # Display memory usage after pruning this layer
        print(
            f"Memory usage after pruning layer {layer_name}: {get_memory_usage():.2f} MB"
        )
        memory_usages.append(get_memory_usage())

# Plot the memory usage after pruning each layer
layers = [f"Layer {i+1}" for i in range(len(memory_usages))]


plt.figure(figsize=(10, 6))
plt.plot(layers, memory_usages, marker="o", linestyle="-", color="r")
plt.title("Memory Usage Evolution During Pruning")
plt.xlabel("Layers")
plt.ylabel("Memory Usage (MB)")
plt.grid(True, which="both", linestyle="--", linewidth=0.5)
plt.tight_layout()

plt.savefig("memory_usage_analysis.png")

# Upload the memory usage plot to GCP bucket
plot_local_path = "memory_usage_analysis.png"
plot_destination_folder = "memory_usage_analysis"
upload_to_gcs(bucket_name, plot_local_path, plot_destination_folder, credentials)

# Move the model to CPU for quantization
MODEL = MODEL.cpu()
MODEL.eval()

# Apply dynamic quantization to the model
quantized_model = torch.quantization.quantize_dynamic(
    MODEL, {torch.nn.Linear}, dtype=torch.qint8
)

# Display memory usage after quantization
print(f"Memory usage after quantization: {get_memory_usage():.2f} MB")

# Save the quantized model locally
local_path = "llama_7b_pruned"
quantized_model.save_pretrained(local_path)

# Free up memory by deleting models
del MODEL, quantized_model
gc.collect()
torch.cuda.empty_cache()

# Display memory usage after saving the quantized model
print(f"Memory usage after saving quantized model: {get_memory_usage():.2f} MB")

# Upload the quantized model to GCP bucket
bucket_name = "hugging_face_models"
source_folder = local_path
destination_folder = "llama_7b_pruned"
upload_to_gcs(bucket_name, source_folder, destination_folder, credentials)

# Delete the locally saved model directory
os.rmdir(local_path)

# Display the final memory usage
print(f"Memory usage at the end: {get_memory_usage():.2f} MB")
