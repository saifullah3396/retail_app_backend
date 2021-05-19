"""
Defines the urls for this application.
"""

from django.urls import include, path

from .group.views import (AddUserView, GroupsListCreateDestroyView,
                          GroupsRetrieveUpdateDestroyView, RemoveUserView)
from .views import VerifyEmailView, django_rest_auth_null

urlpatterns = [
    path('', include('rest_auth.urls')),
    # overrides verify-email to fix rest-auth bug where verify-email does not
    # filter get request
    path(
        'registration/verify-email/',
        VerifyEmailView.as_view(),
        name='verify_email'),
    path('registration/', include('rest_auth.registration.urls')),
    # removes this url which gets called when verification email is generated.
    # this is not required in our case since our frontend is on react
    path(
        'rest-auth/registration/account-email-verification-sent/',
        django_rest_auth_null,
        name='account_email_verification_sent'),
    path(
        'groups/',
        GroupsListCreateDestroyView.as_view(),
        name='groups_list_create_destroy'),
    path(
        'groups/<name>',
        GroupsRetrieveUpdateDestroyView.as_view(),
        name='groups_retrieve_update_destroy'),
    path(
        'groups/<name>/add/',
        AddUserView.as_view(),
        name='groups_add_user'),
    path(
        'groups/<name>/remove/',
        RemoveUserView.as_view(),
        name='groups_remove_user'),
]
