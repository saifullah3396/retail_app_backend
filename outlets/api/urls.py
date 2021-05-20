"""
Defines the urls for the views defined in the organizations api.
"""

from django.urls import path

from outlets.api.views import (OutletsListCreateDestroyView,
                               OutletsRetrieveUpdateDestroyView,
                               OutletUsersListCreateDestroyView,
                               OutletUsersRetrieveUpdateDestroyView)

urlpatterns = [
    path(
        '',
        OutletsListCreateDestroyView.as_view(),
        name='outlets_list_create_destroy'),
    path(
        '<pk>',
        OutletsRetrieveUpdateDestroyView.as_view(),
        name='outlets_retrieve_update_destroy'),
    path(
        '<outlet>/users/',
        OutletUsersListCreateDestroyView.as_view(),
        name='outlet_users_retrieve_update_destroy'),
    path(
        '<outlet>/users/<pk>',
        OutletUsersRetrieveUpdateDestroyView.as_view(),
        name='outlet_users_retrieve_update_destroy'),
]
