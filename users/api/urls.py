"""
Defines the urls for the views defined in the users api.
"""

from django.urls import path

from users.api.views import (AppUsersListCreateDestroyView,
                             AppUsersRetrieveUpdateDestroyView)

urlpatterns = [
    path(
        '',
        AppUsersListCreateDestroyView.as_view(),
        name='app_users_list_create_delete'),
    path(
        '<pk>',
        AppUsersRetrieveUpdateDestroyView.as_view(),
        name='app_users_retrieve_update_delete'),
]
