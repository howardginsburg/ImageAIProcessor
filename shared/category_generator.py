import os, requests, logging, json

class CategoryGenerator:

    def generate_categories(self, image_url):
        logging.info(f"Generating categories for image: {image_url}")
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
                            "text": "You are a helpful assistant that looks at images and suggests categories based on image recognition.  You must only recommend (Lifestyle, Civil Rights, Entertainment, Sports) as potential categories.  If you are not sure, don't recommend anything.  Your response should always text in a comma separated list."
                        }
                    ]
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Please suggest categories from for the image provided."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"{image_url}"
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
        categories_csv = response.json()['choices'][0]['message']['content']

        categories = [category.strip() for category in categories_csv.split(',')]
        #categories = json.dumps(categories_list)


        logging.info(f"Categories generated: {categories}")

        return categories
        