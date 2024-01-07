# myapp/exceptions.py
from rest_framework.views import exception_handler


def json_exception_handler(exc, context):
    """ Custom exception handler to return JSON response

    Args:
        exc (exception): Exception object
        context (context): Context object

    Returns:
        dict: JSON response
    """
    
    # Call the default exception handler
    response = exception_handler(exc, context)
    
    message = ""
    
    if response and "detail" in response.data:
        message = response.data['detail']
        del response.data['detail']
    else:
        # Create response only with first error
        error_text = list(response.data.values())[0]
        
        # Catch the first error message
        if isinstance(error_text, list):
            error_text = error_text[0]
            
        # Catch the first error message from nested objects
        if isinstance(error_text, dict):
            if "message" in error_text:
                error_text = error_text['message']
            else:
                error_text = list(error_text.values())[0]
            
        # Detect languaje from request
        message = error_text
                
    # Customize the response based on the exception type
    response.data = {
        'status': 'error',
        'message': message,
        'data': response.data
    }
    return response