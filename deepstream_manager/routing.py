"""
Defines the routing for the consumers
"""

from django.conf.urls import url
from django.core.asgi import get_asgi_application
from django.urls import re_path

# from . import deepstream_backend_streamer, deepstream_frontend_streamer

UUID_REGEX = \
    '[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}'

websocket_urlpatterns = [
    # re_path(
    #     r'^deepstream/client/(?P<group_id>{})/$'.format(UUID_REGEX),
    #     deepstream_frontend_streamer.DeepstreamFrontendStreamer.as_asgi()),
    # re_path(
    #     r'^deepstream/server/',
    #     deepstream_backend_streamer.DeepstreamBackendStreamer.as_asgi()),
    url(r'', get_asgi_application()),
]
