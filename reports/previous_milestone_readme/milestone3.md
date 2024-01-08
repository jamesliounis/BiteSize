x# BiteSize - Generative AI-based Question Generator 

## AC215 - Milestone 3

**Team Members**  
Elie Attias, James Liounis, Hope Neveux, Kimberly Llajaruna Peralta, Michael Sam 

**Group Name**  
BiteSize

**Project**  
In this project, we aim to develop an application that generates multiple choice questions from an uploaded document. This tool can aid educators in quickly preparing assessment materials, and students in better understanding the assigned materials in an interactive manner.

## Repository Structure

```
.
├── LICENSE
├── README.md
├── deployment_scripts
│   ├── Dockerfile
│   ├── app.py
│   ├── build_tag_push.sh
│   ├── deploy_vertex_model.py
│   └── requirements.txt
├── notebooks
│   ├── basecode.ipynb
│   └── vaq.ipynb
├── references
├── reports
├── requirements.txt
└── src
    ├── docker-compose.yml
    └── preprocessing_question_gen
        ├── Dockerfile
        ├── generate_mcq.py
        ├── infer.py
        ├── install_requirements.sh
        └── requirements.txt
```

## Instructions for Running Containers

### Prerequisites

1. Ensure Docker and Docker Compose are installed:
   - [Docker](https://docs.docker.com/get-docker/)
   - [Docker Compose](https://docs.docker.com/compose/install/)

2. Clone the repository:
```bash
git clone git@github.com:jamesliounis/BiteSize.git
cd BiteSize
```

3. Navigate to the `src` directory:
```bash
cd src
```

### Preprocessing Question Generation Container

This container preprocesses data for the question generation pipeline. 

Input: Raw data.  
Output: Processed data for inference.

1. `src/preprocessing_question_gen/generate_mcq.py` - Facilitates multiple choice question generation.
2. `src/preprocessing_question_gen/infer.py` - Facilitates inference.
3. `src/preprocessing_question_gen/requirements.txt` - Python package dependencies.
4. `src/preprocessing_question_gen/Dockerfile` - Initiates with `python:3.8-slim-buster`.

Please note that at this time our `infer.py` script communicates with a `Llama-2-7b` model which has been deployed on GCP's VertexAI. For this, we are using an open-source version of Llama directly from HuggingFace, which can be found [here](https://huggingface.co/openlm-research/open_llama_7b_v2).


### Running the Preprocessing Question Generation Container

1. Build the Docker image:
```bash
docker build -t bitesize_question_gen ./preprocessing_question_gen
```

2. Run the container:
```bash
docker run -v [PATH TO YOUR LOCAL DATA]:/data -v [PATH TO YOUR SECRETS]:/secrets bitesize_question_gen
```

**Note**: Replace the paths in the above commands as necessary for your local setup.

### Using Docker Compose (Optional)

You may also use Docker Compose to run the container via:
```bash
docker-compose up
```

## Deployment Scripts Explanation

The deployment_scripts directory contains scripts and configurations for deploying and managing the BiteSize application on cloud platforms, particularly Google Cloud's Vertex AI.

`Dockerfile`
This file provides instructions for Docker to build an image for the BiteSize application. It uses a PyTorch base image with CUDA support and installs necessary Python packages from `requirements.txt`. The application is then started using `handler.py`.

`build_tag_push.sh`
This shell script automates the process of building the Docker image, tagging it, and pushing it to the Google Cloud's Container Registry.

`handler.py`
This Python script is the core of the application. It sets up a Flask application with two endpoints:

i. A POST endpoint that accepts text and uses a pre-trained model to generate responses.
ii. A GET endpoint that provides information about the deployed model.
The Llama model (from the transformers library on HuggingFace) is utilized for text generation.

`deploy_vertex_model.py`
This is an automation script for deploying machine learning models on Google's Vertex AI platform. It handles tasks such as:

- Authenticating with Google Cloud.
- Uploading the model to Vertex AI.
- Creating or fetching an existing endpoint.
- Deploying the model to the specified endpoint.
- It can be used interactively or by providing command-line arguments.

`requirements.txt`
Lists the Python package dependencies required to run the BiteSize application. These packages are installed when building the Docker image. It includes packages for working with Google Cloud, the transformers library for the Llama model, and others for processing and serving.

## Notebooks
This folder contains exploratory data analysis (EDA), crucial insights, reports, and visualizations.

### VAQ notebook
We've recently introduced a notebook named "VAQ" that centers on the Visual Question Answering (VQA) model. The VQA model is engineered to respond to queries pertaining to images. The primary aim of this functionality is to enable users to upload an image, after which the model will generate questions based on the image, thereby allowing users to test their knowledge.

Contained within the files is a function that necessitates the image file's location for image loading. Additionally, there are three other functions that correspond to three distinct models from Hugging Face. These models include:

1. "vit-gpt2-coco-en," which functions as a caption generator. It takes the image as input and produces a descriptive caption for the image.

2. We're also delving into the "vilt-b32-finetuned-vqa" model, which specializes in offering concise responses to user-generated questions concerning the images.

3. The final model in our investigation is the "Zero Shot" model, boasting a remarkable 2.7 billion parameters, representing a state-of-the-art achievement in this field. Currently , this model is too big to run locally but we expect it to perform the best out of the three models. 

For the next milestone, we hope to deploy these models too.




