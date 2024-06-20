import os, logging, json, datetime
import azure.functions as func
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from concurrent.futures import ThreadPoolExecutor
import image_scaler
import facial_recognition
import narrative_generator
import logging


app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="orchestrator")
def orchestrator(req: func.HttpRequest) -> func.HttpResponse:

    logging.info('Orchestrator function triggered.')    

    # Get the filename from the request parameters
    filename = req.params.get('filename')
    if not filename:
        return func.HttpResponse("You must pass in the filename parameter in the query string", status_code=400)
    
    logging.info(f"Orchestrating functions for file: {filename}")

    start_time = datetime.datetime.now()

    result_dict = {}
    result_dict["metrics"] = {}
    result_dict["filename"] = filename

    blob_service_client = BlobServiceClient.from_connection_string(os.getenv('STORAGE_ACCOUNT_CONNECTION')) 

    logging.info(f"Calling ImageScaler function for file: {filename}")
    resized_result = resize_image(filename)
    resized_filename = resized_result["resized_filename"]
    result_dict["resizedfilename"] = resized_filename
    result_dict["metrics"]["image_resize"] = resized_result["total_time"]

    # Generate a SAS token for the blob
    sas_token = generate_blob_sas(
        blob_service_client.account_name,
        os.getenv('RESIZED_IMAGE_CONTAINER'),
        resized_filename,
        account_key=blob_service_client.credential.account_key,
        permission=BlobSasPermissions(read=True),
        expiry=datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    )

    # Construct the SAS URL for the blob
    sas_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{os.getenv('RESIZED_IMAGE_CONTAINER')}/{resized_filename}?{sas_token}"

    
    logging.info(f"Calling FaceOrchestrator and AI Narrative functions in parallel for file: {resized_filename}")
    # Execute API calls in parallel
    with ThreadPoolExecutor(max_workers=2) as executor:
        face_orchestrator_future = executor.submit(call_face_orchestrator, sas_url)
        ai_narrative_future = executor.submit(call_ai_narrative, sas_url)

        face_api_result = face_orchestrator_future.result()
        ai_narrative_result = ai_narrative_future.result()

    # Add results to the result dictionary
    result_dict["facedetails"] = face_api_result["face_result"]
    result_dict["metrics"]["facial_recognition"] = face_api_result["total_time"]
    result_dict["ainarrative"] = ai_narrative_result["narrative"]
    result_dict["metrics"]["ai_narrative"] = ai_narrative_result["total_time"]

    end_time = datetime.datetime.now()

    total_time = (end_time - start_time).total_seconds()
    result_dict["metrics"]["total_time"] = total_time

    logging.info(f"Orchestration completed in {total_time} seconds")

    # Convert the result back to json
    result_json = json.dumps(result_dict)

    if (os.getenv('ORCHESTRATOR_RESULT_CONTAINER') is not None):
        # Create a new BlobClient for the results json blob
        result_file = f"{os.path.splitext(filename)[0]}.json"
    
        result_service_client = blob_service_client

        if (os.getenv('ORCHESTRATOR_RESULT_CONNECTION') is not None):
            result_service_client = BlobServiceClient.from_connection_string(os.getenv('ORCHESTRATOR_RESULT_CONNECTION'))

        result_blob_client = result_service_client.get_blob_client(os.getenv('ORCHESTRATOR_RESULT_CONTAINER'), result_file)
        # Upload the result blob.
        result_blob_client.upload_blob(result_json, overwrite=True)

    # Log the result
    logging.info(f"Orchestration API result: {result_json}")

    return func.HttpResponse(result_json, mimetype="application/json", status_code=200)

def resize_image(filename):
    start_time = datetime.datetime.now()
    resized_filename = image_scaler.ImageHelper().resize(filename)
    end_time = datetime.datetime.now()

    total_time = (end_time - start_time).total_seconds()
    logging.info(f"Image resizing completed in {total_time} seconds")

    # Create a dictionary with the results
    result = {
        'resized_filename': resized_filename,
        'total_time': total_time
    }

    return result

def call_face_orchestrator(sas_url):
    start_time = datetime.datetime.now()
    face_result = facial_recognition.AzureFaceRecognition().process_image(sas_url)
    end_time = datetime.datetime.now()

    total_time = (end_time - start_time).total_seconds()
    logging.info(f"Face recognition completed in {total_time} seconds")

    result = {
        'face_result': face_result,
        'total_time': total_time
    }
    return result

def call_ai_narrative(sas_url):
    start_time = datetime.datetime.now()
    narrative = narrative_generator.NarrativeGenerator().generate_narrative(sas_url)
    end_time = datetime.datetime.now()

    total_time = (end_time - start_time).total_seconds()
    logging.info(f"AI narrative generation completed in {total_time} seconds")

    result = {
        'narrative': narrative,
        'total_time': total_time
    }
    return result

    
