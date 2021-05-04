"""
Defines the unit tests related to 'retrieve' api requests for this application.
"""

from django.urls import include, path
from django.utils import timezone
from rest_framework import status

from core.tests import TestsBase
from deepstream_servers.models import DeepstreamServer


# pylint: disable=pointless-string-statement, invalid-names, line-too-long
class DSUpdateTests(TestsBase):
    """
    Defines unit tests for 'retrieve' api requests for views defined
    at 'locations/' url.
    """

    """Define the api url patterns used in this test unit."""
    api_urlpatterns = [
        path('deepstream_servers/', include('deepstream_servers.api.urls')),
    ]

    """Define the the complete url pattern used in this test unit."""
    urlpatterns = [
        path('api/v1/', include(api_urlpatterns)),
    ]

    def setUp(self):
        """
        Sets up the test cases.
        """
        super(DSUpdateTests, self).setUp()
        test_mac_addrs = [self.generate_random_mac_addr() for i in range(20)]
        test_connected_at = timezone.now()
        test_last_echo_at = timezone.now()
        self.test = [
            {
                'test_name': 'update_deepstream_server_by_id',
                'type': 'patch',
                'path_name': 'deepstream_servers_retrieve_update_delete',
                'request': [
                    {   # update deepstream_server by id. change addr to an existing
                        # deepstream_server name inside the floor, bad
                        'test_name': 'rename_ds0',
                        'args': {'pk': self.deepstream_servers['ds0_o1'].id},
                        'user': 'staff_user',
                        'data': {
                            # check uniqueness
                            'mac_addr': self.deepstream_servers['ds1_o1'].mac_addr
                        },
                        'status': status.HTTP_400_BAD_REQUEST,
                    },
                    {   # update deepstream_server by id. change org to another org,
                        # okay
                        'test_name': 'change_ds0_org',
                        'args': {'pk': self.deepstream_servers['ds0_o1'].id},
                        'user': 'staff_user',
                        'data': {
                            'organization': self.orgs['o1'].id
                        },
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertDictContainsSubset(
                                {
                                    'organization': self.orgs['o1'].id
                                }, data)
                        )
                    },
                    {   # update deepstream_server by id, okay for staff
                        'test_name': 'update_ds0_o1_by_staff',
                        'args': {'pk': self.deepstream_servers['ds0_o1'].id},
                        'user': 'staff_user',
                        'data': {
                            'mac_addr': test_mac_addrs[0],
                            'organization': self.orgs['o1'].id
                        },
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertDictContainsSubset(
                                {
                                    'mac_addr': test_mac_addrs[0],
                                    'organization': self.orgs['o1'].id
                                }, data)
                        )
                    },
                    {   # update deepstream_server by id, okay for org_1_admin
                        'test_name': 'update_ds0_o1_by_org_1_admin',
                        'args': {'pk': self.deepstream_servers['ds0_o1'].id},
                        'user': 'org_1_admin_user',
                        'data': {
                            'mac_addr': test_mac_addrs[1],
                            'organization': self.orgs['o1'].id
                        },
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertDictContainsSubset(
                                {
                                    'mac_addr': test_mac_addrs[1],
                                    'organization': self.orgs['o1'].id
                                }, data)
                        )
                    },
                    {   # update non-available fields, bad
                        'test_name': 'update_non_fields_1_ds0_o1',
                        'args': {'pk': self.deepstream_servers['ds0_o1'].id},
                        'user': 'org_1_admin_user',
                        'data': {
                            'status': DeepstreamServer.ONLINE
                        },
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertTrue(
                                self.deepstream_servers['ds0_o1'].status !=
                                DeepstreamServer.ONLINE)
                        )
                    },
                    {   # update non-available fields, bad
                        'test_name': 'update_non_fields_2_ds0_o1',
                        'args': {'pk': self.deepstream_servers['ds0_o1'].id},
                        'user': 'org_1_admin_user',
                        'data': {
                            'connected_at': test_connected_at
                        },
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertTrue(
                                str(self.deepstream_servers['ds0_o1'].connected_at) !=
                                str(test_connected_at))
                        )
                    },
                    {   # update non-available fields, bad
                        'test_name': 'update_non_fields_3_ds0_o1',
                        'args': {'pk': self.deepstream_servers['ds0_o1'].id},
                        'user': 'org_1_admin_user',
                        'data': {
                            'last_echo_at': test_last_echo_at
                        },
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertTrue(
                                str(self.deepstream_servers['ds0_o1'].last_echo_at) !=
                                str(test_last_echo_at))
                        )
                    },
                    {   # update deepstream_server of org, forbidden for sub-org admin
                        'test_name': 'update_ds0_o1_by_sub_org_1_admin',
                        'args': {'pk': self.deepstream_servers['ds0_o1'].id},
                        'user': 'sub_org_11_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # update deepstream_server, bad for other org-admin
                        'test_name': 'update_ds0_o1_by_org_2_admin',
                        'args': {'pk': self.deepstream_servers['ds0_o1'].id},
                        'user': 'org_2_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # update deepstream_server by id, forbidden for random user
                        'test_name': 'update_ds0_o1_by_other_user',
                        'args': {'pk': self.deepstream_servers['ds0_o1'].id},
                        'user': 'other_user',
                        'status': status.HTTP_403_FORBIDDEN
                    },
                ]
            },
            {
                'test_name': 'update_sub_deepstream_server_by_id',
                'type': 'patch',
                'path_name': 'deepstream_servers_retrieve_update_delete',
                'request': [
                    {   # update sub-org deepstream_server by id, okay for staff
                        'test_name': 'update_ds0_sub1_o1_by_staff',
                        'args': {'pk': self.deepstream_servers['ds0_sub1_o1'].id},
                        'user': 'staff_user',
                        'data': {
                            'mac_addr': test_mac_addrs[3],
                            'organization': self.orgs['o1'].id
                        },
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertDictContainsSubset(
                                {
                                    'mac_addr': test_mac_addrs[3],
                                    'organization': self.orgs['o1'].id
                                }, data)
                        )
                    },
                    {   # update sub-org deepstream_server by id, okay for org admin itself
                        # under which this sub-org exists
                        'test_name':
                            'update_ds0_sub1_o1_by_org_1_admin',
                        'args': {'pk': self.deepstream_servers['ds0_sub1_o1'].id},
                        'user': 'org_1_admin_user',
                        'data': {
                            'mac_addr': test_mac_addrs[4],
                            'organization': self.orgs['sub1_o1'].id
                        },
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertDictContainsSubset(
                                {
                                    'mac_addr': test_mac_addrs[4],
                                    'organization': self.orgs['sub1_o1'].id
                                }, data)
                        )
                    },
                    {   # update sub-org deepstream_server by id, okay for sub-org admin
                        # itself
                        'test_name':
                            'update_ds0_sub1_o1_by_sub_1_org_1_admin',
                        'args': {'pk': self.deepstream_servers['ds0_sub1_o1'].id},
                        'user': 'sub_org_11_admin_user',
                        'data': {
                            'mac_addr': test_mac_addrs[5],
                            'organization': self.orgs['sub1_o1'].id
                        },
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertDictContainsSubset(
                                {
                                    'mac_addr': test_mac_addrs[5],
                                    'organization': self.orgs['sub1_o1'].id
                                }, data)
                        )
                    },
                    {   # update sub-org deepstream_server by id, send unauth org id
                        'test_name':
                            'update_ds0_sub1_o1_by_sub_1_org_1_admin_bad_org',
                        'args': {'pk': self.deepstream_servers['ds0_sub1_o1'].id},
                        'user': 'sub_org_11_admin_user',
                        'data': {
                            'mac_addr': test_mac_addrs[5],
                            'organization': self.orgs['o1'].id
                        },
                        'status': status.HTTP_400_BAD_REQUEST
                    },
                    {   # update sub-org deepstream_server by id, bad for other
                        # org-admin under which this sub-org does not exist
                        'test_name':
                            'update_ds0_sub1_o1_by_org_2_admin',
                        'args': {'pk': self.deepstream_servers['ds0_sub1_o1'].id},
                        'data': {
                            'mac_addr': test_mac_addrs[6],
                            'organization': self.orgs['o1'].id
                        },
                        'user': 'org_2_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # update sub-org deepstream_server by id, bad for other
                        # sub-org admin to which this sub-org does not exist
                        'test_name':
                            'update_ds0_sub1_o1_by_sub_1_org_2_admin',
                        'args': {'pk': self.deepstream_servers['ds0_sub1_o1'].id},
                        'data': {
                            'mac_addr': test_mac_addrs[7],
                            'organization': self.orgs['o1'].id
                        },
                        'user': 'sub_org_12_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # update sub-org deepstream_server by id, forbidden for employees
                        'test_name': 'update_ds0_sub1_o1_by_employee',
                        'args': {'pk': self.deepstream_servers['ds0_sub1_o1'].id},
                        'user': 'employee_user',
                        'data': {
                            'mac_addr': test_mac_addrs[8],
                            'organization': self.orgs['o1'].id
                        },
                        'status': status.HTTP_403_FORBIDDEN,
                    },
                    {   # update sub-org by id, forbidden for random user
                        'test_name': 'update_ds0_o1_by_other_user',
                        'args': {'pk': self.deepstream_servers['ds0_o1'].id},
                        'user': 'other_user',
                        'status': status.HTTP_403_FORBIDDEN
                    }
                ]
            }
        ]

    def test_(self):
        """
        The single test function that runs all the test cases defined in
        the self.test_sets.
        """
        for test_config in self.test:
            self.run_single_test(test_config)
