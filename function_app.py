import azure.functions as func 
import function_faceorchestrator as faceorchestrator
import function_imagescaler as imagescaler

#app = func.FunctionApp() 
app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

app.register_functions(faceorchestrator.bp) 
app.register_functions(imagescaler.bp)   