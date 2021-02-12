from django.urls import path
from .views import *

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
