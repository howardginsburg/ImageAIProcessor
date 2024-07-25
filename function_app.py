import logging
import azure.functions as func
import logging
import function_http
import function_blob


app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

app.register_functions(function_http.bp)
app.register_functions(function_blob.bp)