"""
Defines the urls for the views defined in the Server api.
"""
from django.urls import path

from ds_servers.api.views import (DSServersListCreateDestroyView,
                                  DSServersRetrieveUpdateDestroyView)

urlpatterns = [
    path(
        '',
        DSServersListCreateDestroyView.as_view(),
        name='ds_servers_list_create_delete'),
    path(
        '<pk>/',
        DSServersRetrieveUpdateDestroyView.as_view(),
        name='ds_servers_retrieve_update_delete'),
]
