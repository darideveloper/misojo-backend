# myapp/exceptions.py
from rest_framework.views import exception_handler


def json_exception_handler(exc, context):
    # Call the default exception handler
    response = exception_handler(exc, context)
    
    messages = []
    
    if response and "detail" in response.data:
        messages.append(response.data['detail'])
        del response.data['detail']
    else:
        # Create response merging all errors
        for field, error_text in response.data.items():
            field = field.replace('_', ' ')
            
            # Catch the first error message
            if isinstance(error_text, list):
                error_text = error_text[0]
                
            # Catch the first error message from nested objects
            if isinstance(error_text, dict):
                if "message" in error_text:
                    error_text = error_text['message']
                else:
                    error_text = list(error_text.values())[0]
                        
            error_text = error_text.replace('.', '').replace('_', ' ')
            messages.append(f"{field} error: {error_text}")
            
    message = ', '.join(messages)
    
    # Customize the response based on the exception type
    response.data = {
        'status': 'error',
        'message': message,
        'data': response.data
    }
    return response