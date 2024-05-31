import azure.functions as func
from azure.storage.blob import BlobClient, BlobServiceClient, generate_blob_sas, BlobSasPermissions
import azure_face_recognition
import imagehelper
from PIL import Image
from io import BytesIO
import json
import datetime
import logging
import os

bp = func.Blueprint() 


@bp.route(route="imagescaler")
def imagescaler(req: func.HttpRequest) -> func.HttpResponse:
    """
    Takes an image from a blob container, resizes it, and uploads the resized image to another blob container.

    Parameters:
    req (func.HttpRequest): The HTTP request object.

    Returns:
    func.HttpResponse: The HTTP response object. The body of the response contains json of the new name of the file.

    """
          
    # Get the filename from the request parameters
    filename = req.params.get('filename')
    if not filename:
        return func.HttpResponse("You must pass in the filename parameter in the query string", status_code=400)
  
    # Create a BlobServiceClient object
    blob_service_client = BlobServiceClient.from_connection_string(os.getenv('STORAGE_ACCOUNT_CONNECTION'))  
    
    # Get the BlobClient for the original blob
    original_blob_client = blob_service_client.get_blob_client(os.getenv('ORIGINAL_IMAGE_CONTAINER'), filename)

    # Download the blob to a stream
    original_blob_data = original_blob_client.download_blob().readall()

    # Open the image and convert it to PNG
    image = Image.open(BytesIO(original_blob_data))
    image = imagehelper.ImageHelper().resize(image=image)
    
    # Create a new BlobClient for the converted blob
    converted_filename = f"{os.path.splitext(filename)[0]}_converted.png"
    converted_blob_client = blob_service_client.get_blob_client(os.getenv('CONVERTED_IMAGE_CONTAINER'), converted_filename)

    # Open the temp file in read mode
    with open(image.filename, "rb") as data:
        # Upload the contents of the file to the blob
        converted_blob_client.upload_blob(data, overwrite=True)
    
    # Remove the local temp file
    os.remove(image.filename)

    result = json.dumps({"filename": converted_filename})
    
    # Log the result
    logging.info(f"Face API result: {result}")

    

    # Return the result as a JSON string in the body of the HTTP response
    return func.HttpResponse(body=result,
            status_code=200,
            headers={
                'Content-Type': 'application/json'
            }
    )