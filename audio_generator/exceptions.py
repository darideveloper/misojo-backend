# myapp/exceptions.py
from rest_framework.views import exception_handler
from rest_framework.response import Response

def json_exception_handler(exc, context):
    
    # Call the default exception handler
    response = exception_handler(exc, context)
    
    messages = []
    
    if "detail" in response.data:
        messages.append(response.data['detail'])
        del response.data['detail']
    else:
        # Create response message from error data
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