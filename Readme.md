# Image Ingest Pipeline

This Azure Functions project is a pipeline for reading images from a blob storage container, resizing them, and processing them through the Azure Face API to determine unique faces, and attempt to identify 'celebrity' faces.

## Prerequisites

1. Azure Storage Account
    - You must create three containers in the storage account: ex: `images`, `resized`, and `results`.
1. Azure AI Services Account (Face API)
    - You must submit a [request](https://learn.microsoft.com/azure/ai-services/computer-vision/overview-identity) to enable usage of the full Face API including face similarity and celebrity recognition.


## Getting Started

1. This repo is setup using devcontainers.  You must have docker installed or run it as a Codespace in Github. If you plan to run it locally, after the project opens, make sure to select 'Yes' when prompted to reopen in container.  This will ensure the correct environment is setup for the project, including the Azure Functions runtime environment.
1. Copy the `local.settings.json.example` file to `local.settings.json` make updates.
    - `BASE_URL` is the base url for the Azure Functions runtime.  For example: `http://localhost:7071` or `https://<appname>.azurewebsites.net`
    - `FUNCTIONS_KEY` is the key for the Azure Functions runtime.  This is used when calling the orchestrator function to call the other functions.  This is not needed when running locally.
    - `AZURE_AI_SERVICE_ENDPOINT` is the endpoint for the Azure AI Service.  For example: `https://<appname>.cognitiveservices.azure.com/`
    - `AZURE_AI_SERVICE_KEY` is the key for the Azure AI Service.
    - `AZURE_STORAGE_CONNECTION` is the connection string for the Azure Storage Account.
    - `ORIGINAL_IMAGE_CONTAINER` is the name of the container where the original images are stored. For example: `images`
    - `RESIZED_IMAGE_CONTAINER` is the name of the container where the resized images are stored. For example: `resized`
    - `ORCHESTRATOR_RESULT_CONTAINER` is the name of the container where the face results are stored. For example: `results`
    - `AZURE_OPEN_AI_ENDPOINT` is the endpoint for the Azure OpenAI Service.  For example: `https://<your openai name>.openai.azure.com/openai/deployments/<your gpt4 turbo deployment>/chat/completions?api-version=2024-05-01-preview`
    - `AZURE_OPEN_AI_KEY` is the key for the Azure OpenAI Service.
1. You can run the project locally by clicking the debug button in VSCode and selecting 'Attach to Python Functions'.

## Architecture Overview

This project contains several functions that can be orchestrated together.  ImageScaler to resize images to 6MB or less as required for facial recognition and then FaceOrchestrator to process the images through the Azure Face API.

### Orchestrator

An http trigger function that accepts an image file in the `images` container.  It will then orchestrate the calling of the ImageScaler, FaceOrchestrator, and AI Narrative functions.  It will then upload the results as a json file `results` container with the face rectangles and celebrity names.

### ImageScaler

An http trigger with the name of an image file in the `images` container.  It will download the image, resize it, and upload it to the `resized` container.

### FaceOrchestrator

An Http trigger with the name of a resized image file in the `resized` container.  It will create a SAS token for the image, process it through the Azure Face API to determine unique faces, and attempt to identify 'celebrity' faces.

![Architecture](/media/faceorchestrator.png)

### AI Narrative

An Http trigger with the name of an image file in the `resized` container.  It will create a SAS token for the image, process it through an Azure OpenAI instance to generate a narrative for an image.

## Deployment

1. Create a new Azure Functions App in the Azure Portal.  You can deploy the project using the Azure Functions extension in VSCode or by using the Azure Functions CLI.
1. You must set the environment variables in the Azure Functions App for the settings in the `local.settings.json` file.