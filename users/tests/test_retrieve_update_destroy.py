"""
Defines the unit tests related to 'create' api requests for this application.
"""
# pylint: disable=line-too-long

from backend import urls
from django.contrib.auth import get_user_model
from django.urls import include, path
from rest_framework import status

from core.tests.base import TestsBase
from core.tests.utils import generate_fake_data
from user_auth.tests.factories import group_factory
from users.tests.factories import user_factory

# get user model
USER_MODEL = get_user_model()
NUM_TEST_USERS = 10


class AppUsersRetrieveUpdateDestroyTests(TestsBase):
    """
    Defines unit tests for 'retrieve/update/destroy' api requests for views
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

    def retrieve_user_response_check_fn(
            self, user, response, query_args, *args, **kwargs):
        """
        Super user can see all users while normal users only themselves.
        """
        if user.is_superuser:
            # super user can get every user detail
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        else:
            if query_args['pk'] == user.id:  # a normal can see himself
                self.assertEqual(response.status_code, status.HTTP_200_OK)
            else:  # not found otherwise
                self.assertEqual(response.status_code,
                                 status.HTTP_404_NOT_FOUND)

    def update_user_response_check_fn(
            self, user, data, response, query_args, *args, **kwargs):
        """
        Super user can update all users while normal users only themselves.
        """
        if user.is_superuser:
            # super user can updated every user
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        else:
            if query_args['pk'] == user.id:  # a normal can see himself
                self.assertEqual(response.status_code, status.HTTP_200_OK)
            else:  # not found otherwise
                self.assertEqual(
                    response.status_code,
                    status.HTTP_404_NOT_FOUND)

        if response.status_code == status.HTTP_200_OK:
            # make sure only the updatable data is updated
            updated_user = self.users[query_args['pk']]
            self.assertDictContainsSubset(
                {
                    'id': str(updated_user.id),  # unchanged field
                    'username': updated_user.username,  # unchanged field
                    'email': updated_user.email,  # unchanged field
                    'first_name': data['first_name'],  # changed field
                    'last_name': data['last_name'],  # changed field
                    'is_superuser': updated_user.is_superuser,  # unchanged field
                },
                response.data)

            # make sure the number of groups match
            self.assertEqual(len(response.data['groups']),
                             len(updated_user.groups.all()))

            # make sure avatar is uploaded on the correct link
            self.assertIn(
                'http://testserver/media/avatars/avatar',
                response.data['avatar'])

    def destroy_user_response_check_fn(
            self, user, response, query_args, *args, **kwargs):
        """
        Super user can destroy all users. Users can destroy themselves
        """

        if user.is_superuser:
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        else:
            if query_args['pk'] == user.id:  # a normal can see himself
                self.assertEqual(response.status_code, status.HTTP_200_OK)

            else:  # not found otherwise
                self.assertEqual(
                    response.status_code,
                    status.HTTP_404_NOT_FOUND)

    def setUp(self):
        """
        Sets up the test cases.
        """
        super().setUp()
        self.tests = [
            {
                'test_name': 'retrieve_user',
                'type': 'get',
                'path_name': 'app_users_retrieve_update_destroy',
                'request': [
                    {
                        'name': 'retrieve_user_{}'.format(user.username),
                        'query_args': {'pk': user.id},
                        'response_check_fn': self.retrieve_user_response_check_fn,
                    }  # generate requests for all users to retrieve all other users
                    for user in self.users.values()]
            },
            {
                'test_name': 'update_user',
                'type': 'put',
                'path_name': 'app_users_retrieve_update_destroy',
                'request': [
                    {
                        'name': 'update_user_{}'.format(user.username),
                        'data': lambda: {  # this regenerates new data every time
                            **generate_fake_data(user_factory.AppUserFactory),
                            'group': 'free_user'
                        },
                        'data_format': 'multipart',
                        'query_args': {'pk': user.id},
                        'response_check_fn': self.update_user_response_check_fn,
                    }  # generate requests for all users to update all other users
                    for user in self.users.values()]
            },
            {
                'test_name': 'destroy_user',
                'type': 'delete',
                'path_name': 'app_users_retrieve_update_destroy',
                'request': [
                    {
                        'name': 'destroy_user_{}'.format(user.username),
                        # undelete deleted user models
                        'post_test_cb': lambda: USER_MODEL.objects.deleted_only().undelete(),
                        'query_args': {'pk': user.id},
                        'response_check_fn': self.destroy_user_response_check_fn,
                    }  # generate requests for all users to delete all other users
                    for user in self.users.values()]
            },
        ]

    def test_(self):
        """
        The single test function that runs all the test cases defined in
        the self.test.
        """
        for test_config in self.tests:
            self.run_single_test(test_config, show_passed=False)
