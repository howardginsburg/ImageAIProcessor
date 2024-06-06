import azure.functions as func
import facial_recognition
import json
import logging
import os
from util import generate_sas_url

bp = func.Blueprint() 


@bp.route(route="facialdetection")
def facialdetection(req: func.HttpRequest) -> func.HttpResponse:
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

    sas_url = generate_sas_url(os.getenv('STORAGE_ACCOUNT_CONNECTION'), os.getenv('CONVERTED_IMAGE_CONTAINER'), filename)

    # Call the Face API function
    result = facial_recognition.AzureFaceRecognition().process_image(sas_url)

    # Create a new dictionary to store the result
    result_dict = {}
    result_dict["filename"] = filename
    result_dict["result"] = result

    # Convert the result back to json and add the file name to it
    result_json = json.dumps(result_dict)
    
    # Log the result
    logging.info(f"Face API result: {result_json}")

    # Return the result as a JSON string in the body of the HTTP response
    return func.HttpResponse(body=result_json,
            status_code=200,
            headers={
                'Content-Type': 'application/json'
            }
    )