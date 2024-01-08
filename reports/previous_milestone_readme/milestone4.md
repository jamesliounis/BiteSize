# BiteSize: Generative AI-based Question Generator
*Harvard University AC215 -- MLOps*

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

# Table of Contents
1. [About](#about)
    - [Group Name](#group-name)
    - [Team Members](#team-members)
    - [Project Abstract](#project)
    - [Example Uses](#example-uses)
    - [Repository Structure](#repository-structure)
2. [OpenLLaMA-7b For Textual Test Generation](#openllama-7b-for-textual-test-generation)
    - [Optimizing the Model](#step-1-optimizing-the-model)
    - [Building the Model](#step-2-building-the-model)
    - [Deploying the Optimized Model](#step-3-deploying-optimized-model)
    - [Building the Streamlit App](#step-4-building-the-streamlit-app)
3. [ViLT-32b for Visual Question Answering Test Generation](#vilt-32b-for-visual-question-answering-test-generation)
    - [Data Loading](#step-1-data-loading)
    - [Model Deployment](#step-2-model-deployment)
4. [Custom Objects](#custom-objects)
    - [MCQGenerator](#mcqgenerator)
    - [TestBank](#testbank)
    - [LlamaTextGenerator](#llamatextgenerator)
    - [Bucket](#bucket)
    - [Errors](#errors)
5. [Notebooks](#notebooks)

# About

### **Group Name**  
+ BiteSize

### **Team Members**  
+ James Liounis ([jamesliounis@g.harvard.edu](mailto:jamesliounis@g.harvard.edu))
+ Hope Neveux ([hopeneveux@g.harvard.edu](mailto:hopeneveux@g.harvard.edu))
+ Kimberly Llajaruna Peralta ([kllajarunaperalta@g.harvard.edu](mailto:kllajarunaperalta@g.harvard.edu))
+ Michael Sam Chec ([msamchec@g.harvard.edu](mailto:msamchec@g.harvard.edu))


### **Project**  

![Logo](./assets/logo/logo-no-background.png)

+ *[Website](https://bitesize-jsrdxhl2pa-ue.a.run.app/)*
+ *[Midterm Presentation](./reports/BiteSize_Presentation.pptx)*

Faster and more efficient methods for extracting important knowledge are crucial for the modern student and educator. By automating question generation from course materials, students using the *BiteSize* application save time and learn faster and more effectively. 

We recognize every student is different. Thus, we've built *BiteSize* to create tests of your customization of difficulty, repeats, and test length. We also recognize the way information is presented across courses differs. *BiteSize* can test you on the textual information of your handouts (pdfs, docxs, and other formats) as well as uploaded graphs / figures. 

*BiteSize* can aid educators in quickly preparing assessment materials and students in better understanding their materials in an interactive manner.

### Example Uses 

|*For the Student* | *For the Teacher*|
|---------------|-----------------|
| Study for an exam | Prepare a study guide |
| Get a better understanding of your notes / handout / reading | Prepare an educational trivia game |
| Learn how to pick out information from graphs / charts / pictures quickly | Ensure critical concepts stand out |
| ... | ...|

![Pitch](./reports/bitesize_overview_arch.png)

### Repository Structure

----------------------

```
.
├── LICENSE
├── README.md
├── docker-compose.yml
├── assets
│   ├── logos
│   │   ├── block_icon.png
│   │   ├── book-logo.png
│   │   ├── logo-black.png
│   │   ├── logo-color.png
│   │   ├── logo-no-background.png
│   │   └── logo-white.png
├── models
│   ├── deploy
│   │   ├── build_model
│   │   │   ├── Dockerfile
│   │   │   ├── build_and_push.sh
│   │   │   ├── main.py
│   │   │   └── requirements.txt
│   │   ├── deploy_model
│   │   │   ├── Dockerfile
│   │   │   ├── deploy_to_vertex.py
│   │   │   ├── requirements.txt
│   │   │   └── run_all.sh
│   │   └── kubernetes
│   │       ├── Dockerfile
│   │       ├── config.yaml
│   │       ├── create_docker_image.py
│   │       ├── create_kubernetes_cluster.sh
│   │       ├── deploy_llama.ipynb
│   │       ├── deploy_llama.py
│   │       ├── install_nvidia_drivers.sh
│   │       ├── kubernetes_deployment.yaml
│   │       └── requirements.txt
│   └── prune_and_quantize
│       ├── Dockerfile
│       ├── configs
│       │   └── llama_computational_graph.json
│       ├── requirements.txt
│       └── scripts
│           └── prune_model.py
├── notebooks
│   ├── basecode.ipynb
│   └── vaq.ipynb
├── references
├── reports
│   ├── architecture_diagram_v2
│   ├── BiteSize_Presentation.pptx
│   ├── memory_usage_analysis.png
│   └── vqa_architecture.png 
├── requirements.txt
├── src
│   ├── deploy_interactive_app
│   │   ├── Dockerfile
│   │   └── deploy_container.sh
│   └── preprocessing_question_gen
│       ├── Dockerfile
│       ├── app.py
│       ├── customerrors.py
│       ├── gcp.py
│       ├── generate_config.sh
│       ├── generate_mcq.py
│       ├── infer.py
│       ├── requirements.txt
│       └── testbank.py
└── utils
    ├── check_model_health
    │   ├── app.py
    │   ├── check_model_health.py
    │   └── request.json
    └── delete_endpoints.sh
```
-----------------------


This repository is structured to seamlessly *build*, *deploy*, and *optimize* machine learning models for generating questions from documents. We have structured it in a way that follows the process that we followed ourselves. The easiest way to carry out the process from building and deploying the model to deploying a fully functional app would be to follow these simple steps:


1. Ensure Docker and Docker Compose are installed:
   - [Docker](https://docs.docker.com/get-docker/)
   - [Docker Compose](https://docs.docker.com/compose/install/)

2. Clone the repository (you may want to do this in a virtual environment):

```bash
git clone git@github.com:jamesliounis/BiteSize.git
cd BiteSize
```

3. Run the Docker compose command that will initiate a multi-stage process involving building and running several Docker containers, each designed for a specific task in the workflow. The `--build` flag ensures that Docker images for each service are built (or rebuilt) before starting the containers. 

```bash
# Build and run containers with Docker Compose
docker-compose up --build
```

# OpenLLaMA-7b for Textual Test Generation 
Please refer to the diagram below for an overview of our current infrastructure. 

![Architecture Diagram](./reports/architecture_diagram_v2.png)

The `models` directory is dedicated to all operations concerning the model. You can execute all the workflow steps of this part by simply running:

```bash
cd ./models/deploy/deploy_model/
./run_all.sh
```

Our workflow followed the following steps:

## **Step 1: Optimizing the Model**

Previously not able to get inference in a timely fashion from the deployed Llama-7B, and when we were we were using too large of an instance, which was proving itself way too expensive in terms of both computation and monetary costs. The pruning process in our script zeroes out weights below a certain threshold without reducing the model's memory footprint, as it doesn't eliminate weights but merely sets some to zero. However, this seems to have potentially improved computational efficiency and inference time while actually increasing memory usage. 

![Memory Usage Analysis](./reports/memory_usage_analysis.png)

It is the second part of our process where we performed dynamic quantization, which reduced the model's size more substantially by converting weights to a lower precision format `(torch.qint8)`, that led to lower memory requirements and possibly faster inference. Deploying the model on GCP or similar platforms further benefits from efficient management of memory and compute resources, likely optimizing the performance of the quantized and pruned model. We were able to serve the model with a simple `n1-standard-4` (4 vCPUs, 30GB memory) as opposed to the original `n1-standard-16` that we were using (16 vCPUs, 60 GB).
Further analysis would probably be needed in this part where we would also compare the effect of deploying without pruning and with quantization or vice-versa. However, due to computational constraints we have decided to push this to a later stage. 

Relevant scripts: 

+ `prune_and_quantize`: Scripts to prune and quantize the model, with a view to making it lighter and faster.
+ `configs`: Contains configuration files like Llama's computational graph. 

>**Note**: Replace the paths in the above commands as necessary for your local setup.

## **Step 2: Building the Model**

This part involved re-factoring previous code to deploy optimized model weights directly from a GCS bucket. 

`build_model`: Scripts and Docker configurations to build the machine learning model.

- `Dockerfile`: Defines the environment for building the model.
- `build_and_push.sh`: Script to build the Docker image and push it to a repository.
- `main.py`: The main script where the model is built.
- `requirements.txt`: Dependencies specific to building the model.

## **Step 3: Deploying optimized model**

Once we had everything in place, we deployed the model.

`deploy_model`: Scripts and Docker configurations related to deploying the model.

- `Dockerfile`: Defines the environment for deploying the model.
- `deploy_to_vertex.py`: Script to deploy the model to Google Cloud Vertex AI.
- `requirements.txt`: Dependencies required for deployment.
- `run_all.sh`: Utility script that encapsulates the entire deployment process.


## **Step 4: Building the Streamlit app**

### **`src`**:

We first proceeded in refactoring the code for our scripts to interact with a deployed model. This involved heavily changing the format to adapt to the manner in which the inference requests were sent and then formatting the output appropriately. 

The `src` directory houses the source code for deploying an interactive application and preprocessing for question generation:

`preprocessing_question_gen`: Code and assets related to data preprocessing and question generation.

- `Dockerfile`: Defines the environment for preprocessing and question generation.
- `BiteSize_logo.png`: Logo asset for the application or tool.
- `app.py`: Main application script.
- `generate_config.sh`: Script to generate config.json file which is necessary for authentication with Vertex AI endpoint. 
- `generate_mcq.py`: Script to generate multiple-choice questions.
- `infer.py`: Script to make inferences or predictions.
- `requirements.txt`: Dependencies specific to this module.


`deploy_interactive_app`: Scripts and Docker configurations for deploying the interactive app:

- `Dockerfile`: Defines the environment.
- `deploy_container.sh`: Script to deploy the Docker container for the app to Google Cloud Run.

`kubernetes`: Contains scripts and configurations for deploying the model on a Kubernetes cluster. We decided against this approach despite its simplicity as we did not have enough GPUs at the time to satisfy the minimum GPU requirement to build a 3-node GPU cluster. Feel free to visit the directory to see all the code pertaining to this form of deployment. 

### **`utils`**:
The utils directory contains utility scripts and tools:

`check_model_health`: Tools to check the health or status of the deployed model.
`app.py`: Possibly a web app or interface to check model health.
`check_model_health.py`: Script that performs the health check.
`request.json`: Sample request file.
`delete_endpoints.sh`: A utility script to delete endpoints, possibly cleaning up after deployments.


# ViLT-32b for Visual Question Answering Test Generation
Please refer to the diagram below for an overview of our current infrastructure. 

![VQA Architcture](./reports/vqa_architecture.png)

## **Step 1: Data loading**
For our model, as we wanted to generate questions based on images, we decided to use the [ViLT-32b] model from Hugging Face.

In order to fine tune our model, we first need to load the data. We used the [VQA dataset](https://visualqa.org/download.html) for this purpose. The dataset is available in two formats: `mscoco` and `abstract_v002`. We chose to use the `mscoco` format as it is more widely used and has more data.

Once we obtained the data, we put it on a GCP bucket. From there, we were able to traine the model as you can see in the file src/vqa/training branch.
Some of the files in this branch are:
- `task.py`: This file contains the code to train the model. It also contains the code to load the data from the GCP bucket and the model.
- `cli.sh`: This file is used to run the `train.py` file on a GCP VM. It also contains the parameters that we used to train the model.
- `dockerfile`: This file is used to create a docker image that contains all the dependencies needed to train the model.

Due to quota constraints, we decide it to run it for 10 epochs. 

Here it is the graph of the loss  as given by WandB:

![Training](./reports/finetune.jpeg)

## **Step 2: Model Deployment**
To being able to infere, we first needed to upload the weights into a bucket. The code for that is still in progress and on the branch `src/vqa/deployment`.

Some of the most important files from there are:
- `cli.py` : this file is where we retrieve the model weight after training.
- `docker-shell.sh`: this file is used to create a docker image that contains all the dependencies needed to obtain the weights.

The model is available in the GCP bucket `gs://vqa-app-models-demo`.  The deployment process it is still in progress.



# Custom Objects

## `MCQGenerator`
> Note: Located in `generate_mcq.py`

This is the interface for users which...

1. Processes the textual information into something our model can use to create custom tests
2. Create a `TestBank`, which holds all the possible questions provided from the inference call to our hosted mode on Vertex AI
3. Format the individual tests returned by `TestBank`

## `TestBank`

This object allows us to anchor a text to a TestBank object, which can store multiple question banks of Multiple-Choice Questions, Short Answers, Mixed Formats, and Custom Prompts. It contains it's own instantiation of the `LLamaTextGenerator`, for which we use specific functions pre-loaded with prompts to generate the entire question bank for our 4 outlined options. 

Short documents inherently generate fewer questions to maintains quality of the questions. 

The question bank is generated all at once for every textual document upload and contains questions of 3-tiered difficulty: Easy, Medium, and Difficult. These are saved to the particular instatiation of the `TestBank` object. This strategy ensures we inference the deployed model only once, thus optimizing the actual test generation to be a standard retrieval from storage. 

### Explicitly Handled Special Cases

| _Situation_ | _Behavior_ |
| ----------- | ---------- |
| User wants a test of unseen question but has gone through them all | (1) Inform them  (2) Reset the unseen question to entire question bank |
|  User wants unseen questions only but they want more questions than are available | (1) Inform them  (2) Make a shorter test including all the questions in the question bank by re-assigning number of questions argument|
| User asked for more questions than they have left in the unseen set | (1) Inform them  (2) Make a test out of the remaining unseen questions by re-assigning number of questions argument|
|  User tries to enter something other than a single number for their number of questions argument | (1) Inform them through `TypeError` |

## `LlamaTextGenerator`
> Note: Located in `infer.py`

Connects to the Vertex AI deployment of our pruned and dynamically quantized verson of OpenLLaMA-7b. Also sends prediction requests based on the call to build the respective question bank from `TestBank` as indicated by the user interacting with the interface `MCQGenerator`.

## `Bucket`
> Note: Located in `gcp.py`

Rather than needing to call the client mutliple times to connect to our GCP bucket with documents, we can store the information and important methods for listing and getting files in this object.  Has the benefit of making our source code more self-documenting.

## Errors

### `OverwriteError`
> Note: Located in `customerrors.py`

This is a custom `Exception` which is raised in the specific development case when the `QuestionGenerator` has text but our methods is trying to re-assign a document to an already instantaited object. 


### `DocumentLength`
> Note: Located in `customerrors.py`

This is a custom `Exception` which is raised in the specific user case when the `TestBank` is asked to create a question bank from text that is too short to make a meaningful quiz from. 

### `UnknownTestType`
> Note: Located in `customerrors.py`

This is a custom `Exception` which is raised in the specific developed case when the `MCQGenerator` that is fed something other than mcq, short answer, or custom when building a question bank. 

# Notebooks
This folder contains exploratory data analysis (EDA), crucial insights, reports, visualizations, and initial code testing.
