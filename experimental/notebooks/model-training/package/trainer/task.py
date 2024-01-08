## IMPORTS
import argparse
import os
import requests
import zipfile
import tarfile
import time
import json
import re
import io
from typing import Optional
from os import listdir
from os.path import isfile, join
from tqdm.auto import tqdm
from PIL import Image
from transformers import ViltConfig
#from tqdm.notebook import tqdm  ### KIM COMMENTED THIS
from tqdm import tqdm
import torch
from transformers import ViltProcessor
import numpy as np
from transformers import ViltForQuestionAnswering
from torch.utils.data import DataLoader
# W&B
import wandb
from wandb.keras import WandbCallback, WandbMetricsLogger
from tensorflow.python.keras import backend as K
# Cloud
from google.cloud import storage


####### PATHS #####################
#root = '/Users/samch/OneDrive/Desktop/bu_mlops/val2014/val2014'
#path_questions = '/Users/samch/OneDrive/Desktop/bu_mlops/v2_OpenEnded_mscoco_val2014_questions.json'
#path_annotations = '/Users/samch/OneDrive/Desktop/bu_mlops/v2_mscoco_val2014_annotations.json'


# Define the name of your GCP bucket
gcs_client = storage.Client()
bucket_name = "bite-size-documents"
bucket = gcs_client.get_bucket(bucket_name)

# Define the new paths using the GCS URL format
root = f'gs://{bucket_name}'
path_questions = f'gs://{bucket_name}/training_data/v2_OpenEnded_mscoco_val2014_questions.json'
path_annotations = f'gs://{bucket_name}/training_data/v2_mscoco_val2014_annotations.json'


def load_json_from_gcs(bucket_name, blob_name):
    bucket = storage.Client().bucket(bucket_name)
    blob = bucket.blob(blob_name)
    content = blob.download_as_text()
    return json.loads(content)


def read_image_from_gcs(bucket_name, blob_name):
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)
    image_data = blob.download_as_string()
    image = Image.open(io.BytesIO(image_data))
    return image

################ arguments for Vertex AI # Setup the arguments for the trainer task -> NEED TO MODIFY ######################
parser = argparse.ArgumentParser()
parser.add_argument(
    "--model-dir", dest="model_dir", default="test", type=str, help="Model dir."
)
parser.add_argument("--lr", dest="lr", default=5e-5, type=float, help="Learning rate.")
parser.add_argument(
    "--model_name",
    dest="model_name",
    # default="dandelin/vilt-b32-finetuned-vqa",   #KIIIMMM
    default="vilt-b32-finetuned-vqa",
    type=str,
    help="Model name",
)
parser.add_argument(
    "--train_base",
    dest="train_base",
    default=False,
    action="store_true",
    help="Train base or not",
)
parser.add_argument(
    "--epochs", dest="epochs", default=10, type=int, help="Number of epochs."
)
parser.add_argument(
    "--learning_rate", dest="learning_rate", default=5e-5, type=float, help="Learning rate"
)
parser.add_argument(
    "--batch_size", dest="batch_size", default=16, type=int, help="Size of a batch."
)
parser.add_argument(
    "--wandb_key", dest="wandb_key", default="16", type=str, help="WandB API Key"
)
args = parser.parse_args()
####### UTILITY FUNCTIONS AND CLASSES #####################
def id_from_filename(filename: str) -> Optional[int]:
    match = filename_re.fullmatch(filename)
    if match is None:
        return None
    return int(match.group(1))


def collate_fn(batch):
  input_ids = [item['input_ids'] for item in batch]
  pixel_values = [item['pixel_values'] for item in batch]
  attention_mask = [item['attention_mask'] for item in batch]
  token_type_ids = [item['token_type_ids'] for item in batch]
  labels = [item['labels'] for item in batch]

  # create padded pixel values and corresponding pixel mask
  encoding = processor.image_processor.pad(pixel_values, return_tensors="pt")

  # create new batch
  batch = {}
  batch['input_ids'] = torch.stack(input_ids)
  batch['attention_mask'] = torch.stack(attention_mask)
  batch['token_type_ids'] = torch.stack(token_type_ids)
  batch['pixel_values'] = encoding['pixel_values']
  batch['pixel_mask'] = encoding['pixel_mask']
  batch['labels'] = torch.stack(labels)
  return batch


def get_score(count: int) -> float:
    return min(1.0, count / 3)


class VQADataset(torch.utils.data.Dataset):
    """VQA (v2) dataset."""

    def __init__(self, questions, annotations, processor):
        self.questions = questions
        self.annotations = annotations
        self.processor = processor

    def __len__(self):
        return len(self.annotations)

    def __getitem__(self, idx):
        # get image + text
        annotation = self.annotations[idx]
        questions = self.questions[idx]
        #image = Image.open(id_to_filename[annotation['image_id']])
        image = read_image_from_gcs(bucket_name, id_to_filename[annotation["image_id"]][len(f'gs://{bucket_name}/'):])

        text = questions['question']

        encoding = self.processor(image, text, padding="max_length", truncation=True, return_tensors="pt")
        # remove batch dimension
        for k,v in encoding.items():
          encoding[k] = v.squeeze()
        # add labels
        labels = annotation['labels']
        scores = annotation['scores']
        # based on: https://github.com/dandelin/ViLT/blob/762fd3975c180db6fc88f577cf39549983fa373a/vilt/modules/objectives.py#L301
        targets = torch.zeros(len(config.id2label))
        for label, score in zip(labels, scores):
              targets[label] = score
        encoding["labels"] = targets
        return encoding



####### PIPELINE #####################
gcs_directory = "training_data/val2014"   #NEW
blobs = bucket.list_blobs(prefix=gcs_directory)   #NEW
file_names = [blob.name for blob in blobs]        #NEW

#file_names = [f for f in tqdm(listdir(root)) if isfile(join(root, f))]
filename_re = re.compile(r".*(\d{12})\.((jpg)|(png))")

filename_to_id = {root + "/" + file: id_from_filename(file) for file in file_names}
id_to_filename = {v:k for k,v in filename_to_id.items()}

config = ViltConfig.from_pretrained("dandelin/vilt-b32-finetuned-vqa")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = ViltForQuestionAnswering.from_pretrained("dandelin/vilt-b32-mlm",
                                                 id2label=config.id2label,
                                                 label2id=config.label2id)
model.to(device)

#Questions
#data_questions = json.load(open(path_questions))
#questions = data_questions['questions']

#Annotations
#data_annotations = json.load(open(path_annotations))
#annotations = data_annotations['annotations']

data_questions = load_json_from_gcs(bucket_name, "training_data/v2_OpenEnded_mscoco_val2014_questions.json")
data_annotations = load_json_from_gcs(bucket_name, "training_data/v2_mscoco_val2014_annotations.json")
questions = data_questions['questions']
annotations = data_annotations['annotations']

#Processor
processor = ViltProcessor.from_pretrained("dandelin/vilt-b32-mlm")


# # Training Params
# ############################
model_name = args.model_name
learning_rate = args.learning_rate
batch_size = args.batch_size
epochs = args.epochs
train_base = args.train_base

# Free up memory
K.clear_session()

#Dataset
dataset = VQADataset(questions=questions[:100],
                     annotations=annotations[:100],
                     processor=processor)


wandb.login(key=args.wandb_key)

# Initialize a W&B run
wandb.init(
    project="vqa-training-vertex-ai",
    config={
        "learning_rate": learning_rate,
        "epochs": epochs,
        "batch_size": batch_size,
    },
    sync_tensorboard=True  ### ADDED LAST !!!!!!!!!!!!
)

#Train dataloader
train_dataloader = DataLoader(dataset, collate_fn=collate_fn, batch_size=batch_size, shuffle=True)

for annotation in tqdm(annotations , desc="Processing"): ### KIM ADDED , desc="Processing"
    answers = annotation['answers']
    answer_count = {}
    for answer in answers:
        answer_ = answer["answer"]
        answer_count[answer_] = answer_count.get(answer_, 0) + 1
    labels = []
    scores = []
    for answer in answer_count:
        if answer not in list(config.label2id.keys()):
            continue
        labels.append(config.label2id[answer])
        score = get_score(answer_count[answer])
        scores.append(score)
    annotation['labels'] = labels
    annotation['scores'] = scores
    

print("checkpoint-------------------------------------") 
####### TRAINING #####################

start_time = time.time()
optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)

model.train()
for epoch in range(epochs):
   print(f"Epoch: {epoch}")
   for batch in tqdm(train_dataloader):
        # get the inputs;
        batch = {k:v.to(device) for k,v in batch.items()}

        # zero the parameter gradients
        optimizer.zero_grad()

        # forward + backward + optimize
        outputs = model(**batch)
        loss = outputs.loss
        print("Loss:", loss.item())
        loss.backward()
        optimizer.step()

        WandbCallback().on_epoch_end(epoch, logs={'loss': loss.item()})

        
execution_time = (time.time() - start_time) / 60.0
print("Training execution time (mins)", execution_time)
print("Training Job Complete")

# Update W&B
wandb.config.update({"execution_time": execution_time})

#KIMMM
# Determine the directory of the current script
script_directory = os.path.dirname(os.path.abspath(__file__))
# Create a WandB model artifact
model_artifact = wandb.Artifact(model_name, type="model")

# Save the fine-tuned model to a local directory
model.save_pretrained(script_directory) #-> not saving the weights
# model_weights_file = "model_weights.pb"
# torch.save(model.state_dict(), model_weights_file)

# Add the model files to the artifact
model_artifact.add_dir(script_directory)
# model_artifact.add_file(model_weights_file, "weights_and_biases/model_weights.pb")

# #NEW TRIAL KIM
# # Save the model's weights and configuration
# model_weights_file = "model_weights.pth"
# # Determine the current working directory
# current_directory =  os.path.dirname(os.path.abspath(__file__))

# # Define the path for the model configuration file
# model_config_file = os.path.join(current_directory, "model_config.json")

# # Save the model's weights
# torch.save(model.state_dict(), model_weights_file)

# # Save the model's configuration
# model.config.save_pretrained(model_config_file)

# # Now you can log both the weights and configuration to WandB
# model_artifact = wandb.Artifact(model_name, type="model")

# model_artifact.add_file(model_weights_file, "weights_and_biases/model_weights.pth")
# # model_artifact.add_file(model_config_file, "weights_and_biases/model_config.json")


# Log the model artifact
wandb.log_artifact(model_artifact)

### END KIMMM


# Close the W&B run
wandb.run.finish()


print("Training Job Complete")







# Tensorflow
#import tensorflow as tf
#from tensorflow import keras
#from tensorflow.keras.models import Model, Sequential
#from tensorflow.keras.utils import to_categorical
#from tensorflow.python.keras import backend as K
#from tensorflow.python.keras.utils.layer_utils import count_params

# sklearn
#from sklearn.model_selection import train_test_split

# Tensorflow Hub
#import tensorflow_hub as hub

# W&B
#import wandb
#from wandb.keras import WandbCallback, WandbMetricsLogger


# Setup the arguments for the trainer task -> NEED TO MODIFY
# parser = argparse.ArgumentParser()
# parser.add_argument(
#     "--model-dir", dest="model_dir", default="test", type=str, help="Model dir."
# )
# parser.add_argument("--lr", dest="lr", default=0.001, type=float, help="Learning rate.")
# parser.add_argument(
#     "--model_name",
#     dest="model_name",
#     default="mobilenetv2",
#     type=str,
#     help="Model name",
# )
# parser.add_argument(
#     "--train_base",
#     dest="train_base",
#     default=False,
#     action="store_true",
#     help="Train base or not",
# )
# parser.add_argument(
#     "--epochs", dest="epochs", default=10, type=int, help="Number of epochs."
# )
# parser.add_argument(
#     "--batch_size", dest="batch_size", default=16, type=int, help="Size of a batch."
# )
# parser.add_argument(
#     "--wandb_key", dest="wandb_key", default="16", type=str, help="WandB API Key"
# )
# args = parser.parse_args()

# # TF Version 
# print("tensorflow version", tf.__version__)
# print("Eager Execution Enabled:", tf.executing_eagerly())
# # Get the number of replicas
# strategy = tf.distribute.MirroredStrategy()
# print("Number of replicas:", strategy.num_replicas_in_sync)

# devices = tf.config.experimental.get_visible_devices()
# print("Devices:", devices)
# print(tf.config.experimental.list_logical_devices("GPU"))

# print("GPU Available: ", tf.config.list_physical_devices("GPU"))
# print("All Physical Devices", tf.config.list_physical_devices())


# # Utils functions
# def download_file(packet_url, base_path="", extract=False, headers=None):
#     if base_path != "":
#         if not os.path.exists(base_path):
#             os.mkdir(base_path)
#     packet_file = os.path.basename(packet_url)
#     with requests.get(packet_url, stream=True, headers=headers) as r:
#         r.raise_for_status()
#         with open(os.path.join(base_path, packet_file), "wb") as f:
#             for chunk in r.iter_content(chunk_size=8192):
#                 f.write(chunk)

#     if extract:
#         if packet_file.endswith(".zip"):
#             with zipfile.ZipFile(os.path.join(base_path, packet_file)) as zfile:
#                 zfile.extractall(base_path)
#         else:
#             packet_name = packet_file.split(".")[0]
#             with tarfile.open(os.path.join(base_path, packet_file)) as tfile:
#                 tfile.extractall(base_path)
# import re
# from typing import Optional

# filename_re = re.compile(r".*(\d{12})\.((jpg)|(png))")

# # source: https://github.com/allenai/allennlp-models/blob/a36aed540e605c4293c25f73d6674071ca9edfc3/allennlp_models/vision/dataset_readers/vqav2.py#L141
# def id_from_filename(filename: str) -> Optional[int]:
#     match = filename_re.fullmatch(filename)
#     if match is None:
#         return None
#     return int(match.group(1))

# ## Download Data
# start_time = time.time()
# download_file(
#     "https://github.com/dlops-io/datasets/releases/download/v1.0/mushrooms_3_labels.zip",
#     base_path="datasets",
#     extract=True,
# )
# execution_time = (time.time() - start_time) / 60.0
# print("Download execution time (mins)", execution_time)

# # Load Data
# base_path = os.path.join("datasets", "mushrooms")
# label_names = os.listdir(base_path)
# print("Labels:", label_names)

# # Number of unique labels
# num_classes = len(label_names)
# # Create label index for easy lookup
# label2index = dict((name, index) for index, name in enumerate(label_names))
# index2label = dict((index, name) for index, name in enumerate(label_names))

# # Generate a list of labels and path to images
# data_list = []
# for label in label_names:
#     # Images
#     image_files = os.listdir(os.path.join(base_path, label))
#     data_list.extend([(label, os.path.join(base_path, label, f)) for f in image_files])

# print("Full size of the dataset:", len(data_list))
# print("data_list:", data_list[:5])


# #### Kim's code
# #trying to do the same with data questions
# start_time = time.time()
# download_file(
#     "https://s3.amazonaws.com/cvmlp/vqa/mscoco/vqa/v2_Questions_Val_mscoco.zip",
#     base_path="datasets",
#     extract=True,
# )
# execution_time = (time.time() - start_time) / 60.0
# print("Download execution time (mins)", execution_time)
# directory_path = "datasets"
# # List the files in the directory
# files = os.listdir(directory_path)

# # Assuming you want to open the first JSON file in the list
# if len(files) > 0:
#     first_json_file = files[0]
#     json_file_path = os.path.join(directory_path, first_json_file)

#     # Opening JSON file
#     with open(json_file_path, 'r') as f:
#         # Return JSON object as a dictionary
#         data_questions = json.load(f)
#         print(data_questions.keys())
# else:
#     print("No JSON files found in the 'datasets' directory.")

# #trying to do the same with image questions


# # Load X & Y
# # Build data x, y
# data_x = [itm[1] for itm in data_list]
# data_y = [itm[0] for itm in data_list]
# print("data_x:", len(data_x))
# print("data_y:", len(data_y))
# print("data_x:", data_x[:5])
# print("data_y:", data_y[:5])

# # Split Data
# test_percent = 0.10
# validation_percent = 0.2

# # Split data into train / test
# train_validate_x, test_x, train_validate_y, test_y = train_test_split(
#     data_x, data_y, test_size=test_percent
# )

# # Split data into train / validate
# train_x, validate_x, train_y, validate_y = train_test_split(
#     train_validate_x, train_validate_y, test_size=test_percent
# )

# print("train_x count:", len(train_x))
# print("validate_x count:", len(validate_x))
# print("test_x count:", len(test_x))

# # Login into wandb
# wandb.login(key=args.wandb_key)


# # Create TF Datasets
# def get_dataset(image_width=224, image_height=224, num_channels=3, batch_size=32):
#     # Load Image
#     def load_image(path, label):
#         image = tf.io.read_file(path)
#         image = tf.image.decode_jpeg(image, channels=num_channels)
#         image = tf.image.resize(image, [image_height, image_width])
#         return image, label

#     # Normalize pixels
#     def normalize(image, label):
#         image = image / 255
#         return image, label

#     train_shuffle_buffer_size = len(train_x)
#     validation_shuffle_buffer_size = len(validate_x)

#     # Convert all y labels to numbers
#     train_processed_y = [label2index[label] for label in train_y]
#     validate_processed_y = [label2index[label] for label in validate_y]
#     test_processed_y = [label2index[label] for label in test_y]

#     # Converts to y to binary class matrix (One-hot-encoded)
#     train_processed_y = to_categorical(
#         train_processed_y, num_classes=num_classes, dtype="float32"
#     )
#     validate_processed_y = to_categorical(
#         validate_processed_y, num_classes=num_classes, dtype="float32"
#     )
#     test_processed_y = to_categorical(
#         test_processed_y, num_classes=num_classes, dtype="float32"
#     )

#     # Create TF Dataset
#     train_data = tf.data.Dataset.from_tensor_slices((train_x, train_processed_y))
#     validation_data = tf.data.Dataset.from_tensor_slices(
#         (validate_x, validate_processed_y)
#     )
#     test_data = tf.data.Dataset.from_tensor_slices((test_x, test_processed_y))

#     #############
#     # Train data
#     #############
#     # Apply all data processing logic
#     train_data = train_data.shuffle(buffer_size=train_shuffle_buffer_size)
#     train_data = train_data.map(load_image, num_parallel_calls=tf.data.AUTOTUNE)
#     train_data = train_data.map(normalize, num_parallel_calls=tf.data.AUTOTUNE)
#     train_data = train_data.batch(batch_size)
#     train_data = train_data.prefetch(tf.data.AUTOTUNE)

#     ##################
#     # Validation data
#     ##################
#     # Apply all data processing logic
#     validation_data = validation_data.shuffle(
#         buffer_size=validation_shuffle_buffer_size
#     )
#     validation_data = validation_data.map(
#         load_image, num_parallel_calls=tf.data.AUTOTUNE
#     )
#     validation_data = validation_data.map(
#         normalize, num_parallel_calls=tf.data.AUTOTUNE
#     )
#     validation_data = validation_data.batch(batch_size)
#     validation_data = validation_data.prefetch(tf.data.AUTOTUNE)

#     ############
#     # Test data
#     ############
#     # Apply all data processing logic
#     test_data = test_data.map(load_image, num_parallel_calls=tf.data.AUTOTUNE)
#     test_data = test_data.map(normalize, num_parallel_calls=tf.data.AUTOTUNE)
#     test_data = test_data.batch(batch_size)
#     test_data = test_data.prefetch(tf.data.AUTOTUNE)

#     return (train_data, validation_data, test_data)


# def build_mobilenet_model(
#     image_height, image_width, num_channels, num_classes, model_name, train_base=False
# ):
#     # Model input
#     input_shape = [image_height, image_width, num_channels]  # height, width, channels

#     # Load a pretrained model from keras.applications
#     tranfer_model_base = keras.applications.MobileNetV2(
#         input_shape=input_shape, weights="imagenet", include_top=False
#     )

#     # Freeze the mobileNet model layers
#     tranfer_model_base.trainable = train_base

#     # Regularize using L1
#     kernel_weight = 0.02
#     bias_weight = 0.02

#     model = Sequential(
#         [
#             tranfer_model_base,
#             keras.layers.GlobalAveragePooling2D(),
#             keras.layers.Dense(
#                 units=128,
#                 activation="relu",
#                 kernel_regularizer=keras.regularizers.l1(kernel_weight),
#                 bias_regularizer=keras.regularizers.l1(bias_weight),
#             ),
#             keras.layers.Dense(
#                 units=num_classes,
#                 activation="softmax",
#                 kernel_regularizer=keras.regularizers.l1(kernel_weight),
#                 bias_regularizer=keras.regularizers.l1(bias_weight),
#             ),
#         ],
#         name=model_name + "_train_base_" + str(train_base),
#     )

#     return model


# def build_model_tfhub(
#     image_height, image_width, num_channels, num_classes, model_name, train_base=False
# ):
#     # Model input
#     input_shape = [image_height, image_width, num_channels]  # height, width, channels

#     # Handle to pretrained model
#     handle = "https://tfhub.dev/google/imagenet/mobilenet_v2_100_224/feature_vector/4"

#     # Regularize using L1
#     kernel_weight = 0.02
#     bias_weight = 0.02

#     model = Sequential(
#         [
#             keras.layers.InputLayer(input_shape=input_shape),
#             hub.KerasLayer(handle, trainable=train_base),
#             keras.layers.Dense(
#                 units=64,
#                 activation="relu",
#                 kernel_regularizer=keras.regularizers.l1(kernel_weight),
#                 bias_regularizer=keras.regularizers.l1(bias_weight),
#             ),
#             keras.layers.Dense(
#                 units=num_classes,
#                 activation="softmax",
#                 kernel_regularizer=keras.regularizers.l1(kernel_weight),
#                 bias_regularizer=keras.regularizers.l1(bias_weight),
#             ),
#         ],
#         name=model_name + "_train_base_" + str(train_base),
#     )

#     return model


# print("Train model")
# ############################
# # Training Params
# ############################
# model_name = args.model_name
# learning_rate = 0.001
# image_width = 224
# image_height = 224
# num_channels = 3
# batch_size = args.batch_size
# epochs = args.epochs
# train_base = args.train_base

# # Free up memory
# K.clear_session()

# # Data
# train_data, validation_data, test_data = get_dataset(
#     image_width=image_width,
#     image_height=image_height,
#     num_channels=num_channels,
#     batch_size=batch_size,
# )

# if model_name == "mobilenetv2":
#     # Model
#     model = build_mobilenet_model(
#         image_height,
#         image_width,
#         num_channels,
#         num_classes,
#         model_name,
#         train_base=train_base,
#     )
#     # Optimizer
#     optimizer = keras.optimizers.SGD(learning_rate=learning_rate)
#     # Loss
#     loss = keras.losses.categorical_crossentropy
#     # Print the model architecture
#     print(model.summary())
#     # Compile
#     model.compile(loss=loss, optimizer=optimizer, metrics=["accuracy"])
# elif model_name == "tfhub_mobilenetv2":
#     # Model
#     model = build_model_tfhub(
#         image_height,
#         image_width,
#         num_channels,
#         num_classes,
#         model_name,
#         train_base=train_base,
#     )
#     # Optimizer
#     optimizer = keras.optimizers.SGD(learning_rate=learning_rate)
#     # Loss
#     loss = keras.losses.categorical_crossentropy
#     # Print the model architecture
#     print(model.summary())
#     # Compile
#     model.compile(loss=loss, optimizer=optimizer, metrics=["accuracy"])

# # Initialize a W&B run
# wandb.init(
#     project="mushroom-training-vertex-ai",
#     config={
#         "learning_rate": learning_rate,
#         "epochs": epochs,
#         "batch_size": batch_size,
#         "model_name": model.name,
#     },
#     name=model.name,
# )

# # Train model
# start_time = time.time()
# training_results = model.fit(
#     train_data,
#     validation_data=validation_data,
#     epochs=epochs,
#     callbacks=[WandbCallback()],
#     verbose=1,
# )
# execution_time = (time.time() - start_time) / 60.0
# print("Training execution time (mins)", execution_time)

# # Update W&B
# wandb.config.update({"execution_time": execution_time})
# # Close the W&B run
# wandb.run.finish()


# print("Training Job Complete")