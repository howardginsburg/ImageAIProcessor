import logging
import azure.functions as func
import os
import requests
from util import generate_sas_url
#from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
#import datetime

bp = func.Blueprint() 


@bp.route(route="imagenarrativegenerator")

def ImageNarrativeGenerator(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('AI Narrative function triggered.')

    try:
        # Get the filename from the request parameters
        filename = req.params.get('filename')
        if not filename:
            return func.HttpResponse("You must pass in the filename parameter in the query string", status_code=400)

        sas_url = generate_sas_url(os.getenv('STORAGE_ACCOUNT_CONNECTION'), os.getenv('CONVERTED_IMAGE_CONTAINER'), filename)

        # Azure OpenAI GPT model details
        api_key = os.getenv("AZURE_OPEN_AI_KEY")
        gpt4_endpoint = os.getenv("AZURE_OPEN_AI_ENDPOINT")
                
        # Create headers for the request
        headers = {
            "Content-Type": "application/json",
            "api-key": api_key,
        }

        # Create the payload for the request
        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "text",
                            "text": "You are a helpful assistant that looks at images and describes the image(s) in as much detail as possible. Don't use any apostrophe characters (like this ') in your response or possessive nouns (like the man's) in your response."
                        }
                    ]
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Describe the scene in this picture with as much detail as possible. Don't use any apostrophe characters (like this ') in your response or possessive nouns (like the man's) in your response. Review your output, and if there are any apostrophe characters (like this ') replace them with double quotes."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"{sas_url}"
                            }
                        }
                    ]
                }
            ],
            "temperature": 0.7,
            "top_p": 0.95,
            "max_tokens": 2000
        }

        # Send request to GPT-4 endpoint
        response = requests.post(gpt4_endpoint, headers=headers, json=payload)
        response.raise_for_status()  # Will raise an HTTPError if the HTTP request returned an unsuccessful status code
        
        # Extract the narrative from the response
        narrative = response.json()['choices'][0]['message']['content']
        return func.HttpResponse(narrative, status_code=200)

    except Exception as e:
        logging.error(f"Exception occurred: {e}")
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)