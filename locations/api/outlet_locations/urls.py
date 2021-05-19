"""
Defines the urls for the views defined in the locations api.
"""

from django.urls import path

from .views import (OrganizationLocationsListCreateDestroyView,
                    OrganizationLocationsRetrieveUpdateDestroyView)

urlpatterns = [
    path(
        '<uuid:organization_pk>/locations/',
        OrganizationLocationsListCreateDestroyView.as_view(),
        name='org_locations_retrieve_update_delete'),
    path(
        '<uuid:organization_pk>/locations/<pk>',
        OrganizationLocationsRetrieveUpdateDestroyView.as_view(),
        name='org_locations_retrieve_update_delete'),
    # path(
    #     'floors/',
    #     FloorsListCreateDestroyView.as_view(),
    #     name='floors_list_create_delete'),
    # path(
    #     'floors/<pk>',
    #     FloorsRetrieveUpdateDestroyView.as_view(),
    #     name='floors_retrieve_update_delete'),
    # path(
    #     'blocks/',
    #     BlocksListCreateDestroyView.as_view(),
    #     name='blocks_list_create_delete'),
    # path(
    #     'blocks/<pk>',
    #     BlocksRetrieveUpdateDestroyView.as_view(),
    #     name='blocks_retrieve_update_delete'),
]
