import os
import requests
import uuid
from PIL import Image
from io import BytesIO
from util import load_environment_vars
import tempfile

from PIL import Image
from io import BytesIO

class ImageHelper:

    def _resize_image(self, image, max_size_bytes=6*1024*1024):
        """
        Resizes an image if its size in bytes is greater than the specified maximum size.

        Parameters:
        image (PIL.Image): The image to resize.
        max_size_bytes (int, optional): The maximum size of the image in bytes. 
                                        Default is 6*1024*1024, which is approximately 6MB.

        Returns:
        PIL.Image: The original image if its size was less than or equal to max_size_bytes, 
                   otherwise the resized image.
        """
            
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

        return image

        

    def _convert_type(self, image):
        """
        Converts the mode of an image to 'I' (32-bit signed integer pixels) if it has any of the I permutations.
        This is done to ensure that resizing and saving the image as a PNG will work correctly.

        Parameters:
        image (PIL.Image): The image whose mode is to be converted.

        Returns:
        PIL.Image: The image with its mode possibly converted.
        """
        
        # Get the current image mode. It could be 'RGB' for color photos, 'I;16B' for 16-bit grayscale, etc.
        mode = image.mode

        # If the image is not in 'RGB' mode, convert it to 'I' mode
        #if image.mode != 'RGB':
        #    mode = 'I'
        # 

        #If image.mode begins with 'I;' then it is a 32-bit signed integer image
        if image.mode.startswith('I;'):
            mode = 'I' 

        # Convert the image to the new mode
        image = image.convert(mode)
        
        return image


    def _load_image(self, fileuri):
        """
        Loads an image from a given URI. The URI can be a URL or a local file path.

        Parameters:
        fileuri (str): The URI of the image to load.

        Returns:
        PIL.Image: The loaded image.

        Raises:
        Exception: If the image cannot be loaded from the URI.
        """
        
        image = None

        # Try to get the image data from the URL
        try:
            response = requests.get(fileuri)
            image = Image.open(BytesIO(response.content))
        except Exception as e:
            # If the image cannot be loaded from the URL, try to get it as a local file instead.
            image = Image.open(fileuri)

        return image

    def resize(self, image=None, file=None):
        """
        Resizes an image. The image can be provided directly or loaded from a file.

        Parameters:
        image (PIL.Image, optional): The image to resize. If None, the image is loaded from the file parameter.
        file (str, optional): The file path or URL of the image to load and resize. Ignored if the image parameter is not None.

        Returns:
        PIL.Image: The resized image.

        Raises:
        Exception: If both image and file parameters are None.
        """
        
        # If no image is provided, load it from the file
        if image is None:
            image = self._load_image(file)

        # Convert the image to a PNG with the correct image mode
        image = self._convert_type(image)
        # Resize the image
        image = self._resize_image(image)

        # Generate a temporary file name
        temp_image_name = uuid.uuid4()
        # Get the path to the temporary file
        file_path = os.path.join(tempfile.gettempdir(), f'{temp_image_name}.png')

        # Save the image to the temporary file
        image.save(file_path, format='PNG')

        # Open the image from the temporary file
        image = Image.open(file_path)

        return image

if __name__ == "__main__":
    # Load environment variables
    load_environment_vars()

    #print(os.path.dirname(os.path.abspath(__file__)))

    # Get the URI of the image from the environment variables. This can be either a URL or a local file path.
    file_uri = os.getenv("TEST_IMAGE_URI")

    # Create an ImageHelper object
    image_helper = ImageHelper()

    # Use the ImageHelper object to resize the image at the specified URI
    image = image_helper.resize(file=file_uri)

    # Print the location of the resized image
    print(f"Resized image located at: {image.filename}")