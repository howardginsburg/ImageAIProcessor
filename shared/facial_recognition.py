import requests, json, os, json, logging


class AzureFaceRecognition:

    API_VERSION = "v1.1-preview.1"

    def _detect_faces(self, image_url):
        """
        This function detects faces in an image using Azure's Face API.

        Parameters:
        image_url (str): The URL of the image to analyze.

        Returns:
        dict: The JSON response from the API. This includes information about the detected faces.

        """

        # Define the endpoint
        # The endpoint URL is constructed using the base URL stored in the AZURE_AI_SERVICE_ENDPOINT environment variable,
        # along with the specific path for the face detection API.
        face_endpoint = f"{os.getenv('AZURE_AI_SERVICE_ENDPOINT')}/face/{AzureFaceRecognition.API_VERSION}/detect?returnFaceId=true&recognitionModel=recognition_04&detectionModel=detection_03"

        # Define the headers
        # The headers for the API request are defined here. The Content-Type is set to 'application/json',
        # and the subscription key for the Azure AI service is retrieved from the AZURE_AI_SERVICE_KEY environment variable.
        headers = {
            'Content-Type': 'application/json',
            'Ocp-Apim-Subscription-Key': os.getenv("AZURE_AI_SERVICE_KEY"),
        }

        # Define the body
        # The body of the API request is defined here. It is a JSON object that contains the URL of the image to analyze.
        body = json.dumps({
            'url': image_url,
        })

        # Make the POST request
        # The API request is made here. The response from the API is a JSON object that contains information about the detected faces.
        response = requests.post(face_endpoint, headers=headers, data=body)

        # Return the JSON response
        return response.json()

    def _search_for_similar_faces(self, face_ids):
        # Define the endpoint
        face_endpoint = f"{os.getenv('AZURE_AI_SERVICE_ENDPOINT')}/face/{AzureFaceRecognition.API_VERSION}/identify"

        # Define the headers
        headers = {
            'Content-Type': 'application/json',
            'Ocp-Apim-Subscription-Key': os.getenv("AZURE_AI_SERVICE_KEY"),
        }

        # Initialize an empty list to store all responses
        all_responses = []

        # Split face_ids into chunks of 10
        for i in range(0, len(face_ids), 10):
            chunk_face_ids = face_ids[i:i+10]

            # Define the body
            body = json.dumps({
                'faceIds': chunk_face_ids,
                'personIds': ["*"]
            })

            # Make the POST request
            response = requests.post(face_endpoint, headers=headers, data=body)

            # Append the response to all_responses
            all_responses.extend(response.json())

        # Return all responses
        return all_responses
    
    def _create_person(self, name):
        """
        This function creates a new person in Azure's Face API.

        The person is created with a default name 'name'. The function returns the ID of the newly created person.

        Returns:
        str: The ID of the newly created person.

        """

        # Define the endpoint
        # The endpoint URL is constructed using the base URL stored in the AZURE_AI_SERVICE_ENDPOINT environment variable,
        # along with the specific path for the person creation API.
        face_endpoint = f"{os.getenv('AZURE_AI_SERVICE_ENDPOINT')}/face/{AzureFaceRecognition.API_VERSION}/persons"

        # Define the headers
        # The headers for the API request are defined here. The Content-Type is set to 'application/json',
        # and the subscription key for the Azure AI service is retrieved from the AZURE_AI_SERVICE_KEY environment variable.
        headers = {
            'Content-Type': 'application/json',
            'Ocp-Apim-Subscription-Key': os.getenv("AZURE_AI_SERVICE_KEY"),
        }

        # Define the body
        # The body of the API request is defined here. It is a JSON object that contains the name of the person to create.
        body = json.dumps({
            'name': name,
        })

        # Make the POST request
        # The API request is made here. The response from the API is a JSON object that contains information about the newly created person.
        response = requests.post(face_endpoint, headers=headers, data=body)
        
        # Return the personId from the response
        return response.json()['personId']

    def _update_person(self, person_id, name):
        # Define the endpoint
        face_endpoint = f"{os.getenv('AZURE_AI_SERVICE_ENDPOINT')}/face/{AzureFaceRecognition.API_VERSION}/persons/{person_id}"

        # Define the headers
        headers = {
            'Content-Type': 'application/json',
            'Ocp-Apim-Subscription-Key': os.getenv("AZURE_AI_SERVICE_KEY"),
        }

        # Define the body
        body = json.dumps({
            'name': name,
        })

        # Make the PATCH request
        response = requests.patch(face_endpoint, headers=headers, data=body)


    def _add_face_to_person(self, person_id, image_url, bounding_box):
        """
        This function adds a face to a person in Azure's Face API.

        Parameters:
        person_id (str): The ID of the person to add the face to.
        image_url (str): The URL of the image containing the face.
        bounding_box (dict): A dictionary containing the bounding box of the face in the image. 
                            It should have 'left', 'top', 'width', and 'height' keys.

        Returns:
        dict: The JSON response from the API. This includes information about the added face.

        """

        # Define the endpoint
        # The endpoint URL is constructed using the base URL stored in the AZURE_AI_SERVICE_ENDPOINT environment variable,
        # along with the specific path for the face addition API.
        face_endpoint = f"{os.getenv('AZURE_AI_SERVICE_ENDPOINT')}/face/{AzureFaceRecognition.API_VERSION}/persons/{person_id}/recognitionModels/Recognition_04/persistedFaces?targetFace={str(bounding_box['left'])},{str(bounding_box['top'])},{str(bounding_box['width'])},{str(bounding_box['height'])}&detectionModel=Detection_03"

        # Define the headers
        # The headers for the API request are defined here. The Content-Type is set to 'application/json',
        # and the subscription key for the Azure AI service is retrieved from the AZURE_AI_SERVICE_KEY environment variable.
        headers = {
            'Content-Type': 'application/json',
            'Ocp-Apim-Subscription-Key': os.getenv("AZURE_AI_SERVICE_KEY"),
        }

        # Define the body
        # The body the API request is defined here. It is a JSON object that contains the URL of the image containing the face.
        body = json.dumps({
            'url': image_url,
        })

        # Make the POST request
        # The API request is made here. The response from the API is a JSON object that contains information about the added face.
        response = requests.post(face_endpoint, headers=headers, data=body)

        # Return the JSON response
        return response.json()

    def _detect_celebrity(self, image_url):
        """
        This function detects celebrities in an image using Azure's Computer Vision API.

        Parameters:
        image_url (str): The URL of the image to analyze.

        Returns:
        list: A list of dictionaries, each containing information about a detected celebrity. 
            Each dictionary includes the name of the celebrity and the confidence score.

        """

        # Define the endpoint
        # The endpoint URL is constructed using the base URL stored in the AZURE_AI_SERVICE_ENDPOINT environment variable,
        # along with the specific path for the celebrity detection API.
        face_endpoint = f"{os.getenv('AZURE_AI_SERVICE_ENDPOINT')}/vision/v3.2/analyze?visualFeatures=Categories&details=Celebrities&language=en&model-version=latest"

        # Define the headers
        # The headers for the API request are defined here. The Content-Type is set to 'application/json',
        # and the subscription key for the Azure AI service is retrieved from the AZURE_AI_SERVICE_KEY environment variable.
        headers = {
            'Content-Type': 'application/json',
            'Ocp-Apim-Subscription-Key': os.getenv("AZURE_AI_SERVICE_KEY"),
        }

        # Define the body
        # The body the API request is defined here. It is a JSON object that contains the URL of the image to analyze.
        body = json.dumps({
            'url': image_url,
        })

        # Make the POST request
        # The API request is made here. The response from the API is a JSON object that contains information about the detected celebrities.
        response = requests.post(face_endpoint, headers=headers, data=body)

        celebrities = []

        try:
            celebrities =  response.json()['categories'][0]['detail']['celebrities']
        except KeyError:
            pass
        
        return celebrities

    def _check_boundingbox_overlap(self, bb1, bb2):
        """
        This function checks if two bounding boxes overlap.

        Parameters:
        bb1, bb2 (dict): Dictionaries representing bounding boxes. 
                        Each should have 'top', 'left', 'width', and 'height' keys.

        Returns:
        bool: True if the bounding boxes overlap, False otherwise.

        """

        # Assert that the width and height of both bounding boxes are non-negative
        assert bb1['width'] >= 0 and bb1['height'] >= 0
        assert bb2['width'] >= 0 and bb2['height'] >= 0

        # Calculate the coordinates of the corners of the bounding boxes
        bb1_x1 = bb1['left']
        bb1_y1 = bb1['top']
        bb1_x2 = bb1_x1 + bb1['width']
        bb1_y2 = bb1_y1 + bb1['height']

        bb2_x1 = bb2['left']
        bb2_y1 = bb2['top']
        bb2_x2 = bb2_x1 + bb2['width']
        bb2_y2 = bb2_y1 + bb2['height']

        # Determine the coordinates of the intersection rectangle
        x_left = max(bb1_x1, bb2_x1)
        y_top = max(bb1_y1, bb2_y1)
        x_right = min(bb1_x2, bb2_x2)
        y_bottom = min(bb1_y2, bb2_y2)

        # If the coordinates of the intersection rectangle are valid (i.e., the right side is to the right of the left side and the bottom is below the top), 
        # then the bounding boxes overlap. Otherwise, they do not overlap.
        if x_right < x_left or y_bottom < y_top:
            return False  # No overlap
        else:
            return True  # Overlap exists
        
    def process_image(self, image_url):
        logging.info(f"Processing image: {image_url}")

        # Detect the faces in the image.
        logging.debug("Detecting faces...")
        detected_faces_result = self._detect_faces(image_url)

        # Create a dictionary where the key is the faceId and the value is the face data.  We need
        # to be able to lookup bounding box information.
        faces_dict = {face['faceId']: face for face in detected_faces_result}


        # Get any celebrities in the image.
        logging.debug("Detecting celebrities...")
        celebrity_result = self._detect_celebrity(image_url)

        # Extract all face IDs
        face_ids = [face['faceId'] for face in detected_faces_result]

        # Search for similar faces
        logging.debug("Searching for similar faces...")
        similar_faces_results = self._search_for_similar_faces(face_ids)

        persons = []

        # For each similar face result, process it
        for similar_faces_result in similar_faces_results:
            face_id = similar_faces_result['faceId']
            logging.debug(f"Processing face: {face_id}")

            # Initialize the person name as None
            celebrity_name = "Unknown"

            # Get the person id of the most similar face or create a new person if no similar face is found.
            if len(similar_faces_result['candidates']) == 0:
                # create a new person
                person_id = self._create_person(celebrity_name)
                logging.debug(f"No similar face found.  Created new person.  Person ID: {person_id}")
            else:
                person_id = similar_faces_result['candidates'][0]['personId']
                logging.debug(f"Similar face found.  Person ID: {person_id}")

            # Get the faceRectangle of the face
            face_rectangle = faces_dict[face_id]['faceRectangle']

            # Add the face to the person
            logging.debug(f"Adding face {face_id} to person {person_id}.")
            self._add_face_to_person(person_id, image_url, face_rectangle)

            # Loop through the celebrities to see if we got any matches.
            for celebrity in celebrity_result:
                logging.debug(f"Checking for celebrity match against {celebrity['name']}")
                # We need to check if the bounding boxes overlap to determine if the face is a celebrity.
                if self._check_boundingbox_overlap(celebrity['faceRectangle'], face_rectangle):
                    logging.debug(f"Face {face_id} is a {celebrity['name']}.  Assigning celebrity to person {person_id}.")
                    celebrity_name = celebrity['name']
                    self._update_person(person_id, celebrity_name)
                    break

            # Add the person data to the list
            persons.append({
                'person_id': person_id,
                'celebrity_name': celebrity_name,
                'bounding_box': face_rectangle
            })

        logging.info(f"Persons detected: {persons}")
        return persons
