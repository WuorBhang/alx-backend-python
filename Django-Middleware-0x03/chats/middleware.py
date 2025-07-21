import datetime
import logging

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user if request.user.is_authenticated else "Anonymous"
        log_message = f"{datetime.datetime.now()} - User: {user} - Path: {request.path}"
        logger.info(log_message)
        
        # Write to file
        with open('requests.log', 'a') as f:
            f.write(log_message + '\n')

        response = self.get_response(request)
        return response
