"""
ASGI config for NaijaBay project.

HTTP requests go to Django views; WebSockets (messaging) go through
Channels with cookie-JWT authentication.

Run with:  daphne -p 8000 NaijaBay.asgi:application   (or uvicorn)
"""

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NaijaBay.settings')

import django  # noqa: E402

django.setup()

from messaging.middleware import jwt_cookie_auth_middleware  # noqa: E402
from messaging.routing import websocket_urlpatterns  # noqa: E402

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AllowedHostsOriginValidator(
            jwt_cookie_auth_middleware(AuthMiddlewareStack(URLRouter(websocket_urlpatterns)))
        ),
    }
)
