import os, logging
import azure.functions as func
import azurefunctions.extensions.bindings.blob as blob
import logging
import image_processor
from azure.storage.blob import BlobServiceClient


bp = func.Blueprint()
container_name = os.getenv('UPLOAD_IMAGE_CONTAINER')

@bp.blob_trigger(arg_name="client", path=f"{container_name}/{{filename}}", connection="STORAGE_ACCOUNT_CONNECTION")
def function_blob(client: blob.BlobClient):

    logging.info(f"Blob Trigger function triggered: {client.blob_name}")
    blob_data = client.download_blob().readall()

    # Create a BlobServiceClient object
    blob_service_client = BlobServiceClient.from_connection_string(os.getenv('STORAGE_ACCOUNT_CONNECTION'))  
    
    # Get the BlobClient for the original blob
    original_blob_client = blob_service_client.get_blob_client(os.getenv('ORIGINAL_IMAGE_CONTAINER'), client.blob_name)
    original_blob_client.upload_blob(blob_data, overwrite=True)

    # Create an instance of the ImageProcessor class
    processor = image_processor.ImageProcessor()
    result_json = processor.process(client.blob_name)

    logging.info(f"Image processing completed for {client.blob_name}")
    logging.info(f"Result: {result_json}")

    #Delete the original blob
    client.delete_blob()

    logging.info(f"Blob trigger processing completed!")

    
    
