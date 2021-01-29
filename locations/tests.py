import copy
from django.urls import include, path, reverse
from rest_framework.authtoken.models import Token
from rest_framework import status
from backend.tests import TestsBase


class LocationTests(TestsBase):
    api_urlpatterns = [
        path('locations/', include('locations.api.urls')),
    ]

    urlpatterns = [
        path('api/v1/', include(api_urlpatterns)),
    ]

    paths_admin = [
        {
            'name': 'locations_admin',
            'args': None
        },
        {
            'name': 'locations_admin_detail',
            'args': [lambda parent: parent.locations['location_1_org_1'].id]
        },
        {
            'name': 'floors_admin',
            'args': None
        },
        {
            'name': 'floors_admin_detail',
            'args': [lambda parent: parent.floors['floor_0_location_1'].id, ]
        },
        {
            'name': 'blocks_admin',
            'args': None
        },
        {
            'name': 'blocks_admin_detail',
            'args': [lambda parent: parent.blocks['block_0_floor_0_location_1'].id]
        }]

    paths_user = [
        {
            'name': 'floors_user',
            'args': None
        },
        {
            'name': 'blocks_user',
            'args': None
        }]

    def get_unauth(self, path_name, args=None):
        """
        Ensure requesting locations from unauthorized users is forbidden
        """
        if args:
            get_url = reverse(path_name, args=args)
        else:
            get_url = reverse(path_name)
        self.get(
            get_url,
            None,
            self.tokens['other_user'],
            status.HTTP_403_FORBIDDEN)

    def get_auth(self, path_name, args=None, user_name='staff_user'):
        """
        Ensure requesting locations from unauthorized users is forbidden
        """
        if args:
            get_url = reverse(path_name, args=args)
        else:
            get_url = reverse(path_name)
        self.get(
            get_url,
            None,
            self.tokens[user_name],
            status.HTTP_200_OK)

    # def test_get_all_unauth(self):
    #     """
    #     Ensure requesting locations and sub_locations from unauthorized
    #     users is forbidden
    #     """
    #     for path in self.paths_admin:
    #         print('path', path['name'])
    #         if path['args'] is not None:
    #             args = [
    #                 arg(self) if callable(arg) else arg
    #                 for arg in path['args']]
    #             self.get_unauth(path['name'], args=args)
    #         else:
    #             self.get_unauth(path['name'])

    # def test_get_all_auth(self):
    #     """
    #     Ensure requesting locations and sub_locations from staff users
    #     is okay
    #     """
    #     for path in self.paths_admin:
    #         if path['args'] is not None:
    #             args = [
    #                 arg(self) if callable(arg) else arg
    #                 for arg in path['args']]
    #             self.get_auth(path['name'], args=args)
    #         else:
    #             self.get_auth(path['name'])

    def test_get_user_all_unauth(self):
        """
        Ensure requesting locations and sub_locations from unauthorized
        users is forbidden
        """
        for path in self.paths_user:
            if path['args'] is not None:
                args = [
                    arg(self) if callable(arg) else arg
                    for arg in path['args']]
                self.get_unauth(path['name'], args=args)
            else:
                self.get_unauth(path['name'])

    def test_get_user_all_auth(self):
        """
        Ensure requesting locations and sub_locations from staff users
        is okay
        """
        for path in self.paths_user:
            if path['args'] is not None:
                args = [
                    arg(self) if callable(arg) else arg
                    for arg in path['args']]
                self.get_auth(path['name'], args=args,
                              user_name='employee_user')
            else:
                self.get_auth(path['name'], user_name='employee_user')
