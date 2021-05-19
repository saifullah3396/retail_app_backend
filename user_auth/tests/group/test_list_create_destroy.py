"""
Defines the unit tests related to 'create' api requests for this application.
"""
# pylint: disable=line-too-long


from django.contrib.auth.models import Permission
from django.urls import include, path
from rest_framework import status

from backend import urls
from core.tests.base import TestsBase
from core.tests.utils import generate_fake_data
from user_auth.models import DefaultUserGroups, UserGroup
from user_auth.tests.factories import group_factory
from users.models import AppUser
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


class GroupsListCreateDestroyTests(TestsBase):
    """
    Defines unit tests for 'list/create/destroy' api requests for views
    defined at 'user_auth/groups/' url.

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
        self.users, self.tokens = user_factory.generate_user_factory(
            num_users=NUM_TEST_USERS)

    def list_groups_response_check_fn(self, user, response, *args, **kwargs):
        """
        Super user can see all groups while normal users only themselves.
        """
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        if user.is_superuser:
            self.assertEqual(
                len(response.data['results']), len(GROUP_MODEL.objects.all()))
        else:
            groups = GROUP_MODEL.objects.filter(
                authority__gte=user.highest_group.authority)
            self.assertEqual(
                len(response.data['results']), len(groups))

    def generate_data_for_id_list_groups(self):
        """
        Generates a list of groups which can be used for get list request
        """
        id_list = []

        # generate some groups that would be listed
        id_list.extend(
            group_factory.UserGroupFactory.create_batch(5))

        return [('name', group.name) for group in id_list]

    def id_list_groups_response_check_fn(self, user, response, query_params, *args, **kwargs):
        """
        Groups can be id listed by any user
        """
        # if there is any group in the list whose authority is higher than user
        # this will return a bad request
        bad_request = False
        for query in query_params:
            if GROUP_MODEL.objects.get(name=query[1]).authority < user.highest_group.authority:
                bad_request = True

        if bad_request:
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        else:
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(
                len(response.data['results']), len(query_params))

    def create_group_response_check_fn(self, user, response, data, *args, **kwargs):
        """
        Create can be called by super user only
        """
        if user.is_superuser:
            if data['authority'] >= DefaultUserGroups.FREE_USER.value:
                self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        else:
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        if response.status_code == status.HTTP_201_CREATED:
            # make sure returned data is correct
            self.assertDictContainsSubset(
                {
                    'name': data['name'],
                    'authority': data['authority']
                },
                response.data)

    def list_destroy_groups_response_check_fn(self, response, *args, **kwargs):
        """
        Any user cannot delete all groups in obtained list.
        """
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def generate_data_for_id_list_destroy_groups(self):
        """
        Generates a list of users which can then be deleted
        """
        to_be_del_list = []

        # generate some groups that would be deleted
        to_be_del_list.extend(
            group_factory.UserGroupFactory.create_batch(5))

        return [('name', group.name) for group in to_be_del_list]

    def id_list_destroy_groups_response_check_fn(self, user, response, *args, **kwargs):
        """
        Groups can be delete with ids list as input only by staff
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
                'test_name': 'create_group',
                'type': 'post',
                'path_name': 'groups_list_create_destroy',
                'request': [
                    {
                        'name': 'create_group_random_data',
                        'data': lambda: generate_fake_group_data(),
                        'response_check_fn':
                            self.create_group_response_check_fn
                    },
                ]
            },
            {
                'test_name': 'list_groups',
                'type': 'get',
                'path_name': 'groups_list_create_destroy',
                'request': [
                    {
                        'name': 'list_groups',
                        'response_check_fn': self.list_groups_response_check_fn,
                    },
                ]
            },
            {
                'test_name': 'id_list_groups',
                'type': 'get',
                'path_name': 'groups_list_create_destroy',
                'request': [
                    {
                        'name': 'id_list_groups',
                        'query_params': self.generate_data_for_id_list_groups(),
                        'response_check_fn': self.id_list_groups_response_check_fn,
                    }
                ]
            },
            {
                'test_name': 'list_destroy_groups',
                'type': 'delete',
                'path_name': 'groups_list_create_destroy',
                'request': [
                    {
                        'name': 'list_destroy_groups',
                        'response_check_fn': self.list_destroy_groups_response_check_fn,
                    },
                ]
            },
            {
                'test_name': 'id_list_destroy_groups',
                'type': 'delete',
                'path_name': 'groups_list_create_destroy',
                'request': [
                    {
                        'name': 'id_list_destroy_groups',
                        'query_params': self.generate_data_for_id_list_destroy_groups(),
                        'response_check_fn': self.id_list_destroy_groups_response_check_fn,
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
