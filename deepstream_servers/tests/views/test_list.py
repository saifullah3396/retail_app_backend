"""
Defines the unit tests related to 'list' api requests for this application.
"""

from django.urls import include, path
from rest_framework import status

from core.tests import TestsBase


# pylint: disable=pointless-string-statement, invalid-names, line-too-long
class DSListTests(TestsBase):
    """
    Defines unit tests for 'list' api requests for views defined
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
        super(DSListTests, self).setUp()
        self.test = [
            {
                'test_name': 'get_deepstream_servers_list',
                'type': 'get',
                'path_name': 'deepstream_servers_list_create_delete',
                'request': [
                    {   # get deepstream_servers list by staff
                        'test_name': 'get_deepstream_servers_list_by_staff',
                        'args': None,
                        'user': 'staff_user',
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                len(
                                    data.get('results', None)),
                                len(self.ds_dict))
                        )
                    },
                    {    # get deepstream_servers list by org admin
                        'test_name': 'get_deepstream_servers_list_by_org1_admin',
                        'args': None,
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                len(data.get('results', None)),
                                len(self.ds_o1_dict) +
                                len(self.ds_sub1_o1_dict))
                        )
                    },
                    {   # get deepstream_servers list by sub-org admin
                        'test_name': 'get_deepstream_servers_list_by_sub1_org1_admin',
                        'args': None,
                        'user': 'sub_org_11_admin_user',
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                len(data.get('results', None)),
                                len(self.ds_sub1_o1_dict))
                        )
                    },
                    {   # get deepstream_servers list by another org admin
                        'test_name': 'get_deepstream_servers_list_by_org2_admin',
                        'args': None,
                        'user': 'org_2_admin_user',
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                len(data.get('results', None)),
                                len(self.ds_o2_dict) +
                                len(self.ds_sub1_o2_dict))
                        )
                    },
                    {   # get deepstream_servers list by employee, okay
                        'test_name': 'get_deepstream_servers_list_by_employee',
                        'args': None,
                        'user': 'employee_user',
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                len(data.get('results', None)),
                                len(self.ds_sub1_o1_dict)
                            )
                        )
                    },
                    {   # get deepstream_servers list by random user, forbidden
                        'test_name': 'get_deepstream_servers_list_by_other_user',
                        'args': None,
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
