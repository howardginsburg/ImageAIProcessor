import os, requests, logging

class NarrativeGenerator:

    def generate_narrative(self, image_url):
        logging.info(f"Generating narrative for image: {image_url}")
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
        narrative = response.json()['choices'][0]['message']['content']

        logging.info(f"Narrative generated: {narrative}")

        return narrative
        