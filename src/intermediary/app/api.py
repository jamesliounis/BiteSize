from typing import Annotated
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware 
from google.cloud import storage
# from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from fastapi import HTTPException
import os
import aiofiles
from pydantic import BaseModel
import json


class UserAnswers(BaseModel):
    # Define a Pydantic model to represent your JSON data structure
    # Adjust this based on the actual structure of your JSON data
    MCQ: dict
    
app = FastAPI()

# Add CORS middleware CHECK WITH ARI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"])

# Replace 'your-gcs-bucket-name' with your actual GCS bucket name
GCS_BUCKET_NAME = 'bite-size-documents-2'

def upload_to_gcs(file_path: str, blob_name: str):
    """Uploads a file to GCS."""

    client = storage.Client.from_service_account_json('gen_service_account.json')
    bucket = client.bucket(GCS_BUCKET_NAME)
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(file_path)


@app.post("/upload/")
async def upload_file(file: UploadFile=File(...)):
    try:
        # Save the uploaded file locally
        if not os.path.exists("temp"):
            os.makedirs("temp")
        
        file_path = f"temp/{file.filename}"

        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await file.read()  # async read
            await out_file.write(content)  # async write

        # Upload the file to GCS
        blob_name = f"documents_to_be_summarized/{file.filename}"
        upload_to_gcs(file_path, blob_name)

        # Optionally, you can delete the local file after uploading to GCS
        os.remove(file_path)

        return JSONResponse(content={"message": "File uploaded successfully"}, status_code=200)
    except Exception as e:
        raise HTTPException(
            status_code=HTTPException,
            detail=f"Could not process the file. Error: {str(e)}",
        )
    


@app.post("/upload_answers/")
async def upload_answers(user_answers: UserAnswers):
    try:
        # Access your JSON data using the 'user_answers' parameter
        # The structure of 'user_answers' will match the UserAnswers Pydantic model
        # You can now process the JSON data as needed
        
        # For example, print the MCQ dictionary
        print(user_answers.MCQ)

        # Do whatever processing is necessary with the JSON data
        temp_dir = 'temp'
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        file_path = os.path.join(temp_dir, 'user_answers.json') #change this at some point MAKE UNIQUEEEEEE
        with open(file_path, 'w') as file:
            file.write(user_answers.model_dump_json())

        # Upload the file to GCS
        blob_name = 'user_answers/user_answers.json'
        upload_to_gcs(file_path, blob_name)
        os.remove(file_path)

        return JSONResponse(content={"message": "JSON data received successfully"}, status_code=200)
    except Exception as e:
        raise HTTPException(
            status_code=HTTPException,
            detail=f"Could not process the JSON data. Error: {str(e)}"
        )

@app.get("/status")
async def get_api_status():
    return {
        "version": "1.0",
    }