import os, json


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

if __name__ == "__main__":
    load_environment_vars()
    # Iterate through all the keys in the environment variables and print the key and value
    for key in os.environ.keys():
        print(key, os.getenv(key))
    