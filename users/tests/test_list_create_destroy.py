"""
Defines the unit tests related to 'create' api requests for this application.
"""
# pylint: disable=line-too-long

from django.contrib.auth import get_user_model
from django.urls import include, path
from django_filters.rest_framework import backends
from rest_framework import status

from backend import urls
from core.tests.base import TestsBase
from core.tests.utils import generate_fake_data
from user_auth.tests.factories import group_factory
from users.tests.factories import user_factory

# get user model
USER_MODEL = get_user_model()
NUM_TEST_USERS = 10


class AppUsersListCreateDestroyTests(TestsBase):
    """
    Defines unit tests for 'list/create/destroy' api requests for views
    defined at 'users/' url.

    Attributes:
        api_urlpatterns: Api url patterns used in this test unit.
        urlpatterns: Complete url pattern used in this test unit.
    """

    urlpatterns = urls.urlpatterns

    def generate_factory_data(self):
        """
        Generates factory data that can be used in test cases
        """
        self.groups = group_factory.generate_group_factory()
        self.users, self.tokens = \
            user_factory.generate_user_factory(num_users=NUM_TEST_USERS)

    def create_user_response_check_fn(self, user, response, *args, **kwargs):
        """
        Create is forbidden for every use as it is done through registration
        """
        if user.is_staff:
            self.assertEqual(response.status_code,
                             status.HTTP_405_METHOD_NOT_ALLOWED)
        else:
            self.assertEqual(response.status_code,
                             status.HTTP_403_FORBIDDEN)

    def list_users_response_check_fn(self, user, response, *args, **kwargs):
        """
        Super user can see all users while normal users only themselves.
        """
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        if user.is_superuser:
            # super user gets list of all users
            self.assertEqual(
                len(response.data['results']), len(USER_MODEL.objects.all()))
        else:
            # a normal only returns list of normal users
            self.assertEqual(
                len(response.data['results']),
                len(USER_MODEL.objects.exclude(is_staff=True, is_superuser=True)))

    def generate_data_for_id_list_users(self, with_superuser=True):
        """
        Generates a list of users which can then be deleted
        """
        id_list = []

        if with_superuser:
            # generate a super user to be deleted
            id_list.append(
                user_factory.SuperUserFactory.create(username='admin2'))

        # generate app users to be deleted
        id_list.extend(user_factory.AppUserFactory.create_batch(
            2, groups=(self.groups['FREE_USER'],)))

        return [('id', user.id) for user in id_list]

    def id_list_users_with_superuser_response_check_fn(self, user, response, query_params, *args, **kwargs):
        """
        Users can be id listed by any user as long as no super user is
        involved in query
        """
        if user.is_superuser:
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        else:
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def id_list_users_without_superuser_response_check_fn(self, user, response, query_params, *args, **kwargs):
        """
        Users can be id listed by any user as long as no super user is involved in query
        """
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.data['results']), len(query_params))

    def list_destroy_users_response_check_fn(self, response, *args, **kwargs):
        """
        Any user cannot delete all users in obtained list.
        """
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def generate_data_for_id_list_destroy_users(self):
        """
        Generates a list of users which can then be deleted
        """
        to_be_del_users_list = []

        # generate a super user to be deleted
        to_be_del_users_list.append(
            user_factory.SuperUserFactory.create(username='admin2'))

        # generate app users to be deleted
        to_be_del_users_list.extend(user_factory.AppUserFactory.create_batch(
            2, groups=(self.groups['FREE_USER'],)))

        return [('id', user.id) for user in to_be_del_users_list]

    def id_list_destroy_users_response_check_fn(self, user, response, *args, **kwargs):
        """
        Users can be delete with ids list as input only by staff
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
                'test_name': 'create_user',
                'type': 'post',
                'path_name': 'app_users_list_create_destroy',
                'request': [
                    {
                        'name': 'create_user_random_data',
                        'data': lambda: generate_fake_data(
                            user_factory.AppUserFactory),
                        'response_check_fn':
                            self.create_user_response_check_fn,
                        # user contains an image so send it as multipart
                        'data_format': 'multipart',
                    },
                ]
            },
            {
                'test_name': 'list_users',
                'type': 'get',
                'path_name': 'app_users_list_create_destroy',
                'request': [
                    {
                        'name': 'list_users',
                        'response_check_fn': self.list_users_response_check_fn,
                    },
                ]
            },
            {
                'test_name': 'id_list_users',
                'type': 'get',
                'path_name': 'app_users_list_create_destroy',
                'request': [
                    {
                        'name': 'id_list_users_without_superuser',
                        'query_params': self.generate_data_for_id_list_users(with_superuser=False),
                        'response_check_fn': self.id_list_users_without_superuser_response_check_fn,
                    },
                    {
                        'name': 'id_list_users_with_superuser',
                        'query_params': self.generate_data_for_id_list_users(with_superuser=True),
                        'response_check_fn': self.id_list_users_with_superuser_response_check_fn,
                    },
                ]
            },
            {
                'test_name': 'list_destroy_users',
                'type': 'delete',
                'path_name': 'app_users_list_create_destroy',
                'request': [
                    {
                        'name': 'list_destroy_users',
                        'response_check_fn': self.list_destroy_users_response_check_fn,
                    },
                ]
            },
            {
                'test_name': 'id_list_destroy_users',
                'type': 'delete',
                'path_name': 'app_users_list_create_destroy',
                'request': [
                    {
                        'name': 'id_list_destroy_users',
                        'query_params': self.generate_data_for_id_list_destroy_users(),
                        'response_check_fn': self.id_list_destroy_users_response_check_fn,
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
            self.run_single_test(test_config, show_passed=False)
