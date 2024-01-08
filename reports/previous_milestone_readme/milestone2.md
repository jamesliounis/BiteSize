# BiteSize - Generative AI-based Question Generator 

## AC215 - Milestone 2

**Team Members**  
Elie Attias, James Liounis, Hope Neveux, Kimberly Llajaruna-Peralta, Michael Samcec

**Group Name**  
BiteSize

**Project**  
In this project, we aim to develop an application that generates multiple choice questions from an uploaded document. This tool can aid educators in quickly preparing assessment materials, and students in better understanding the assigned materials in an interactive manner.

Repository Structure
----------------------

```
.
├── LICENSE
├── README.md
├── notebooks
│   └── basecode.ipynb
├── references
├── reports
├── requirements.txt
└── src
    ├── docker-compose.yml
    ├── inference
    │   ├── Dockerfile
    │   ├── infer.py
    │   ├── install_requirements.sh
    │   └── requirements.txt
    └── preprocessing_question_gen
        ├── Dockerfile
        ├── generate_mcq.py
        ├── infer.py
        ├── install_requirements.sh
        └── requirements.txt

```

----------------------------

### Inference Container

This container provides question generation capabilities using generative AI / transformer-based models sourced from [HuggingFace](https://huggingface.co).  
Input: Uploaded document stored in a GCS bucket, and pre-processed using capabilities from `generate_mcq.py`.  
Output: Generated multiple choice questions.

1. `src/inference/infer.py` - Utilizes pre-trained models to generate questions from the provided content.
2. `src/inference/requirements.txt` - Dependencies for the inference process.
3. `src/inference/Dockerfile` - Initiates with `python:3.8-slim-buster` and sets up the environment for inference.

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

### Running the Inference Container

1. Build the Docker image:
```bash
docker build -t bitesize_inference ./inference
```

2. Run the container:
```bash
docker run -v [PATH TO YOUR LOCAL DATA]:/data -v [PATH TO YOUR SECRETS]:/secrets bitesize_inference
```

### Preprocessing Question Generation Container

This container preprocesses data for the question generation pipeline.  
Input: Raw data.  
Output: Processed data for inference.

1. `src/preprocessing_question_gen/generate_mcq.py` - Facilitates multiple choice question generation.
2. `src/preprocessing_question_gen/requirements.txt` - Python package dependencies.
3. `src/preprocessing_question_gen/Dockerfile` - Initiates with `python:3.8-slim-buster`.

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

If you intend to run both containers simultaneously or manage their communication, use Docker Compose:
```bash
docker-compose up
```

## Notebooks
This folder contains exploratory data analysis (EDA), crucial insights, reports, and visualizations.
