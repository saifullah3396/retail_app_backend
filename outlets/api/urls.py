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
        '<uuid:organization_pk>/outlets/',
        OutletsListCreateDestroyView.as_view(),
        name='outlets_list_create_destroy'),
    path(
        '<uuid:organization_pk>/outlets/<pk>',
        OutletsRetrieveUpdateDestroyView.as_view(),
        name='outlets_retrieve_update_destroy'),
    path(
        '<uuid:organization_pk>/outlets/<uuid:outlet_pk>/users/',
        OutletUsersListCreateDestroyView.as_view(),
        name='outlet_users_retrieve_update_destroy'),
    path(
        '<uuid:organization_pk>/outlets/<uuid:outlet_pk>/users/<pk>',
        OutletUsersRetrieveUpdateDestroyView.as_view(),
        name='outlet_users_retrieve_update_destroy'),
]
