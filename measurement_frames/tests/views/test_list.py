"""
Defines the unit tests related to 'list' api requests for this application.
"""

from django.urls import include, path
from rest_framework import status

from core.tests import TestsBase


# pylint: disable=pointless-string-statement
class BlockListTests(TestsBase):
    """
    Defines unit tests for 'list' api requests for views defined
    at 'locations/' url.
    """

    """Define the api url patterns used in this test unit."""
    api_urlpatterns = [
        path('locations/blocks/', include('locations.api.urls')),
    ]

    """Define the the complete url pattern used in this test unit."""
    urlpatterns = [
        path('api/v1/', include(api_urlpatterns)),
    ]

    def setUp(self):
        """
        Sets up the test cases.
        """
        super(BlockListTests, self).setUp()
        self.test = [
            {
                'test_name': 'get_blocks_list',
                'type': 'get',
                'path_name': 'blocks_list_create_delete',
                'request': [
                    {   # get blocks list by staff
                        'test_name': 'get_blocks_list_by_staff',
                        'args': None,
                        'user': 'staff_user',
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                len(
                                    data.get('results', None)),
                                len(self.bs_names))
                        )
                    },
                    {    # get blocks list by org admin
                        'test_name': 'get_blocks_list_by_org1_admin',
                        'args': None,
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                len(data.get('results', None)),
                                len(self.bs_f0_l1_o1_names) +
                                len(self.bs_f1_l1_o1_names) +
                                len(self.bs_f0_l1_sub1_o1_names))
                        )
                    },
                    {   # get blocks list by sub-org admin
                        'test_name': 'get_blocks_list_by_sub1_org1_admin',
                        'args': None,
                        'user': 'sub_org_11_admin_user',
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                len(data.get('results', None)),
                                len(self.bs_f0_l1_sub1_o1_names))
                        )
                    },
                    {   # get blocks list by another org admin
                        'test_name': 'get_blocks_list_by_org2_admin',
                        'args': None,
                        'user': 'org_2_admin_user',
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                len(data.get('results', None)),
                                len(self.bs_f0_l1_o2_names) +
                                len(self.bs_f0_l1_sub1_o2_names))
                        )
                    },
                    {   # get blocks list by employee, okay
                        'test_name': 'get_blocks_list_by_employee',
                        'args': None,
                        'user': 'employee_user',
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                len(data.get('results', None)),
                                len(self.bs_f0_l1_sub1_o1_names)
                            )
                        )
                    },
                    {   # get blocks list by random user, forbidden
                        'test_name': 'get_blocks_list_by_other_user',
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
