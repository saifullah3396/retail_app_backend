"""
Defines the unit tests related to 'retrieve' api requests for this application.
"""

import datetime

from django.urls import include, path
from rest_framework import status

from core.tests import TestsBase
from deepstream_servers.models import DeepstreamServer


# pylint: disable=pointless-string-statement, invalid-names, line-too-long
class DSRetrieveTests(TestsBase):
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
        super(DSRetrieveTests, self).setUp()

        def django_datetime_to_drf_format(x):
            return str(x).split('+')[0]+'+0000'

        self.test = [
            {
                'test_name': 'get_deepstream_server_by_id',
                'type': 'get',
                'path_name': 'deepstream_servers_retrieve_update_delete',
                'request': [
                    {   # get deepstream_server by id, okay for staff
                        'test_name': 'get_ds0_b1_f0_l1_o1_by_staff',
                        'args': {'pk': self.deepstream_servers['ds0_b1_f0_l1_o1'].id},
                        'user': 'staff_user',
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertDictContainsSubset(
                                {
                                    'id': str(self.deepstream_servers['ds0_b1_f0_l1_o1'].id),
                                    'ip_addr': 'rtsp://192.168.1.1',
                                    'mac_addr': self.deepstream_servers['ds0_b1_f0_l1_o1'].mac_addr,
                                    # just a fix for annoying time format difference
                                    'connected_at': django_datetime_to_drf_format(
                                        self.deepstream_servers['ds0_b1_f0_l1_o1'].connected_at),
                                    'last_echo_at': django_datetime_to_drf_format(
                                        self.deepstream_servers['ds0_b1_f0_l1_o1'].last_echo_at),
                                    'status': DeepstreamServer.OFFLINE,
                                    'block': self.blocks['b1_f0_l1_o1'].id
                                }, data)
                        )
                    },
                    {   # get deepstream_server by id, okay for org admin itself
                        'test_name': 'get_ds0_b1_f0_l1_o1_by_org_1_admin',
                        'args': {'pk': self.deepstream_servers['ds0_b1_f0_l1_o1'].id},
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertDictContainsSubset(
                                {
                                    'id': str(self.deepstream_servers['ds0_b1_f0_l1_o1'].id),
                                    'ip_addr': 'rtsp://192.168.1.1',
                                    'mac_addr': self.deepstream_servers['ds0_b1_f0_l1_o1'].mac_addr,
                                    # just a fix for annoying time format difference
                                    'connected_at': django_datetime_to_drf_format(
                                        self.deepstream_servers['ds0_b1_f0_l1_o1'].connected_at),
                                    'last_echo_at': django_datetime_to_drf_format(
                                        self.deepstream_servers['ds0_b1_f0_l1_o1'].last_echo_at),
                                    'status': DeepstreamServer.OFFLINE,
                                    'block': self.blocks['b1_f0_l1_o1'].id
                                }, data)
                        )
                    },
                    {   # get deepstream_server of org, forbidden for sub-org admin
                        'test_name': 'get_ds0_b1_f0_l1_o1_by_sub_org_1_admin',
                        'args': {'pk': self.deepstream_servers['ds0_b1_f0_l1_o1'].id},
                        'user': 'sub_org_11_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # get deepstream_server, bad for other org-admin
                        'test_name': 'get_ds0_b1_f0_l1_o1_by_org_2_admin',
                        'args': {'pk': self.deepstream_servers['ds0_b1_f0_l1_o1'].id},
                        'user': 'org_2_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # get deepstream_server by id, forbidden for random user
                        'test_name': 'get_ds0_b1_f0_l1_o1_by_other_user',
                        'args': {'pk': self.deepstream_servers['ds0_b1_f0_l1_o1'].id},
                        'user': 'other_user',
                        'status': status.HTTP_403_FORBIDDEN
                    },
                ]
            },
            {
                'test_name': 'get_sub_deepstream_server_by_id',
                'type': 'get',
                'path_name': 'deepstream_servers_retrieve_update_delete',
                'request': [
                    {   # get sub-org deepstream_server by id, okay for staff
                        'test_name': 'get_ds0_b1_f0_l1_sub1_o1_by_staff',
                        'args': {'pk': self.deepstream_servers['ds0_b1_f0_l1_sub1_o1'].id},
                        'user': 'staff_user',
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertDictContainsSubset(
                                {
                                    'id': str(self.deepstream_servers['ds0_b1_f0_l1_sub1_o1'].id),
                                    'ip_addr': 'rtsp://192.168.1.1',
                                    'mac_addr': self.deepstream_servers['ds0_b1_f0_l1_sub1_o1'].mac_addr,
                                    # just a fix for annoying time format difference
                                    'connected_at': django_datetime_to_drf_format(
                                        self.deepstream_servers['ds0_b1_f0_l1_sub1_o1'].connected_at),
                                    'last_echo_at': django_datetime_to_drf_format(
                                        self.deepstream_servers['ds0_b1_f0_l1_sub1_o1'].last_echo_at),
                                    'status': DeepstreamServer.OFFLINE,
                                    'block': self.blocks['b1_f0_l1_sub1_o1'].id
                                }, data)
                        )
                    },
                    {   # get sub-org deepstream_server by id, okay for org admin itself
                        # under which this sub-org exists
                        'test_name':
                            'get_ds0_b1_f0_l1_sub1_o1_by_org_1_admin',
                        'args': {'pk': self.deepstream_servers['ds0_b1_f0_l1_sub1_o1'].id},
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertDictContainsSubset(
                                {
                                    'id': str(self.deepstream_servers['ds0_b1_f0_l1_sub1_o1'].id),
                                    'ip_addr': 'rtsp://192.168.1.1',
                                    'mac_addr': self.deepstream_servers['ds0_b1_f0_l1_sub1_o1'].mac_addr,
                                    # just a fix for annoying time format difference
                                    'connected_at': django_datetime_to_drf_format(
                                        self.deepstream_servers['ds0_b1_f0_l1_sub1_o1'].connected_at),
                                    'last_echo_at': django_datetime_to_drf_format(
                                        self.deepstream_servers['ds0_b1_f0_l1_sub1_o1'].last_echo_at),
                                    'status': DeepstreamServer.OFFLINE,
                                    'block': self.blocks['b1_f0_l1_sub1_o1'].id
                                }, data)
                        )
                    },
                    {   # get sub-org deepstream_server by id, okay for sub-org admin
                        # itself
                        'test_name':
                            'get_ds0_b1_f0_l1_sub1_o1_by_sub_1_org_1_admin',
                        'args': {'pk': self.deepstream_servers['ds0_b1_f0_l1_sub1_o1'].id},
                        'user': 'sub_org_11_admin_user',
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertDictContainsSubset(
                                {
                                    'id': str(self.deepstream_servers['ds0_b1_f0_l1_sub1_o1'].id),
                                    'ip_addr': 'rtsp://192.168.1.1',
                                    'mac_addr': self.deepstream_servers['ds0_b1_f0_l1_sub1_o1'].mac_addr,
                                    # just a fix for annoying time format difference
                                    'connected_at': django_datetime_to_drf_format(
                                        self.deepstream_servers['ds0_b1_f0_l1_sub1_o1'].connected_at),
                                    'last_echo_at': django_datetime_to_drf_format(
                                        self.deepstream_servers['ds0_b1_f0_l1_sub1_o1'].last_echo_at),
                                    'status': DeepstreamServer.OFFLINE,
                                    'block': self.blocks['b1_f0_l1_sub1_o1'].id
                                }, data)
                        )
                    },
                    {   # get sub-org deepstream_server by id, bad for other
                        # org-admin under which this sub-org does not exist
                        'test_name':
                            'get_ds0_b1_f0_l1_sub1_o1_by_org_2_admin',
                        'args': {'pk': self.deepstream_servers['ds0_b1_f0_l1_sub1_o1'].id},
                        'user': 'org_2_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # get sub-org deepstream_server by id, bad for other
                        # sub-org admin to which this sub-org does not exist
                        'test_name':
                            'get_ds0_b1_f0_l1_sub1_o1_by_sub_1_org_2_admin',
                        'args': {'pk': self.deepstream_servers['ds0_b1_f0_l1_sub1_o1'].id},
                        'user': 'sub_org_12_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # get sub-org deepstream_server by id, okay for staff who is in
                        # this org
                        'test_name': 'get_ds0_b1_f0_l1_sub1_o1_by_employee',
                        'args': {'pk': self.deepstream_servers['ds0_b1_f0_l1_sub1_o1'].id},
                        'user': 'employee_user',
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertDictContainsSubset(
                                {
                                    'id': str(self.deepstream_servers['ds0_b1_f0_l1_sub1_o1'].id),
                                    'ip_addr': 'rtsp://192.168.1.1',
                                    'mac_addr': self.deepstream_servers['ds0_b1_f0_l1_sub1_o1'].mac_addr,
                                    # just a fix for annoying time format difference
                                    'connected_at': django_datetime_to_drf_format(
                                        self.deepstream_servers['ds0_b1_f0_l1_sub1_o1'].connected_at),
                                    'last_echo_at': django_datetime_to_drf_format(
                                        self.deepstream_servers['ds0_b1_f0_l1_sub1_o1'].last_echo_at),
                                    'status': DeepstreamServer.OFFLINE,
                                    'block': self.blocks['b1_f0_l1_sub1_o1'].id
                                }, data)
                        )
                    },
                    {   # get sub-org by id, forbidden for random user
                        'test_name': 'get_ds0_b1_f0_l1_o2_by_other_user',
                        'args': {'pk': self.deepstream_servers['ds0_b1_f0_l1_o2'].id},
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
