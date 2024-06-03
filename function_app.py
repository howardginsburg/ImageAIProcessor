import azure.functions as func 
import function_faceorchestrator as faceorchestrator
import function_imagescaler as imagescaler
import function_ainarrative as ainarrative

#app = func.FunctionApp() 
app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

app.register_functions(faceorchestrator.bp) 
app.register_functions(imagescaler.bp)
app.register_functions(ainarrative.bp)     