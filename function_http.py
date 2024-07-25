import logging
import azure.functions as func
import logging
import image_processor


bp = func.Blueprint()

@bp.route(route="orchestrator")
def function_http(req: func.HttpRequest) -> func.HttpResponse:

    logging.info('Orchestrator function triggered.')    

    # Get the filename from the request parameters
    filename = req.params.get('filename')
    if not filename:
        return func.HttpResponse("You must pass in the filename parameter in the query string", status_code=400)
    
    logging.info(f"Orchestrating functions for file: {filename}")

    # Call the ImageProcessor class to process the image
    result_json = image_processor.ImageProcessor().process(filename)

    return func.HttpResponse(result_json, mimetype="application/json", status_code=200)
    
