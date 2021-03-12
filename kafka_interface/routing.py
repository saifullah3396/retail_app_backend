"""
Defines the routing for the consumers
"""

from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path('', consumers.KafkaStreamerConsumer.as_asgi()),
]
