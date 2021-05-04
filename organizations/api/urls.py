"""
Defines the urls for the views defined in the organizations api.
"""

from django.urls import path

from organizations.api.views import (OrganizationsListCreateDestroyView,
                                     OrganizationsRetrieveUpdateDestroyView)

urlpatterns = [
    path(
        '',
        OrganizationsListCreateDestroyView.as_view(),
        name='organizations_list_create_delete'),
    path(
        '<pk>',
        OrganizationsRetrieveUpdateDestroyView.as_view(),
        name='organizations_retrieve_update_delete'),
]
