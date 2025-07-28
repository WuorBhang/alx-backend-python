from datetime import datetime
import logging
from django.http import HttpResponse, HttpResponseForbidden
from django.core.cache import cache

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user if request.user.is_authenticated else "Anonymous"
        log_message = f"{datetime.now()} - User: {user} - Path: {request.path}"
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
        if current_hour < 9 or current_hour > 17:
            return HttpResponse("Access denied outside business hours (9 AM - 5 PM).", status=403)
        response = self.get_response(request)
        return response


class OffensiveLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.limit = 5  # Max 5 messages
        self.window = 60  # Per 60 seconds

    def __call__(self, request):
        if request.method == 'POST' and request.path.startswith('/messages/'):
            ip = request.META.get('REMOTE_ADDR')
            key = f"message_limit_{ip}"
            current = cache.get(key, 0)
            if current >= self.limit:
                return HttpResponseForbidden("Message rate limit exceeded. Please try again later.")
            cache.set(key, current + 1, self.window)
        return self.get_response(request)


class RolePermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/') and not request.user.is_staff:
            return HttpResponseForbidden("You don't have permission to access this page.")
        return self.get_response(request)


# Optional middleware below — remove if not used

class CustomWebSocketMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        pass

    async def process_websocket(self, scope, receive, send):
        pass


class LogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print(f"Request Method: {request.method} | Path: {request.path}")
        response = self.get_response(request)
        return response