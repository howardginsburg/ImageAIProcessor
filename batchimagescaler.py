

from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
import os
import util
import requests

util.load_environment_vars()

endpoint = "http://localhost:7071/api/imagescaler"

# Create a BlobServiceClient object
blob_service_client = BlobServiceClient.from_connection_string(os.getenv('STORAGE_ACCOUNT_CONNECTION'))

# Get the list of blobs in the original image container
original_container_client = blob_service_client.get_container_client(os.getenv('ORIGINAL_IMAGE_CONTAINER'))
blobs = list(original_container_client.list_blobs())

total_blobs = len(blobs)
# Print the total amount of blobs
print(f"Total blobs in container: {total_blobs}")

i = 1
for blob in blobs:
    filename = blob.name
    print(f"{i} of {total_blobs}: {filename}")
    
    response = requests.get(endpoint, params={'filename': filename})

    if response.status_code != 200:
        print(f"Error: {response.status_code}")

    i += 1




