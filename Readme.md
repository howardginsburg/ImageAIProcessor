# Image Ingest Pipeline

This Azure Functions project is a pipeline for reading images from a blob storage container, resizing them, and processing them through the Azure Face API to determine unique faces, and attempt to identify 'celebrity' faces.

## Prerequisites

1. Azure Storage Account
    - You must create three containers in the storage account: ex: `images`, `resized`, and `face`.
1. Azure AI Services Account (Face API)
    - You must submit a [request](https://learn.microsoft.com/azure/ai-services/computer-vision/overview-identity) to enable usage of the full Face API including face similarity and celebrity recognition.


## Getting Started

1. This repo is setup using devcontainers.  You must have docker installed or run it as a Codespace in Github. If you plan to run it locally, after the project opens, make sure to select 'Yes' when prompted to reopen in container.  This will ensure the correct environment is setup for the project, including the Azure Functions runtime environment.
1. Copy the `local.settings.json.example` file to `local.settings.json` and update the values with your Azure Storage Account and Face API keys.
1. You can run the project locally by clicking the debug button in VSCode and selecting 'Attach to Python Functions'.

## Architecture Overview

This project contains several functions that can be orchestrated together.  ImageScaler to resize images to 6MB or less as required for facial recognition and then FaceOrchestrator to process the images through the Azure Face API.

### ImageScaler

An http trigger with the name of an image file in the `images` container.  It will download the image, resize it, and upload it to the `resized` container.

### FaceOrchestrator

An Http trigger with the name of a resized image file in the `resized` container.  It will create a SAS token for the image, process it through the Azure Face API to determine unique faces, and attempt to identify 'celebrity' faces.  It will then upload the results as a json file `face` container with the face rectangles and celebrity names.

![Architecture](/media/faceorchestrator.png)

