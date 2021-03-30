"""
Defines the urls for the views defined in the Server api.
"""
from django.urls import path

from .views import (ServersListCreateDestroyView,
                    ServersRetrieveUpdateDestroyView)

urlpatterns = [
    path(
        '',
        ServersListCreateDestroyView.as_view(),
        name='servers_list_create_delete'),
    path(
        '<pk>',
        ServersRetrieveUpdateDestroyView.as_view(),
        name='servers_retrieve_update_delete'),
]
