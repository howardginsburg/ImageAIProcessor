import azure.functions as func
import os
from azure.storage.blob import BlobServiceClient
import requests
import logging
import json
from util import get_functions_url

bp = func.Blueprint() 


@bp.route(route="orchestrator")
def orchestrator(req: func.HttpRequest) -> func.HttpResponse:
    

    # Get the filename from the request parameters
    filename = req.params.get('filename')
    if not filename:
        return func.HttpResponse("You must pass in the filename parameter in the query string", status_code=400)
    result_dict = {}
    result_dict["filename"] = filename

    image_scaler_url = get_functions_url("imagescaler", query_string="filename=" + filename)

    # Call the ImageScaler function
    response = requests.get(image_scaler_url)
    
    converted_filename = response.json()["filename"]
    result_dict["convertedfilename"] = converted_filename

    face_orchestrator_url = get_functions_url("facialdetection", query_string="filename=" + converted_filename)

    # Call the FaceOrchestrator function
    response = requests.get(face_orchestrator_url)

    face_api_result = response.json()["result"]
    result_dict["facedetails"] = face_api_result

    # Call the AI Narrative function
    ai_narrative_url = get_functions_url("imagenarrativegenerator", query_string="filename=" + converted_filename)
    response = requests.get(ai_narrative_url)
    # add the string of the response body to the result dictionary
    result_dict["ainarrative"] = response.text

    # Convert the result back to json
    result_json = json.dumps(result_dict)

    # Create a new BlobClient for the converted blob
    result_file = f"{os.path.splitext(filename)[0]}.json"
    blob_service_client = BlobServiceClient.from_connection_string(os.getenv('STORAGE_ACCOUNT_CONNECTION'))  
    result_blob_client = blob_service_client.get_blob_client(os.getenv('ORCHESTRATOR_RESULT_CONTAINER'), result_file)

    # Upload the result blob.
    result_blob_client.upload_blob(result_json, overwrite=True)

    # Log the result
    logging.info(f"Orchestration API result: {result_json}")

    # Return the result as a JSON string in the body of the HTTP response
    return func.HttpResponse(body=result_json,
            status_code=200,
            headers={
                'Content-Type': 'application/json'
            }
    )

    
