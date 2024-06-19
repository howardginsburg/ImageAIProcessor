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
    result_dict["filename"] = filename

    blob_service_client = BlobServiceClient.from_connection_string(os.getenv('STORAGE_ACCOUNT_CONNECTION')) 

    logging.info(f"Calling ImageScaler function for file: {filename}")
    resized_filename = resize_image(filename)
    result_dict["resizedfilename"] = resized_filename

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
    result_dict["facedetails"] = face_api_result
    result_dict["ainarrative"] = ai_narrative_result

    # Convert the result back to json
    result_json = json.dumps(result_dict)

    # Create a new BlobClient for the results json blob
    result_file = f"{os.path.splitext(filename)[0]}.json"
    
    result_blob_client = blob_service_client.get_blob_client(os.getenv('ORCHESTRATOR_RESULT_CONTAINER'), result_file)

    # Upload the result blob.
    result_blob_client.upload_blob(result_json, overwrite=True)

    # Log the result
    logging.info(f"Orchestration API result: {result_json}")

    end_time = datetime.datetime.now()

    logging.info(f"Orchestration completed in {(end_time - start_time).total_seconds()} seconds")

    return func.HttpResponse(result_json, mimetype="application/json", status_code=200)

def resize_image(filename):
    start_time = datetime.datetime.now()
    resized_filename = image_scaler.ImageHelper().resize(filename)
    end_time = datetime.datetime.now()

    logging.info(f"Image resizing completed in {(end_time - start_time).total_seconds()} seconds")
    return resized_filename

def call_face_orchestrator(sas_url):
    start_time = datetime.datetime.now()
    face_result = facial_recognition.AzureFaceRecognition().process_image(sas_url)
    end_time = datetime.datetime.now()
    logging.info(f"Face recognition completed in {(end_time - start_time).total_seconds()} seconds")
    return face_result

def call_ai_narrative(sas_url):
    start_time = datetime.datetime.now()
    narrative = narrative_generator.NarrativeGenerator().generate_narrative(sas_url)
    end_time = datetime.datetime.now()
    logging.info(f"AI narrative generation completed in {(end_time - start_time).total_seconds()} seconds")
    return narrative

    
