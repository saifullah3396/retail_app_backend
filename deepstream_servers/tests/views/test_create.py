"""
Defines the unit tests related to 'create' api requests for this application.
"""
from django.urls import include, path
from django.utils import timezone
from rest_framework import status

from core.tests import TestsBase


# pylint: disable=pointless-string-statement, invalid-names, line-too-long
class DSCreateTests(TestsBase):
    """
    Defines unit tests for 'create' api requests for views defined at
    'deepstream_servers/' url.
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
        super(DSCreateTests, self).setUp()
        test_mac_addrs = [self.generate_random_mac_addr() for i in range(20)]
        self.test = [
            {
                'test_name': 'create_deepstream_servers',
                'type': 'post',
                'path_name': 'deepstream_servers_list_create_delete',
                'request': [
                    {   # create deepstream_server without any data, bad
                        'test_name': 'create_deepstream_server_by_staff_no_data',
                        'data': {},
                        'user': 'staff_user',
                        'status': status.HTTP_400_BAD_REQUEST,
                    },
                    {   # create deepstream_server, okay for staff but error since deepstream_server 0
                        # already exists in this block
                        'test_name': 'create_deepstream_server_by_staff_not_unique',
                        'data': {
                            'ip_addr': 'rtsp://192.168.1.1',
                            'mac_addr': self.deepstream_servers['ds0_b1_f0_l1_o1'].mac_addr,
                            # 'connected_at': test_connected_at,
                            # 'last_echo_at': test_last_echo_at,
                            'block': self.blocks['b1_f0_l1_o1'].id
                        },
                        'user': 'staff_user',
                        'status': status.HTTP_400_BAD_REQUEST,
                    },
                    {   # create a new unique deepstream_server, okay for staff
                        'test_name': 'create_deepstream_server_by_staff',
                        'data': {
                            'ip_addr': 'rtsp://192.168.1.1',
                            'mac_addr': test_mac_addrs[1],
                            'block': self.blocks['b1_f0_l1_o1'].id
                        },
                        'user': 'staff_user',
                        'status': status.HTTP_201_CREATED,
                        'response_check': lambda test, data: (
                            test.assertDictContainsSubset(
                                {
                                    'ip_addr': 'rtsp://192.168.1.1',
                                    'mac_addr': test_mac_addrs[1],
                                    'block': self.blocks['b1_f0_l1_o1'].id
                                }, data)
                        )
                    },
                    {   # create deepstream_server by org-admin, okay
                        'test_name': 'create_deepstream_server_org_admin_1_in_org_1',
                        'data': {
                            'ip_addr': 'rtsp://192.168.1.1',
                            'mac_addr': test_mac_addrs[2],
                            'block': self.blocks['b1_f0_l1_o1'].id
                        },
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_201_CREATED,
                        'response_check': lambda test, data: (
                            test.assertDictContainsSubset(
                                {
                                    'ip_addr': 'rtsp://192.168.1.1',
                                    'mac_addr': test_mac_addrs[2],
                                    'block': self.blocks['b1_f0_l1_o1'].id
                                }, data)
                        )
                    },
                    {   # create deepstream_server by org-admin in lower tree, okay
                        'test_name':
                            'create_deepstream_server_org_admin_1_in_sub_1_org_1',
                        'data': {
                            'ip_addr': 'rtsp://192.168.1.1',
                            'mac_addr': test_mac_addrs[3],
                            'block': self.blocks['b1_f0_l1_sub1_o1'].id
                        },
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_201_CREATED,
                        'response_check': lambda test, data: (
                            test.assertDictContainsSubset(
                                {
                                    'ip_addr': 'rtsp://192.168.1.1',
                                    'mac_addr': test_mac_addrs[3],
                                    'block': self.blocks['b1_f0_l1_sub1_o1'].id
                                }, data)
                        )
                    },
                    {   # create deepstream_server by org-admin in other organization,
                        # bad
                        'test_name': 'create_deepstream_server_org_admin_1_in_org_2',
                        'data': {
                            'ip_addr': 'rtsp://192.168.1.1',
                            'mac_addr': test_mac_addrs[4],
                            'block': self.blocks['b1_f0_l1_o2'].id
                        },
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_400_BAD_REQUEST
                    },
                    {   # create deepstream_server by sub-org-admin in upper tree, bad
                        'test_name': 'create_deepstream_server_sub_org_admin_1_in_org_1',
                        'data': {
                            'ip_addr': 'rtsp://192.168.1.1',
                            'mac_addr': test_mac_addrs[4],
                            'block': self.blocks['b1_f0_l1_o1'].id
                        },
                        'user': 'sub_org_11_admin_user',
                        'status': status.HTTP_400_BAD_REQUEST
                    },
                    {   # create deepstream_server by sub-org-admin in own tree, okay
                        'test_name':
                            'create_deepstream_server_sub_org_admin_1_in_sub_1_org_1',
                        'data': {
                            'ip_addr': 'rtsp://192.168.1.1',
                            'mac_addr': test_mac_addrs[5],
                            'block': self.blocks['b1_f0_l1_sub1_o1'].id
                        },
                        'user': 'sub_org_11_admin_user',
                        'status': status.HTTP_201_CREATED,
                        'response_check': lambda test, data: (
                            test.assertDictContainsSubset(
                                {
                                    'ip_addr': 'rtsp://192.168.1.1',
                                    'mac_addr': test_mac_addrs[5],
                                    'block': self.blocks['b1_f0_l1_sub1_o1'].id
                                }, data)
                        )
                    },
                    {   # create deepstream_server by employee user, forbidden
                        'test_name': 'create_deepstream_server_employee_user',
                        'data': {
                            'ip_addr': 'rtsp://192.168.1.1',
                            'mac_addr': test_mac_addrs[6],
                            'block': self.blocks['b1_f0_l1_sub1_o1'].id
                        },
                        'user': 'employee_user',
                        'status': status.HTTP_403_FORBIDDEN
                    },
                    {   # create deepstream_server by random user, forbidden
                        'test_name': 'create_deepstream_server_other_user',
                        'data': {
                            'ip_addr': 'rtsp://192.168.1.1',
                            'mac_addr': test_mac_addrs[6],
                            'block': self.blocks['b1_f0_l1_sub1_o1'].id
                        },
                        'user': 'other_user',
                        'status': status.HTTP_403_FORBIDDEN
                    },
                ]
            }
        ]

    def test_(self):
        """
        The single test function that runs all the test cases defined in
        the self.test.
        """
        for test_config in self.test:
            self.run_single_test(test_config)
