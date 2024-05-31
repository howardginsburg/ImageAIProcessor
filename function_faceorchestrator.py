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


@bp.route(route="faceorchestrator")
def faceorchestrator(req: func.HttpRequest) -> func.HttpResponse:
    """
    Orchestrates the processing of an image to detect faces, similar faces from other images, and identify any celebrities present.

    Parameters:
    req (func.HttpRequest): The HTTP request object.

    Returns:
    func.HttpResponse: The HTTP response object. The body of the response contains a JSON string with data about the persons detected in the image.

    """
          
    # Get the filename from the request parameters
    filename = req.params.get('filename')
    if not filename:
        return func.HttpResponse("You must pass in the filename parameter in the query string", status_code=400)
  
    # Create a BlobServiceClient object
    blob_service_client = BlobServiceClient.from_connection_string(os.getenv('STORAGE_ACCOUNT_CONNECTION'))  
    
    
    # Generate a SAS token for the blob
    sas_token = generate_blob_sas(
        blob_service_client.account_name,
        os.getenv('CONVERTED_IMAGE_CONTAINER'),
        filename,
        account_key=blob_service_client.credential.account_key,
        permission=BlobSasPermissions(read=True),
        expiry=datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    )

    # Construct the SAS URL for the blob
    sas_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{os.getenv('CONVERTED_IMAGE_CONTAINER')}/{filename}?{sas_token}"  

    # Call the Face API function
    result = azure_face_recognition.AzureFaceRecognition().process_image(sas_url)

    # Create a new dictionary to store the result
    result_dict = {}
    result_dict["filename"] = filename
    result_dict["result"] = result

    # Convert the result back to json and add the file name to it
    result_json = json.dumps(result_dict)

    # Create a new BlobClient for the converted blob
    face_result_file = f"{os.path.splitext(filename)[0]}.json"
    face_result_blob_client = blob_service_client.get_blob_client(os.getenv('FACE_RESULT_CONTAINER'), face_result_file)

    # Open the temp file in read mode
    face_result_blob_client.upload_blob(result_json, overwrite=True)
    
    # Log the result
    logging.info(f"Face API result: {result_json}")

    # Return the result as a JSON string in the body of the HTTP response
    return func.HttpResponse(body=result_json,
            status_code=200,
            headers={
                'Content-Type': 'application/json'
            }
    )