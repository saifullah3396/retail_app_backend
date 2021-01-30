import copy
from django.urls import include, path, reverse
from rest_framework.authtoken.models import Token
from rest_framework import status
from common.tests import TestsBase


class UserApiTests(TestsBase):
    api_urlpatterns = [
        path('users/', include('users.api.urls')),
    ]

    urlpatterns = [
        path('api/v1/', include(api_urlpatterns)),
    ]

    get_paths_admin = [
        {
            'name': 'app_user_list_admin_access',
            'args': None
        },
    ]

    get_cfg_app_admin = [
        {
            'path_name': 'app_user_list_app_admin_access',
            'args': None,
            'request_user': 'org_1_admin_user',
            'status_code': status.HTTP_200_OK
        },
        {
            'path_name': 'app_user_detail_app_admin_access',
            'args': ['current'],
            'request_user': 'org_1_admin_user',
            'status_code': status.HTTP_200_OK
        },
        {
            'path_name': 'app_user_detail_app_admin_access',
            'args': [lambda parent: parent.users['org_1_admin_user'].id],
            'request_user': 'org_1_admin_user',
            'status_code': status.HTTP_200_OK
        },
        {
            'path_name': 'app_user_detail_app_admin_access',
            'args': [lambda parent: parent.users['org_2_admin_user'].id],
            'request_user': 'org_1_admin_user',
            'status_code': status.HTTP_403_FORBIDDEN
        },
        {
            'path_name': 'app_user_detail_app_admin_access',
            'args': [lambda parent: parent.users['sub_org_11_admin_user'].id],
            'request_user': 'org_1_admin_user',
            'status_code': status.HTTP_200_OK
        },
        {
            'path_name': 'app_user_detail_app_admin_access',
            'args': [lambda parent: parent.users['sub_org_12_admin_user'].id],
            'request_user': 'org_1_admin_user',
            'status_code': status.HTTP_200_OK
        },
        {
            'path_name': 'app_user_detail_app_admin_access',
            'args': [lambda parent: parent.users['employee_user'].id],
            'request_user': 'org_1_admin_user',
            'status_code': status.HTTP_200_OK
        },
        {
            'path_name': 'app_user_detail_app_admin_access',
            'args': [lambda parent: parent.users['employee_user'].id],
            'request_user': 'org_2_admin_user',
            'status_code': status.HTTP_403_FORBIDDEN
        },
        {
            'path_name': 'app_user_detail_app_admin_access',
            'args': [lambda parent: parent.users['sub_org_11_admin_user'].id],
            'request_user': 'sub_org_12_admin_user',
            'status_code': status.HTTP_403_FORBIDDEN
        }]

    def get_unauth(self, path_name, args=None, user_name='other_user'):
        """
        Ensure requesting organizations from unauthorized users is forbidden
        """
        if args:
            get_url = reverse(path_name, args=args)
        else:
            get_url = reverse(path_name)
        self.get(
            get_url,
            None,
            self.tokens[user_name],
            status.HTTP_403_FORBIDDEN)

    def get_auth(self, path_name, args=None, user_name='staff_user'):
        """
        Ensure requesting organizations from unauthorized users is forbidden
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

    def test_get_all_unauth(self):
        """
        Ensure requesting organizations and sub_organizations from unauthorized
        users is forbidden
        """
        for path in self.get_paths_admin:
            if path['args'] is not None:
                args = [
                    arg(self) if callable(arg) else arg for arg in path['args']]
                self.get_unauth(path['name'], args=args)
            else:
                self.get_unauth(path['name'])

    def test_get_all_auth(self):
        """
        Ensure requesting organizations and sub_organizations from staff users
        is okay
        """
        for path in self.get_paths_admin:
            if path['args'] is not None:
                args = [
                    arg(self) if callable(arg) else arg for arg in path['args']]
                self.get_auth(path['name'], args=args)
            else:
                self.get_auth(path['name'])

    def test_get_cfg_app_admin(self):
        """
        Perform all tests as given in get config
        """
        for cfg in self.get_cfg_app_admin:
            path_name = cfg['path_name']
            if cfg['args'] is not None:
                args = [
                    arg(self) if callable(arg) else arg for arg in cfg['args']]
                get_url = reverse(path_name, args=args)
            else:
                get_url = reverse(path_name)

            self.get(
                get_url,
                None,
                self.tokens[cfg['request_user']],
                cfg['status_code'])
