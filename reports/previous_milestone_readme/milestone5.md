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
6. [Application Design Document](#application-design-document)
    - [Problem Statement and Solution](#problem-statement-and-solution)
    - [Solution Architecture](#solution-architecture)
    - [Technical Architecture](#technical-architecture)
        - [Frontend](#building-the-frontend-part-of-the-application)
        - [Backend](#building-the-backend-part-of-the-application)
    - [User Interface](#user-interface)

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
├── cleanup.sh
├── runall.sh
├── requirements.txt
├── docker-compose.yml
├── backend
│   ├── Dockerfile  
│   ├── __init__.py
│   ├── main.py
│   ├── requirements.txt
│   ├── run.sh
│   └── app
│       ├── __init__.py
│       └── api.py
├── assets
│   ├── logos
│   │   ├── block_icon.png
│   │   ├── book-logo.png
│   │   ├── logo-black.png
│   │   ├── logo-color.png
│   │   ├── logo-no-background.png
│   │   └── logo-white.png
├── frontend
│   ├── Dockerfile
│   ├── deploy.sh
│   ├── run.sh
│   ├── my-app
│   │   ├── public
│   │   │   ├── book-logo.png
│   │   │   ├── favicon.ico
│   │   │   ├── hope.jpg
│   │   │   ├── kim.jpg
│   │   │   ├── michael.jpg
│   │   │   ├── james.jpg
│   │   │   ├── index.html
│   │   │   ├── logo-black-color.png
│   │   │   ├── logo-color.png
│   │   │   ├── logo-no-background.png
│   │   │   ├── logo192.png
│   │   │   ├── logo512.png
│   │   │   ├── manifest.json
│   │   │   ├── paper.png
│   │   │   ├── robots.txt
│   │   │   └── upload.png
│   │   └── src
│   │       ├── App.js
│   │       ├── index.js
│   │       ├── reportWebVitals.js
│   │       ├── setupTests.js
│   │       ├── README.md
│   │       ├── components
│   │       │   ├── grading_request.js
│   │       │   ├── question_gen_request.js
│   │       │   ├── Loading.js
│   │       │   ├── MainContent.js
│   │       │   ├── Navigation.js
│   │       │   ├── SAQuestion.js
│   │       │   ├── TCard.js
│   │       │   └── TestType.js
│   │       ├── css
│   │       │   ├── App.css
│   │       │   ├── index.css
│   │       │   ├── Navbar.css
│   │       │   ├── TMC.css
│   │       │   └── Upload.css
│   │       └── pages
│   │           ├── About.js
│   │           ├── Finish.js
│   │           ├── MCQCard.js
│   │           ├── SACard.js
│   │           └── Upload.js
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
│   ├── about.png
│   ├── application_design.pptx
│   ├── architecture_diagram_v2.png
│   ├── architecture_diagram.pptx
│   ├── architecture_diagram_v2.pptx
│   ├── bitesize_overview_arch.png
│   ├── BiteSize_Presentation.pptx
│   ├── feedback.png
│   ├── finetune.jpeg
│   ├── frontend_mockdes_v1.pdf
│   ├── home.png
│   ├── kubernetes_cluster.png
│   ├── learn.png
│   ├── mcq.png
│   ├── memory_usage_analysis.png
│   ├── short.png
│   ├── sol1.png
│   ├── sol2.png
│   ├── tech.png
│   └── vqa_architecture.png 
├── requirements.txt
├── src
│   ├── build_backend
│   │   ├── deploy
│   │   │   ├── deploy_to_k8s.sh
│   │   │   ├── deploy_to_k8s.yaml
│   │   │   ├── scheduler_config.sh
│   │   │   └── roles_and_permissions
│   │   │       ├── deployment-role.yaml
│   │   │       ├── deployment-rolebinding.yaml
│   │   │       ├── pod-reader-role.yaml
│   │   │       └── read-pods-binding.yaml
│   │   ├── generate_test
│   │   │   ├── Dockerfile
│   │   │   ├── generate_test.py
│   │   │   ├── infer.py
│   │   │   └── requirements.txt
│   │   ├── grade_and_explain
│   │   │   ├── Dockerfile
│   │   │   ├── autograder_api.py
│   │   │   ├── infer_explanation.py
│   │   │   └── requirements.txt
│   │   └── post_requests
│   │       ├── generate_questions
│   │       │   ├── index.html
│   │       │   ├── question_gen_requests.js
│   │       │   └── question_gen_requests.py
│   │       ├── grade
│   │       │   ├── grading_request.js
│   │       │   └── grading_request.py
│   │       ├── text_extraction
│   │       │   ├── Dockerfile
│   │       │   ├── deploy_to_cloud_run.sh
│   │       │   ├── extract_text.py
│   │       │   └── requirements.txt
│   │       └── utils
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
Please refer to the diagram below for an overview of our proposed infrastructure. 

![VQA Architcture](./reports/vqa_architecture.png)

## **Step 1: Data loading and fine-tuning**
For our model, we wanted to generate questions based on images, and we explored the use of the [ViLT-32b] model from Hugging Face. 

We fine tuned our model. To achieve so, we first needed to load the data. We used the [VQA dataset](https://visualqa.org/download.html) for this purpose. The dataset is available in two formats: `mscoco` and `abstract_v002`. We chose to use the `mscoco` format as it is more widely used and has more data.

Once we obtained the data, we put it on a GCP bucket. From there, we were able to traine the model as you can see in the file src/vqa/training branch.
Some of the files in this branch are:
- `task.py`: This file contains the code to train the model. It also contains the code to load the data from the GCP bucket and the model.
- `cli.sh`: This file is used to run the `train.py` file on a GCP VM. It also contains the parameters that we used to train the model.
- `dockerfile`: This file is used to create a docker image that contains all the dependencies needed to train the model.

Due to quota constraints, we decide it to run it for 10 epochs. 

Here it is the graph of the loss  as given by WandB:

![Training](./reports/finetune.jpeg)

## **Step 2: Model Deployment**
To being able to infer, we first needed to upload the weights into a bucket. The code for that is on the folder `src/vqa/deployment`.

Some of the most important files from there are:
- `cli.py` : this file is where we retrieve the model weight after training.
- `docker-shell.sh`: this file is used to create a docker image that contains all the dependencies needed to obtain the weights.

The model is available in the GCP bucket `gs://vqa-app-models-demo`.


## **Decision on incorporating the feature into the deployed app**

### **Introduction**
After conducting trials in inference and experimenting with fine-tuning a VQA (Visual Question Answering) model, we ultimately decided against incorporating this feature into the deployed app. The initial goal of the exploration process was to generate questions based on the textual interpretation of images, assuming that the multimodal model is robust enough to capture any detail or technical specificity in the image.

### **Challenges and limitations**
The objective was to generate questions from images at a level that reinforces student learning. However, the challenge lies in the highly specialized nature of the required knowledge. For instance, in an art class, it might involve distinguishing between different styles, names of artworks and artists, or techniques used. In mathematics, the aim could be to recognize equations or mathematical properties. In zoology, the focus might be on identifying varieties or animal families. In medicine, the goal could be to recognize specific symptoms or conditions.

The outputs of the available multimodal models, even after fine-tuning, lack the necessary specialization. This outcome is somewhat expected, as achieving the ideal scenario of accurately answering any possible question on any uploaded image requires highly specialized knowledge. Such knowledge would necessitate extensive and specific datasets covering a wide array of topics and domain expertise, which is beyond the project's scope. Given that the app is designed to be multipurpose and not specialized in any particular subject, we made the decision to omit this feature. Instead, we opted to concentrate on optimizing and reallocating resources to work on the Textual Test Generation model. This focus will allow for more flexible test generation, evaluation, and providing feedback to students.

### **Approaches**
#### **1. VQA**
We observed that the available VQA models on Hugging Face can answer basic questions but are limited to the vocabulary of the model. The vocabulary of VQA models lacks a sufficiently rich representation to answer the specialized questions we desire within our app. Architectures like [VILT-B32](https://huggingface.co/dandelin/vilt-b32-finetuned-vqa) output a vector of probabilities for tokens (similar to a classification problem), and these tokens depend on the fixed vocabulary.

#### **2. Captioners**
Other explored ideas included using captioners like [BLIP](https://huggingface.co/Salesforce/blip-image-captioning-large) or [VIT-GPT2](https://huggingface.co/nlpconnect/vit-gpt2-image-captioning). However, the same issue arises: the descriptions are relatively short, and the vocabulary is not specialized enough to construct a useful question from the text.

#### **3. Specialized computer vision services**
Additionally, there are other specialized computer vision services, such as [Astica AI](https://astica.ai/vision/describe-images/), that offer an API that provides a caption, tags, and a long description. However, they also face the challenge of a vocabulary that is not specialized enough for our specific needs.

#### **4. Fine-tuning a extremelly specific domain**
Finally, we also explored the possibility of fine-tuning a captioning model for a specialized topic, such as [medical evaluation of chest X-rays](https://towardsdatascience.com/medical-image-captioning-on-chest-x-rays-a43561a6871d). However, even with specific data, the model's performance fell short of our expectations. This raised concerns, as scaling up this focus tp more topics seemed unviable. If deployed, the app might provide erroneous information on sensitive and complex topics like the medical field, which is inherently intricate. Consequently, this approach did not convince us. Additionally, it presented a significant limitation as it restricted usage to an extremely specific area (disease detection using chest X-rays), which would only work if the user submits pictures of chest X-rays for inference. This restriction meant it could only answer questions related to this specific domain. Such a narrow focus contradicted the multipurpose nature we envisioned for the app.


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




## Getting Started

### Installation

Clone the repository and navigate to the backend app directory:

```bash
git clone [REPOSITORY_URL]
cd [CLONED_DIRECTORY]/src/build_backend

```bash
cd src/build_backend
ls
```

## Directory Structure

- `deploy/`: Scripts and Kubernetes configurations for deployment.
- `generate_test/`: Scripts for generating tests from documents.
- `grade_and_explain/`: Scripts for automatic grading and providing explanations.
- `post_requests/`: Scripts for generating post requests to send to deployed model.

## Deploying backend

You can deploy the backend with one simple command as a shell file encapsulates all the steps necessary, from building the application containers to deploying the entire backend via an Ansible playbook. Simply run the following command:

```bash
cd deploy/
sh deploy_to_k8s.sh
```
This script will set up roles and permissions (all the permissions are being given via individual shell scripts in the `roles_and_permissions` directory, see next section), and deploy your application using the `deploy_to_k8s.yml` file.

The entire application is deployed to this Kubernetes cluster:

![Kubernetes Cluster](/reports/kubnernetes_cluster.png)

## Roles and Permissions

Kubernetes configurations for roles and permissions are defined in the roles_and_permissions/ directory. Apply them as necessary:

```shell
kubectl apply -f roles_and_permissions/deployment-role.yaml
kubectl apply -f roles_and_permissions/deployment-rolebinding.yaml
kubectl apply -f roles_and_permissions/pod-reader-role.yaml
kubectl apply -f roles_and_permissions/read-pods-binding.yaml
```

# Application Design Document

## Problem statement and solution

In addressing the challenges of modern education, BiteSize tackles the crucial problem of efficiently acquiring essential knowledge. By automating question generation from course materials, the application aims to save students valuable time and enhance their learning experiences. The core issues at hand include the pressing need for faster and more effective knowledge extraction, as well as the necessity to accommodate diverse learning styles and preferences.

Recognizing student diversity, BiteSize provides a unique approach to learning customization, allowing users to tailor tests based on difficulty, repetition, and length. This adaptability aims to offer a personalized and efficient learning journey, addressing the identified problem of varied learning preferences. Additionally, BiteSize's versatility extends to different course material format. This feature tackles the challenge of diverse information presentation, ensuring a comprehensive assessment for a well-rounded understanding of the subject matter. BiteSize is not only beneficial for students but also serves as a valuable resource for educators. It facilitates the swift creation of assessment materials, enabling educators to streamline their preparation process. Additionally, the interactive nature of BiteSize enhances students' engagement with the material, leading to a more profound comprehension of key concepts.


## Solution Architecture

Solutions architecture identifies building blocks in our app, ensuring BiteSize effectively addresses the problem statement. It designs scalable, integrated solutions, considering software, hardware, networks, and processes for optimal functionality and efficiency in meeting specific business or technical challenges. In order to achieve so, we will further explain 3 elements: process (people), execution (code) and state (source, data and models).

![Solutions Architecture](/reports/sol1.png)

![Solutions Architecture](/reports/sol2.png)


### The Process being performed by the user

We have identified 3 types of people involved in the process:

**○ Data Scientists:** they play a pivotal role in our solution architecture by contributing to:

1. Creating code for text parsing and information cleaning: develop code to parse text from documents and ensure the extraction of clean and accurate information.

2. Selecting the best algorithm and model: They are responsible for choosing the most suitable algorithm and model though experimentation, enabling the app to efficiently analyze and extract relevant information from uploaded documents.

3. Applying techniques like prompt engineering: using techniques such as prompt engineering, they generate questions and feed the user's answers back into the model for feedback, overseeing the question-generation process.

4. Assessing and evaluating ML task results: Data scientists evaluate the quality of questions and answers generated by the model, ensuring optimal performance and relevance.

5. Optimizing the model: They employ methods like pruning and quantization to enhance the efficiency and effectiveness of the model.

6. Deploying the model: Data scientists oversee the deployment of the model, ensuring seamless integration into the app for end-users.


**○ Developers:** Developers are instrumental in constructing the app, ensuring the seamless integration of machine learning algorithms and user interfaces. Their multifaceted role encompasses:

1. Building the App: Developers are responsible for the overall development of the application.

2. Designing the Frontend and implementing It: They design and implement the frontend of the app, focusing on creating an intuitive and user-friendly interface.

3. Integrating the Frontend with Backend: Developers integrate the frontend with the backend, ensuring smooth communication and functionality.

4. Coding, Testing, and Refining: Their ongoing tasks involve coding new features, rigorously testing the application, and refining it for optimal performance and an enhanced user experience.


**○ Users:** Users play a crucial role in the app, engaging in the following tasks:

1. Uploading Documents: Users upload documents to the system, initiating the process.

2. Receiving Questionnaires: Upon document upload, users receive questionnaires generated by the app, directly related to the content of their documents.

3. Answering Questions: Users engage with the questionnaires, providing answers according to the type of questions presented.

4. Receiving Feedback and Learning: Users receive feedback based on their responses, facilitating a learning process through the test. This interactive feature enhances the overall user experience and comprehension of the uploaded information.



### The code Execution blocks required to fulfil the Process:


**⬤ ML Tasks**

○ Utilize a web-based hosted notebook solution from Google for experimenting with ML tasks (creating questionnaires, getting the answers, checking if the answers are correct or not, giving feedback).

○ Implement a ML pipeline to streamline the process (integration with GCP)

○ Containerized ML Components: Utilize containerization to encapsulate ML components, ensuring seamless integration and efficiency, leading to automation and execution of ML tasks efficiently.

Document Processing Workflow:
1. Document Parsing: Employ a document parsing process to extract relevant information.
2. LLM Model Questionnaire Creation: Use an LLM model to generate a comprehensive questionnaire based on the parsed document.
3. Sequential Question Presentation: Present generated questions to the user sequentially.
4. User Response Handling: Receive and process user answers to the presented questions.
5. Feedback Delivery: Return insightful feedback based on the user's responses, facilitating an interactive and educational user experience.

**⬤ Frontend**

Develop a user-friendly, single-page application equipped with the functionality to effortlessly upload documents. The application interface is designed for seamless interaction, allowing users to easily navigate and explore the features. Users can upload documents and, upon upload, access generated tests for a comprehensive and user-centric experience. The intuitive design ensures a smooth and efficient process, enhancing the overall usability of the application. Mode details about the design can be found in the User Interface section.

**⬤ Backend**

Implement an API server to expose Python functions to the frontend, acting as a crucial bridge for efficient communication between backend and frontend components. This server orchestrates the flow of data, ensuring seamless integration. Deployment on Kubernetes using Ansible has been successfully completed, further optimizing scalability and maintainability.


#### The State required during the life cycle of the App: Source Control, Database, Data / Models

○ Source Control (GitHub): Utilize GitHub as a source control platform to store and version code. This facilitates collaboration among team members, ensuring a systematic approach to code management.

○ Container Registry: Employ DockerHub as a container registry for storing Docker images. This centralized repository streamlines the storage and retrieval of containerized app components.

○ Common Document Store: Utilize Vertex AI as a common storage solution for saving documents. This ensures a centralized and efficient repository for document management within the app.

○ Optimized Model Storage: Leverage Vertex AI for storing optimized machine learning models. This dedicated space ensures the secure and efficient storage of models generated during the app's life cycle.

○ Code on Parsing and Prompt Engineering: Incorporate a dedicated section for code related to parsing and prompt engineering. This ensures a structured and organized approach to handling these essential aspects of document processing within the app.


## Technical Architecture

![Technical Architecture](/reports/tech.png)



### Building the Frontend part of the Application

The frontend of the application is build using ReactJS. It is divided as follows: a components folder that contains the different components of the application, a css folder that contains the css files for the different components, and a pages folder that contains the different pages of the application. 

The components folder contains the following components: DataContext.js, MainContent.js, MCQuestion.js, Navigation.js, SAQuestion.js, TCard.js, and TestType.js. These are the components that are used to build the application and they are all imported in the App.js file.


### Building the Backend part of the Application 

This backend application takes a document as input, scrapes its text, and generates questions to quiz students. It includes components for deployment, test generation, grading, and explanation, and posting requests.

For the backend, we used a Flask application to expose Python functions to the frontend. This application is deployed on a Kubernetes cluster using Ansible. The backend is responsible for orchestrating the flow of data between the frontend and the machine learning model. It receives the document from the frontend, sends it to the model for processing, and returns the generated questions to the frontend. The backend also handles the user's responses to the questions, providing feedback based on the answers. The backend is deployed on a Kubernetes cluster using Ansible, ensuring scalability and maintainability. 

The backend folder as a whole contains the following components: a Dockerfile that defines the environment for the backend, a requirements.txt file that contains the dependencies required for the backend, a deploy_container.sh script that deploys the backend container to Google Cloud Run, and a main.py script that contains the main application code. For that we use FastAPI to create the endpoint that would send the file from the front end into the GCP bucket.


## User interface
The frontend of our application uses React, Node.js, and CSS. React is a handy tool for building dynamic interfaces. It helps organize the code with reusable components, making it easier to manage. Node.js supports the backend, handling server-side tasks and finally, CSS takes care of styling and layout, ensuring a good-looking and responsive design. Together, they make our web app interactive, user-friendly, and efficient.

Our frontend is divided into three tabs: "Home", "About Us", and "Start Learning". The "Home" tab is the main landing page, providing an overview of our platform. The "About Us" tab offers information about our team. Lastly, the "Start Learning" tab is where users can begin their educational journey on our platform. 


#### Home
![Home](/reports/home.png)
The landing page showcases the app's presentation, and at the bottom, there's a button that redirects users to the "Start Learning" page. This design encourages users to explore and initiate their learning experience with a simple click.

#### About us
![About us](/reports/about.png)
Includes pictures, names, and email addresses of the team members, giving users a glimpse into the developers of the app.

#### Start Learning
![Start learning](/reports/learn.png)

This main tab is where users interact with the app, and they need to:

1. Choose the number of questions by either manually inputting the value or using the arrows in the quantity box. The app ensures the number is greater than 0; otherwise, a red warning message is displayed.

2. Select the test type; the app currently offers two options: multiple choice or short answer. Users can pick the type that suits their preferences.

3. Upload a document. Users can upload a PDF or Word document to be tested. By clicking the upload button, selecting their local file, users can visualize the document and proceed with the testing.


##### Multiple Choice
![Multiple Choice](/reports/mcq.png)

In the continued section of the Start Learning tab, when the user chooses the Multiple Choice option, the prompt or question appears as the title, accompanied by four answer choices. Only one of these choices is correct, and the user must select the corresponding radio button to indicate their answer. Once the user has made their selection, they can proceed by clicking the submit button.

##### Short Answer
![Short Answer](/reports/short.png)

In the continuation of the Short Answer tab, similar to the multiple-choice questionnaire, when the user selects the Short Answer option, the prompt or question is displayed as the title. Below, there is an input box where the user can type a short answer. Once the user has provided their response, they can proceed by selecting the submit button to submit their answer.

##### Feedback
![Feedback](/reports/feedback.png)
After clicking the submit button on either the Multiple Choice (MCQ) or Short Answer test, the user will receive feedback indicating whether their option/answer was correct or not. Additionally, the user will see specific feedback generated by the Language Learning Model (LLM) in response to their input. This feedback serves as an informative output, helping users understand the correctness of their response and providing insights for learning. If the answer is correct, it will be displayed in green, if it is wrong, the feedback will be displayed in red. At the bottom of the page, the user can the grade which represents the percentage of questions correctly answered.