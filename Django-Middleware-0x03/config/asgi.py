"""
ASGI config for messaging_app project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see:
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
https://channels.readthedocs.io/en/stable/deploying.html
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from chats.routing import websocket_urlpatterns

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Initialize Django ASGI application early for HTTP requests
django_asgi_app = get_asgi_application()

# Combine protocols (HTTP + WebSocket) with security layers
application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(URLRouter(websocket_urlpatterns))
        ),
    }
)