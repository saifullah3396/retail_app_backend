"""
Defines the routing for the consumers
"""

from channels.http import AsgiHandler
from django.conf.urls import url
from django.core.asgi import get_asgi_application
from django.urls import re_path

from . import deepstream_backend_streamer, deepstream_frontend_streamer

websocket_urlpatterns = [
    re_path(
        r'^deepstream/client/(?P<group_id>[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12})/$',
        deepstream_frontend_streamer.DeepstreamFrontendStreamer.as_asgi()),
    re_path(
        # r'^deepstream/server/(?P<group_id>[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12})/$',
        r'^deepstream/server/',
        deepstream_backend_streamer.DeepstreamBackendStreamer.as_asgi()),
    url(r'', get_asgi_application()),
]

# http_urlpatterns = [
#     # re_path(
#     #     # r'^deepstream/server/(?P<group_id>[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12})/$',
#     #     r'^deepstream/server/',
#     #     deepstream_live_receiver.DeepstreamBackendStreamer.as_asgi()),
#     url(r'', get_asgi_application()),
# ]
