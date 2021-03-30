"""
Defines the urls for the views defined in the Server api.
"""
from django.urls import path

from .views import (DeepstreamServersListCreateDestroyView,
                    DeepstreamServersRetrieveUpdateDestroyView)

urlpatterns = [
    path(
        '',
        DeepstreamServersListCreateDestroyView.as_view(),
        name='deepstream_servers_list_create_delete'),
    path(
        '<pk>',
        DeepstreamServersRetrieveUpdateDestroyView.as_view(),
        name='deepstream_servers_retrieve_update_delete'),
]
