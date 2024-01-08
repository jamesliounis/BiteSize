from setuptools import find_packages
from setuptools import setup


REQUIRED_PACKAGES = ["wandb==0.15.11", "tensorflow-hub==0.14.0","transformers==4.34.0" , "torch==2.1.0" , "jupyter_client", "ipywidgets==7.4.2"] 

setup(
    name="vqa-app-trainer",
    version="0.0.1",
    install_requires=REQUIRED_PACKAGES,
    packages=find_packages(),
    description="VQA App Trainer Application",
)