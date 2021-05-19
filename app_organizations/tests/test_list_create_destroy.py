"""
Defines the unit tests related to 'create' api requests for this application.
"""


from django.urls import include, path
from rest_framework import status

from app_organizations.models import AppOrganization
from app_organizations.tests.factories import app_organization_factory
from backend import urls
from core.tests.base import TestsBase
from core.tests.utils import generate_fake_data
from users.tests.factories.user_factory import generate_user_factory

NUM_TEST_USERS = 10
NUM_TEST_ORGS = 10


# pylint: disable=line-too-long
class AppOrganizationsListCreateDestroyTests(TestsBase):
    """
    Defines unit tests for 'list/create/destroy' api requests for views
    defined at 'organizations/' url.

    Attributes:
        api_urlpatterns: Api url patterns used in this test unit.
        urlpatterns: Complete url pattern used in this test unit.
    """

    urlpatterns = urls.urlpatterns

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

    def create_organization_response_check_fn(
            self, response, *args, **kwargs):
        """
        Create can be called by any registered user
        """
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def list_organizations_response_check_fn(
            self, user, response, *args, **kwargs):
        """
        Super user can list all organizations while normal users can only list
        their own.
        """
        if user.is_superuser:
            self.assertEqual(
                len(response.data['results']),
                len(AppOrganization.objects.all()),
                "Number of results don't match!")
        else:
            # a normal user can only see organizations that are active and
            # attached to user
            self.assertEqual(
                len(response.data['results']),
                len(AppOrganization.objects.filter(users=user)),
                "Number of results don't match!")

    def list_destroy_organizations_response_check_fn(
            self, response, *args, **kwargs):
        """
        Any user cannot delete all organizations in obtained list.
        """
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def generate_data_for_id_list_destroy_organizations(self):
        """
        Generates a list of organizations which can then be deleted
        """
        to_be_del_organizations_list = []

        # generate app organizations to be deleted
        to_be_del_organizations_list.extend(
            app_organization_factory.AppOrganizationFactory.create_batch(2))

        return [
            ('id', organization.id)
            for organization in to_be_del_organizations_list]

    def id_list_destroy_organizations_response_check_fn(
            self, user, response, *args, **kwargs):
        """
        Organizations can be delete with ids list as input only by staff
        """
        if user.is_superuser:
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        else:
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def setUp(self):
        """
        Sets up the test cases.
        """
        super().setUp()

        self.tests = [
            {
                'test_name': 'create_organization',
                'type': 'post',
                'path_name': 'app_organizations_list_create_destroy',
                'request': [
                    {
                        'name': 'create_organization_random_data',
                        'data': lambda: generate_fake_data(
                            app_organization_factory.AppOrganizationFactory),
                        'response_check_fn':
                            self.create_organization_response_check_fn,
                        # organization contains an image so send it as
                        # multipart
                        'data_format': 'multipart',
                    },
                ]
            },
            {
                'test_name': 'list_organizations',
                'type': 'get',
                'path_name': 'app_organizations_list_create_destroy',
                'request': [
                    {
                        'name': 'list_organizations',
                        'response_check_fn': self.list_organizations_response_check_fn,
                    },
                ]
            },
            {
                'test_name': 'list_destroy_organizations',
                'type': 'delete',
                'path_name': 'app_organizations_list_create_destroy',
                'request': [
                    {
                        'name': 'list_destroy_organizations',
                        'response_check_fn': self.list_destroy_organizations_response_check_fn,
                    },
                ]
            },
            {
                'test_name': 'id_list_destroy_organizations',
                'type': 'delete',
                'path_name': 'app_organizations_list_create_destroy',
                'request': [
                    {
                        'name': 'id_list_destroy_organizations',
                        'query_params': self.generate_data_for_id_list_destroy_organizations(),
                        'response_check_fn': self.id_list_destroy_organizations_response_check_fn,
                        # undelete deleted user models
                        'post_test_cb': lambda: AppOrganization.objects.deleted_only().undelete(),
                    },
                ]
            }
        ]

    def test_(self):
        """
        The single test function that runs all the test cases defined in
        the self.test.
        """
        for test_config in self.tests:
            self.run_single_test(test_config)
