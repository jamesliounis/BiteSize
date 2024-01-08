"""
Instantaites a GCP bucket object for increased readability and efficent use
"""
from google.cloud import storage

class Bucket():
    def __init__(self, path, bucket_name):
        """
        Creates the GCP bucket object based on the json path.
        """
        storage_client = storage.Client.from_service_account_json(path)
        self.bucket = storage_client.bucket(bucket_name)
        
    def list_files(self, folder_name):
        """
        List all files in a GCP bucket within a specific folder.
        
        Args:
            folder_name (str): the name of the folder within the GCP bucket we want the file names from
        
        Returns:
            list: names of only files (no folders) within this folder
        """
        blobs = self.bucket.list_blobs(prefix=folder_name)
        return [blob.name for blob in blobs if not blob.name.endswith("/")]

    def get_file(self, file_name):
        """
        Get a file from GCP bucket.

        Args:
            file_name (str): the name of the file

        Returns:
            ???: File content in bytes
        """
        blob = self.bucket.blob(file_name)

        # Download as bytes
        content = blob.download_as_bytes()
        return content