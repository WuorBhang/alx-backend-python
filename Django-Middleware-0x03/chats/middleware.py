import datetime
import logging
from django.http import HttpResponseForbidden
from django.core.cache import cache

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user if request.user.is_authenticated else "Anonymous"
        log_message = f"{datetime.datetime.now()} - User: {user} - Path: {request.path}"
        logger.info(log_message)
        
        # Write to log file
        with open('requests.log', 'a') as f:
            f.write(log_message + '\n')

        response = self.get_response(request)
        return response

class RestrictAccessByTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        current_hour = datetime.now().hour

        # Deny access if time is not between 6PM (18) and 9PM (21)
        if current_hour < 18 or current_hour >= 21:
            return HttpResponseForbidden("Access to chat is only allowed between 6PM and 9PM.")

        return self.get_response(request)

class OffensiveLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.limit = 5  # 5 messages
        self.window = 60  # 60 seconds

    def __call__(self, request):
        if request.method == 'POST' and request.path.startswith('/messages/'):
            ip = request.META.get('REMOTE_ADDR')
            key = f"message_limit_{ip}"
            
            current = cache.get(key, 0)
            if current >= self.limit:
                return HttpResponseForbidden("Message rate limit exceeded. Please try again later.")
            
            cache.set(key, current + 1, self.window)
        
        return self.get_response(request)

class RolepermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Example check — you can adjust it based on requirements
        if request.path.startswith('/admin/') and not request.user.is_staff:
            return HttpResponseForbidden("You don't have permission to access this page.")
        return self.get_response(request)

class CustomWebSocketMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Middleware logic for HTTP requests
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        # Optional: Logic to process before a view is called
        pass

    async def process_websocket(self, scope, receive, send):
        # Middleware logic for WebSocket connections
        pass

class LogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print(f"Request Method: {request.method} | Path: {request.path}")
        response = self.get_response(request)
<<<<<<< HEAD
        return response
=======
        return response
>>>>>>> e7ebee07b92fb9c6a3fa560f522960f1d726ab71
