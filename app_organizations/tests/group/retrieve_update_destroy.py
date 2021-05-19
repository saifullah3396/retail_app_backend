"""
Defines the unit tests related to 'create' api requests for this application.
"""
# pylint: disable=line-too-long


from django.urls import include, path
from rest_framework import status

from core.tests.base import TestsBase
from core.tests.utils import generate_fake_data
from user_auth.models import DefaultUserGroups, UserGroup
from user_auth.tests.factories import group_factory
from users.tests.factories import user_factory

# get user model
GROUP_MODEL = UserGroup
NUM_TEST_USERS = 10


def generate_fake_group_data():
    """
    Wrapper for generate_dict_factory
    """
    data = generate_fake_data(group_factory.UserGroupFactory)
    data['authority'] = generate_fake_data(
        group_factory.UserGroupFactory)['authority']
    return data


class GroupsRetrieveUpdateDestroyTests(TestsBase):
    """
    Defines unit tests for 'retrieve/update/destroy' api requests for views
    defined at 'user_auth/groups/' url.

    Attributes:
        api_urlpatterns: Api url patterns used in this test unit.
        urlpatterns: Complete url pattern used in this test unit.
    """

    api_urlpatterns = [
        path('user_auth/groups/', include('user_auth.api.urls')),
    ]

    urlpatterns = [
        path('api/v1/', include(api_urlpatterns)),
    ]

    def generate_factory_data(self):
        """
        Generates factory data that can be used in test cases
        """
        self.groups = group_factory.generate_group_factory()
        self.users, self.tokens = user_factory.generate_user_factory(
            num_users=NUM_TEST_USERS)

    def retrieve_group_response_check_fn(
            self, user, response, query_args, *args, **kwargs):
        """
        Any user can get info about a particular group.
        """
        # if authority of user group is lower than requested group then it will
        # return a not found. Note authorities are calculated in reverse order
        if self.groups[query_args['name']].authority < user.highest_group.authority:
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        else:
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        # assert received data
        if response.status_code == status.HTTP_200_OK:
            updated_group = self.groups[query_args['name']]

            # make sure returned data is correct
            self.assertDictContainsSubset(
                {
                    'name': updated_group.name,
                    'authority': updated_group.authority
                },
                response.data)

    def update_group_response_check_fn(
            self, user, data, response, query_args, *args, **kwargs):
        """
        Super user can update all groups while normal users cannot.
        """

        if user.is_superuser:
            # make sure it returns a bad request if authority is < FREE_USER
            if data['authority'] < DefaultUserGroups.FREE_USER.value:
                self.assertEqual(
                    response.status_code, status.HTTP_400_BAD_REQUEST)
            else:
                # super user can updated every user
                self.assertEqual(response.status_code, status.HTTP_200_OK)
        else:
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        if response.status_code == status.HTTP_200_OK:
            # make sure group info is correct
            self.assertDictContainsSubset(data, response.data)

            # here we make the db is resetted back after update so that our
            # other tests are not affected
            group = GROUP_MODEL.objects.get(name=response.data['name'])
            group = self.groups[query_args['name']]
            group.save()

    def add_user_to_group_response_check_fn(
            self, user, data, response, query_args, *args, **kwargs):
        """
        Super user can update all groups while normal users cannot.
        """
        if user.is_superuser:
            # super user can updated every user
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        else:
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        if response.status_code == status.HTTP_200_OK:
            # make sure new user is added to group
            self.assertTrue(response.data['users'].count(str(data['user'])),
                            "User not added to group.")

    def remove_user_from_group_response_check_fn(
            self, user, data, response, query_args, *args, **kwargs):
        """
        Super user can update all groups while normal users cannot.
        """
        if user.is_superuser:
            # super user can updated every user
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        else:
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        if response.status_code == status.HTTP_200_OK:
            # make sure new user is removed from group
            self.assertFalse(response.data['users'].count(str(data['user'])))

    def destroy_group_response_check_fn(
            self, user, response, query_args, *args, **kwargs):
        """
        Super user can destroy all groups. Normal users cannot.
        """

        # here undeletion is not required since the users aren't allowed to
        # delete groups anyway. Also groups are not safedeleted
        if user.is_superuser:
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        else:
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def setUp(self):
        """
        Sets up the test cases.
        """
        super().setUp()
        user_to_add_remove = \
            user_factory.AppUserFactory.create(
                groups=(self.groups[DefaultUserGroups.FREE_USER.name],))
        self.tests = [
            {
                'test_name': 'retrieve_group',
                'type': 'get',
                'path_name': 'groups_retrieve_update_destroy',
                'request': [
                    {
                        'name': 'retrieve_group_{}'.format(group.name),
                        'query_args': {'name': group.name},
                        'response_check_fn': self.retrieve_group_response_check_fn,
                    }  # generate requests for all groups
                    for group in self.groups.values()]
            },
            {
                'test_name': 'update_group',
                'type': 'put',
                'path_name': 'groups_retrieve_update_destroy',
                'request': [
                    {
                        'name': 'update_group_{}'.format(group.name),
                        'data': lambda: generate_fake_group_data(),
                        'query_args': {'name': group.name},
                        'response_check_fn': self.update_group_response_check_fn,
                    }  # generate requests for all groups to update all other groups
                    for group in self.groups.values()]
            },
            {
                'test_name': 'add_user_to_group',
                'type': 'put',
                'path_name': 'groups_add_user',
                'request': [
                    {
                        'name': 'add_{}_to_group_{}'.format(
                            user_to_add_remove.username, group.name),
                        'data': lambda: {  # this regenerates new data every time
                            'user': user_to_add_remove.id,
                        },
                        'query_args': {'name': group.name},
                        'response_check_fn': self.add_user_to_group_response_check_fn,
                    }  # generate requests for all groups to update all other groups
                    for group in self.groups.values()]
            },
            {
                'test_name': 'remove_user_from_group',
                'type': 'put',
                'path_name': 'groups_remove_user',
                'request': [
                    {
                        'name': 'remove_{}_from_group_{}'.format(
                            user_to_add_remove.username, group.name),
                        'data': lambda: {  # this regenerates new data every time
                            'user': user_to_add_remove.id,
                        },
                        'query_args': {'name': group.name},
                        'response_check_fn': self.remove_user_from_group_response_check_fn,
                    }  # generate requests for all groups to update all other groups
                    for group in self.groups.values()]
            },
            {
                'test_name': 'destroy_group',
                'type': 'delete',
                'path_name': 'groups_retrieve_update_destroy',
                'request': [
                    {
                        'name': 'destroy_group_{}'.format(group.name),
                        'query_args': {'name': group.name},
                        # reset deletion for every item before performing test
                        'post_test_cb': lambda: GROUP_MODEL.objects.deleted_only().undelete(),
                        'response_check_fn': self.destroy_group_response_check_fn,
                    }  # generate requests for all users to delete the groups
                    for group in self.groups.values()]
            },
        ]

    def test_(self):
        """
        The single test function that runs all the test cases defined in
        the self.test.
        """
        for test_config in self.tests:
            self.run_single_test(test_config, show_passed=False)
