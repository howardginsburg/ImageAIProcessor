

from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
import os, requests, json
import requests
from datetime import datetime

def load_environment_vars():
    """
    This function is designed to load environment variables from a local.settings.json file.  It's meant to be used when running one of the python files locally
    rather than within the function app.  This is because the function app will automatically load environment variables from the local.settings.json file.
    """
    # Open the local.settings.json file
    with open('local.settings.json') as f:
        # Load the JSON data from the file
        data = json.load(f)

    # Iterate over the key-value pairs in the 'Values' dictionary
    for key, value in data['Values'].items():
        # Set each key-value pair as an environment variable
        os.environ[key] = value


load_environment_vars()

endpoint = "http://localhost:7071/api/orchestrator"

# Create a BlobServiceClient object
blob_service_client = BlobServiceClient.from_connection_string(os.getenv('STORAGE_ACCOUNT_CONNECTION'))

# Get the list of blobs in the original image container
original_container_client = blob_service_client.get_container_client(os.getenv('ORIGINAL_IMAGE_CONTAINER'))
blobs = list(original_container_client.list_blobs())

total_blobs = len(blobs)
# Print the total amount of blobs
print(f"Total blobs in container: {total_blobs}")

start_time = datetime.now()

i = 1
for blob in blobs:
    filename = blob.name
    print(f"{i} of {total_blobs}: {filename}")
    
    response = requests.get(endpoint, params={'filename': filename})

    if response.status_code != 200:
        print(f"Error: {response.status_code}")

    i += 1

    if i > 100:
        break

end_time = datetime.now()

# Print total time in seconds
print(f"Total time: {(end_time - start_time).total_seconds()} seconds")



