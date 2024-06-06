import azure.functions as func 
import function_facialdetection as facialdetection
import function_imagescaler as imagescaler
import function_ainarrative as ainarrative
import function_orchestrator as orchestrator

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

app.register_functions(facialdetection.bp) 
app.register_functions(imagescaler.bp)
app.register_functions(ainarrative.bp)  
app.register_functions(orchestrator.bp)   