"""
Defines the urls for this application.
"""

from django.urls import include, path

from .group.views import (AddUserView, OrganizationGroupsListCreateDestroyView,
                          OrganizationGroupsRetrieveUpdateDestroyView,
                          RemoveUserView)

urlpatterns = [
    path(
        '<uuid:organization_pk>/groups/',
        OrganizationGroupsListCreateDestroyView.as_view(),
        name='org_groups_list_create_destroy'),
    path(
        '<uuid:organization_pk>/groups/<name>',
        OrganizationGroupsRetrieveUpdateDestroyView.as_view(),
        name='org_groups_list_create_destroy'),
    path(
        '<uuid:organization_pk>/groups/<name>/users/add/',
        AddUserView.as_view(),
        name='org_groups_add_user'),
    path(
        '<uuid:organization_pk>/groups/<name>/users/remove/',
        RemoveUserView.as_view(),
        name='org_groups_remove_user')
]
