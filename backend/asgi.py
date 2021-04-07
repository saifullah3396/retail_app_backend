"""
ASGI Application definition for django channels api.
"""

import os

import deepstream_manager.routing
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    # "http": AuthMiddlewareStack(
    #     URLRouter(
    #         deepstream_manager.routing.http_urlpatterns
    #     )
    # ),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            deepstream_manager.routing.websocket_urlpatterns
        )
    ),
})
