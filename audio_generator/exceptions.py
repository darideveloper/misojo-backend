# myapp/exceptions.py
from rest_framework.views import exception_handler


def json_exception_handler(exc, context):
    
    # Call the default exception handler
    response = exception_handler(exc, context)
    
    # Create response message from error data
    messages = []
    for field, error_text in response.data.items():
        messages.append(f"{field} error: {error_text[0].replace('.', '')}")
        
    message = ', '.join(messages)
    
    # Customize the response based on the exception type
    response.data = {
        'status': 'error',
        'message': message,
        'data': response.data
    }
    return response