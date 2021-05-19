"""
Defines the urls for the views defined in the organizations api.
"""

from django.urls import path

from app_organizations.api.group.views import (
    AddUserView, OrganizationGroupsListCreateDestroyView,
    OrganizationGroupsRetrieveUpdateDestroyView, RemoveUserView)
from app_organizations.api.organization.views import (
    AppOrganizationsListCreateDestroyView,
    AppOrganizationsRetrieveUpdateDestroyView,
    AppOrganizationUsersListCreateDestroyView,
    AppOrganizationUsersRetrieveUpdateDestroyView)

urlpatterns = [
    path(
        '',
        AppOrganizationsListCreateDestroyView.as_view(),
        name='app_organizations_list_create_destroy'),
    path(
        '<uuid:organization_pk>',
        AppOrganizationsRetrieveUpdateDestroyView.as_view(),
        name='app_organizations_retrieve_update_destroy'),
    path(
        '<uuid:organization_pk>/users/',
        AppOrganizationUsersListCreateDestroyView.as_view(),
        name='app_organization_users_retrieve_update_destroy'),
    path(
        '<uuid:organization_pk>/users/<pk>',
        AppOrganizationUsersRetrieveUpdateDestroyView.as_view(),
        name='app_organization_users_retrieve_update_destroy'),
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
