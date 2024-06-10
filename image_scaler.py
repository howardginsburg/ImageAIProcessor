import os
from azure.storage.blob import BlobServiceClient
import requests
import uuid
from PIL import Image
from io import BytesIO
import tempfile

from PIL import Image
from io import BytesIO

class ImageHelper:

    def resize(self, filename):
        # Create a BlobServiceClient object
        blob_service_client = BlobServiceClient.from_connection_string(os.getenv('STORAGE_ACCOUNT_CONNECTION'))  
    
        # Get the BlobClient for the original blob
        original_blob_client = blob_service_client.get_blob_client(os.getenv('ORIGINAL_IMAGE_CONTAINER'), filename)

        # Download the blob to a stream
        original_blob_data = original_blob_client.download_blob().readall()

        # Open the image and convert it to PNG
        image = Image.open(BytesIO(original_blob_data))

        # Get the current image mode. It could be 'RGB' for color photos, 'I;16B' for 16-bit grayscale, etc.
        mode = image.mode

        #If image.mode begins with 'I;' then it is a 32-bit signed integer image
        if image.mode.startswith('I;'):
            mode = 'I' 

        # Convert the image to the new mode
        image = image.convert(mode)

        max_size_bytes=6*1024*1024

        # Calculate the size of the image in bytes
        image_size_bytes = len(image.tobytes())

        # If the image size is greater than max_size_bytes, resize it
        if image_size_bytes > max_size_bytes:
            # Calculate the scale factor
            scale_factor = (max_size_bytes / image_size_bytes) ** 0.5
            # Calculate the new size of the image
            new_size = (int(image.width * scale_factor), int(image.height * scale_factor))
            # Resize the image
            image = image.resize(new_size, Image.Resampling.LANCZOS)

        # Generate a temporary file name
        temp_image_name = uuid.uuid4()
        # Get the path to the temporary file
        file_path = os.path.join(tempfile.gettempdir(), f'{temp_image_name}.png')

        # Save the image to the temporary file
        image.save(file_path, format='PNG')

        # Open the image from the temporary file
        image = Image.open(file_path)

        # Create a new BlobClient for the resized blob
        resized_filename = f"{os.path.splitext(filename)[0]}.png"
        resized_blob_client = blob_service_client.get_blob_client(os.getenv('RESIZED_IMAGE_CONTAINER'), resized_filename)

        # Open the temp file in read mode
        with open(image.filename, "rb") as data:
            # Upload the contents of the file to the blob
            resized_blob_client.upload_blob(data, overwrite=True)
    
        # Remove the local temp file
        os.remove(image.filename)

        return resized_filename