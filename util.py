import os, json, datetime
from urllib.parse import urlencode
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions


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

def generate_sas_url(storage_account_connection, container_name, filename):
    # Create a BlobServiceClient object
    blob_service_client = BlobServiceClient.from_connection_string(storage_account_connection)  
    
    
    # Generate a SAS token for the blob
    sas_token = generate_blob_sas(
        blob_service_client.account_name,
        container_name,
        filename,
        account_key=blob_service_client.credential.account_key,
        permission=BlobSasPermissions(read=True),
        expiry=datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    )

    # Construct the SAS URL for the blob
    sas_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{container_name}/{filename}?{sas_token}"

    return sas_url

def get_functions_url(function_name, query_string):
    functions_url = f"{os.getenv('BASE_URL')}/api/{function_name}"

    query_params = {}
    if query_string:
        query_params = dict(param.split('=') for param in query_string.split('&'))

    # If there is a FUNCTIONS_KEY in the environment variables, add it to the query parameters
    if os.getenv('FUNCTIONS_KEY'):
        query_params['code'] = os.getenv('FUNCTIONS_KEY')

    encoded_query_string = urlencode(query_params)
    functions_url = f"{functions_url}?{encoded_query_string}"

    return functions_url

if __name__ == "__main__":
    load_environment_vars()
    # Iterate through all the keys in the environment variables and print the key and value
    for key in os.environ.keys():
        print(key, os.getenv(key))
    