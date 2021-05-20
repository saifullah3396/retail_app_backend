"""
Defines the urls for the views defined in the users api.
"""

from django.conf.urls import include
from django.urls import path

from users.api.app_user.views import (AppUsersListCreateDestroyView,
                                      AppUsersRetrieveUpdateDestroyView)

urlpatterns = [
    path(
        '',
        AppUsersListCreateDestroyView.as_view(),
        name='app_users_list_create_destroy'),
    path(
        '<pk>/',
        AppUsersRetrieveUpdateDestroyView.as_view(),
        name='app_users_retrieve_update_destroy'),
    path('auth/', include('user_auth.api.urls'))
]
