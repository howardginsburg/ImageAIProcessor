import os, logging, json, datetime
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from concurrent.futures import ThreadPoolExecutor
import shared.image_scaler as image_scaler
import shared.facial_recognition as facial_recognition
import shared.narrative_generator as narrative_generator
import shared.category_generator as category_generator
import logging

class ImageProcessor:
    def process(self, filename):
        
        logging.info(f"Processing file: {filename}")
        start_time = datetime.datetime.now()

        result_dict = {}
        result_dict["metrics"] = {}
        result_dict["filename"] = filename

        blob_service_client = BlobServiceClient.from_connection_string(os.getenv('STORAGE_ACCOUNT_CONNECTION')) 

        logging.info(f"Calling ImageScaler function for file: {filename}")
        resized_result = self._resize_image(filename)
        resized_filename = resized_result["resized_filename"]
        result_dict["resizedfilename"] = resized_filename
        result_dict["metrics"]["image_resize"] = resized_result["total_time"]

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

        
        logging.info(f"Calling Face Processing, Narrative generation, and Category generation in parallel for file: {resized_filename}")
        # Execute API calls in parallel
        with ThreadPoolExecutor(max_workers=2) as executor:
            face_orchestrator_future = executor.submit(self._call_face_orchestrator, sas_url)
            ai_narrative_future = executor.submit(self._call_ai_narrative, sas_url)
            categories_future = executor.submit(self._call_categories, sas_url)

            face_api_result = face_orchestrator_future.result()
            ai_narrative_result = ai_narrative_future.result()
            categories_result = categories_future.result()

        # Add results to the result dictionary
        result_dict["facedetails"] = face_api_result["face_result"]
        result_dict["metrics"]["facial_recognition"] = face_api_result["total_time"]
        result_dict["ainarrative"] = ai_narrative_result["narrative"]
        result_dict["metrics"]["ai_narrative"] = ai_narrative_result["total_time"]
        result_dict["categories"] = categories_result["categories_result"]
        result_dict["metrics"]["ai_categories"] = categories_result["total_time"]

        end_time = datetime.datetime.now()

        total_time = (end_time - start_time).total_seconds()
        result_dict["metrics"]["total_time"] = total_time

        logging.info(f"Processing completed in {total_time} seconds")

        # Convert the result back to json
        result_json = json.dumps(result_dict)

        if (os.getenv('ORCHESTRATOR_RESULT_CONTAINER') is not None):
            # Create a new BlobClient for the results json blob
            result_file = f"{os.path.splitext(filename)[0]}.json"
        
            result_service_client = blob_service_client

            if (os.getenv('ORCHESTRATOR_RESULT_CONNECTION') is not None):
                result_service_client = BlobServiceClient.from_connection_string(os.getenv('ORCHESTRATOR_RESULT_CONNECTION'))

            result_blob_client = result_service_client.get_blob_client(os.getenv('ORCHESTRATOR_RESULT_CONTAINER'), result_file)
            # Upload the result blob.
            result_blob_client.upload_blob(result_json, overwrite=True)

        self._save_to_database(result_json)

        # Log the result
        logging.info(f"Processing result: {result_json}")

        return result_json

    def _resize_image(self,filename):
        start_time = datetime.datetime.now()
        resized_filename = image_scaler.ImageHelper().resize(filename)
        end_time = datetime.datetime.now()

        total_time = (end_time - start_time).total_seconds()
        logging.info(f"Image resizing completed in {total_time} seconds")

        # Create a dictionary with the results
        result = {
            'resized_filename': resized_filename,
            'total_time': total_time
        }

        return result

    def _call_face_orchestrator(self,sas_url):
        start_time = datetime.datetime.now()
        face_result = facial_recognition.AzureFaceRecognition().process_image(sas_url)
        end_time = datetime.datetime.now()

        total_time = (end_time - start_time).total_seconds()
        logging.info(f"Face recognition completed in {total_time} seconds")

        result = {
            'face_result': face_result,
            'total_time': total_time
        }
        return result

    def _call_ai_narrative(self,sas_url):
        start_time = datetime.datetime.now()
        narrative = narrative_generator.NarrativeGenerator().generate_narrative(sas_url)
        end_time = datetime.datetime.now()

        total_time = (end_time - start_time).total_seconds()
        logging.info(f"AI narrative generation completed in {total_time} seconds")

        result = {
            'narrative': narrative,
            'total_time': total_time
        }
        return result

    def _call_categories(self,sas_url):
        start_time = datetime.datetime.now()
        categories = category_generator.CategoryGenerator().generate_categories(sas_url)
        end_time = datetime.datetime.now()

        total_time = (end_time - start_time).total_seconds()
        logging.info(f"AI category generation completed in {total_time} seconds")

        result = {
            'categories_result': categories,
            'total_time': total_time
        }
        return result

    def _save_to_database(self, result_json):
        # TODO - Save the result to a database
        logging.info(f"TODO!!!! Saving result to database!")