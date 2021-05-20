"""
Defines the unit tests related to 'create' api requests for this application.
"""

from django.urls import include, path
from rest_framework import status

from app_organizations.models import AppOrganization, DefaultOrganizationGroups
from app_organizations.tests.factories import app_organization_factory
from core.tests.base import TestsBase
from core.tests.utils import generate_fake_data
from users.tests.factories.user_factory import generate_user_factory

NUM_TEST_USERS = 10
NUM_TEST_ORGS = 10


# pylint: disable=line-too-long
class AppOrganizationsRetrieveUpdateDestroyTests(TestsBase):
    """
    Defines unit tests for 'retrieve/update/destroy' api requests for views
    defined at 'organizations/' url.

    Attributes:
        api_urlpatterns: Api url patterns used in this test unit.
        urlpatterns: Complete url pattern used in this test unit.
    """

    api_urlpatterns = [
        path('organizations/', include('app_organizations.api.urls')),
    ]

    urlpatterns = [
        path('api/v1/', include(api_urlpatterns)),
    ]

    def generate_factory_data(self):
        """
        Generates factory data that can be used in test cases that require
        organizations
        """
        # create users
        self.users, self.tokens = generate_user_factory(
            num_users=NUM_TEST_USERS)

        # create orgs
        self.orgs = \
            app_organization_factory.generate_org_factory(
                num_orgs=NUM_TEST_ORGS)

        # add users to orgs
        self.org_users = \
            app_organization_factory.generate_org_users_factory(
                self.users.values(), self.orgs.values())

    def retrieve_organization_response_check_fn(
            self, user, response, query_args, *args, **kwargs):
        """
        Super user can see all organizations while normal users only their
        organizations.
        """
        query_organization = self.orgs[query_args['organization']]

        if user.is_superuser:
            # super user can get every user detail
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        else:
            if query_organization.users.filter(id=user.id).exists():
                # if user is within the organization, he can get it
                self.assertEqual(response.status_code, status.HTTP_200_OK)
            else:
                # if user is not within the organization
                self.assertEqual(
                    response.status_code,
                    status.HTTP_403_FORBIDDEN)

    def update_organization_response_check_fn(
            self, user, data, response, query_args, *args, **kwargs):
        """
        Super user can update all organizations while normal users can only
        update their own organizations.
        """
        query_organization = AppOrganization.objects.get(
            id=query_args['organization'])

        if user.is_superuser:
            # super user can get every user detail
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        else:
            # get the all users within the organization and see if current
            # user exist within it
            org_user = query_organization.organization_users.filter(
                user=user).first()
            if not org_user:
                # if user is not within the organization
                self.assertEqual(
                    response.status_code,
                    status.HTTP_403_FORBIDDEN)
            else:
                # check user organization group
                if not org_user.groups.filter(name=DefaultOrganizationGroups.ADMIN.name):
                    # forbidden if not admin
                    self.assertEqual(
                        response.status_code,
                        status.HTTP_403_FORBIDDEN)
                else:
                    self.assertEqual(response.status_code, status.HTTP_200_OK)

        if response.status_code == status.HTTP_200_OK:
            # make sure only the updatable data is updated
            self.assertDictContainsSubset(
                {
                    'id': query_organization.id,  # unchanged field
                    'name': data['name'],  # changed field
                },
                response.data)

            # make sure avatar is uploaded on the correct link
            self.assertIn(
                'http://testserver/media/organizations/avatars/avatar',
                response.data['avatar'])

    def destroy_organization_response_check_fn(
            self, user, response, query_args, *args, **kwargs):
        """
        Super users can destroy all organizations. Normal users can only
        destroy organizations to which they are the owners.
        """

        query_organization = AppOrganization.objects.get(
            id=query_args['organization'])

        if user.is_superuser:
            # super user can get every user detail
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        else:
            # get the all users within the organization and see if current
            # user exist within it
            org_user = query_organization.organization_users.filter(
                user=user).first()
            if not org_user:
                # if user is not within the organization
                self.assertEqual(
                    response.status_code,
                    status.HTTP_403_FORBIDDEN)
            else:
                # check user organization group
                if org_user.groups.filter(name=DefaultOrganizationGroups.OWNER.name).exists():
                    self.assertEqual(response.status_code, status.HTTP_200_OK)
                else:
                    # forbidden if not owner
                    self.assertEqual(
                        response.status_code,
                        status.HTTP_403_FORBIDDEN)

    def setUp(self):
        """
        Sets up the test cases.
        """
        super().setUp()
        self.tests = [
            {
                'test_name': 'retrieve_organization',
                'type': 'get',
                'path_name': 'app_organizations_retrieve_update_destroy',
                'request': [
                    {
                        'name': 'retrieve_organization_{}'.format(org.name),
                        'query_args': {'organization': org.id},
                        'response_check_fn': self.retrieve_organization_response_check_fn,
                    }  # generate requests for all organizations to retrieve all other organizations
                    for org in self.orgs.values()]
            },
            {
                'test_name': 'update_organization',
                'type': 'put',
                'path_name': 'app_organizations_retrieve_update_destroy',
                'request': [
                    {
                        'name': 'update_organization_{}'.format(org.name),
                        'data': lambda: {  # this regenerates new data every time
                            **generate_fake_data(app_organization_factory.AppOrganizationFactory),
                        },
                        'data_format': 'multipart',
                        'query_args': {'organization': org.id},
                        'response_check_fn': self.update_organization_response_check_fn,
                    }  # generate requests for all organizations to update all other organizations
                    for org in self.orgs.values()]
            },
            {
                'test_name': 'destroy_organization',
                'type': 'delete',
                'path_name': 'app_organizations_retrieve_update_destroy',
                'request': [
                    {
                        'name': 'destroy_organization_{}'.format(org.name),
                        # undelete deleted organization models
                        'query_args': {'organization': org.id},
                        # undelete all organizations to test results
                        'post_test_cb': lambda: AppOrganization.objects.deleted_only().undelete(),
                        'response_check_fn': self.destroy_organization_response_check_fn,
                    }  # generate requests for all organizations to delete all other organizations
                    for org in self.orgs.values()]
            },
        ]

    def test_(self):
        """
        The single test function that runs all the test cases defined in
        the self.test.
        """
        for test_config in self.tests:
            self.run_single_test(test_config, show_passed=False)
