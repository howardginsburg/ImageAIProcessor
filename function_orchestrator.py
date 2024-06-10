import azure.functions as func
import os
from azure.storage.blob import BlobServiceClient
from concurrent.futures import ThreadPoolExecutor
import requests
import logging
import json
from util import get_functions_url

bp = func.Blueprint() 

@bp.route(route="orchestrator")
def orchestrator(req: func.HttpRequest) -> func.HttpResponse:

    logging.info('Orchestrator function triggered.')    

    # Get the filename from the request parameters
    filename = req.params.get('filename')
    if not filename:
        return func.HttpResponse("You must pass in the filename parameter in the query string", status_code=400)
    
    logging.info(f"Orchestrating functions for file: {filename}")

    result_dict = {}
    result_dict["filename"] = filename

    logging.info(f"Calling ImageScaler function for file: {filename}")
    resized_filename = call_image_scaler(filename)
    result_dict["resizedfilename"] = resized_filename

    
    logging.info(f"Calling FaceOrchestrator and AI Narrative functions in parallel for file: {resized_filename}")
    # Execute API calls in parallel
    with ThreadPoolExecutor(max_workers=2) as executor:
        face_orchestrator_future = executor.submit(call_face_orchestrator, resized_filename)
        ai_narrative_future = executor.submit(call_ai_narrative, resized_filename)

        face_api_result = face_orchestrator_future.result()
        ai_narrative_result = ai_narrative_future.result()

    # Add results to the result dictionary
    result_dict["facedetails"] = face_api_result
    result_dict["ainarrative"] = ai_narrative_result

    # Convert the result back to json
    result_json = json.dumps(result_dict)

    # Create a new BlobClient for the results json blob
    result_file = f"{os.path.splitext(filename)[0]}.json"
    blob_service_client = BlobServiceClient.from_connection_string(os.getenv('STORAGE_ACCOUNT_CONNECTION'))  
    result_blob_client = blob_service_client.get_blob_client(os.getenv('ORCHESTRATOR_RESULT_CONTAINER'), result_file)

    # Upload the result blob.
    result_blob_client.upload_blob(result_json, overwrite=True)

    # Log the result
    logging.info(f"Orchestration API result: {result_json}")

    # Return the result as a JSON string in the body of the HTTP response
    # return func.HttpResponse(body=result_json,
    #         status_code=200,
    #         headers={
    #             'Content-Type': 'application/json'
    #         }
    # )
    return func.HttpResponse(result_json, mimetype="application/json", status_code=200)

def call_image_scaler(filename):
    try:
        image_scaler_url = get_functions_url("imagescaler", query_string="filename=" + filename)
        response = requests.get(image_scaler_url)

        logging.info(f"ImageScaler Response as text: {response.text}")

        # Check if the response is not empty
        if response.content:
            logging.info(f"ImageScaler response: {response.json()}")
            response.raise_for_status()  # Raises an HTTPError if the response status code is 4XX or 5XX
            return response.json().get("filename")
        else:
            logging.error("Empty response received from ImageScaler")
            return None
    except requests.RequestException as e:
        # Handle all requests-related exceptions
        logging.error(f"Request failed: {e}")
        return None
    except ValueError as e:
        # Handle JSON decoding error
        logging.error(f"JSON decoding failed: {e}")
        return None
    except Exception as e:
        # Handle any other exceptions
        logging.error(f"An error occurred: {e}")
        return None

def call_face_orchestrator(filename):
    try:
        face_orchestrator_url = get_functions_url("facialdetection", query_string="filename=" + filename)
        response = requests.get(face_orchestrator_url)
        response.raise_for_status()  # Raises an HTTPError if the response status code is 4XX or 5XX
        logging.info(f"FaceOrchestrator response: {response.json()}")
        return response.json()["result"]
    except requests.RequestException as e:
        # Handle all requests-related exceptions
        logging.error(f"Request failed: {e}")
        return None

def call_ai_narrative(filename):
    try:
        ai_narrative_url = get_functions_url("imagenarrativegenerator", query_string="filename=" + filename)
        response = requests.get(ai_narrative_url)
        response.raise_for_status()  # Raises an HTTPError if the response status code is 4XX or 5XX
        logging.info(f"AI Narrative response: {response.text}")
        return response.text
    except requests.RequestException as e:
        # Handle all requests-related exceptions
        logging.error(f"Request failed: {e}")
        return None

    
