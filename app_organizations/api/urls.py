"""
Defines the urls for the views defined in the organizations api.
"""

from django.conf.urls import include
from django.urls import path

from app_organizations.api.group.views import (
    AddUserView, OrganizationGroupsListCreateDestroyView,
    OrganizationGroupsRetrieveUpdateDestroyView, RemoveUserView)
from app_organizations.api.organization.views import (
    AppOrganizationsListCreateDestroyView,
    AppOrganizationsRetrieveUpdateDestroyView,
    AppOrganizationUsersListCreateDestroyView,
    AppOrganizationUsersRetrieveUpdateDestroyView)

users_urlpatters = [
    path(
        '',
        AppOrganizationUsersListCreateDestroyView.as_view(),
        name='app_organization_users_retrieve_update_destroy'),
    path(
        '<pk>/',
        AppOrganizationUsersRetrieveUpdateDestroyView.as_view(),
        name='app_organization_users_retrieve_update_destroy'),
]

groups_urlpatterns = [
    path(
        '',
        OrganizationGroupsListCreateDestroyView.as_view(),
        name='org_groups_list_create_destroy'),
    path(
        '<name>/',
        OrganizationGroupsRetrieveUpdateDestroyView.as_view(),
        name='org_groups_list_create_destroy'),
    path(
        '<name>/users/add/',
        AddUserView.as_view(),
        name='org_groups_add_user'),
    path(
        '<name>/users/remove/',
        RemoveUserView.as_view(),
        name='org_groups_remove_user')
]

organizationpk_urlpatterns = [
    path(
        '',
        AppOrganizationsRetrieveUpdateDestroyView.as_view(),
        name='app_organizations_retrieve_update_destroy'),
    path(
        'users/',
        include(users_urlpatters)),
    path(
        'groups/',
        include(groups_urlpatterns)),
    path('outlets/', include('outlets.api.urls'))
]

urlpatterns = [
    path(
        '',
        AppOrganizationsListCreateDestroyView.as_view(),
        name='app_organizations_list_create_destroy'),
    path(
        '<organization>/',
        include(organizationpk_urlpatterns)
    )
]
