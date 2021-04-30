"""
Defines the unit tests related to 'list' api requests for this application.
"""

from django.urls import include, path
from rest_framework import status

from core.tests import TestsBase


# pylint: disable=pointless-string-statement, line-too-long, invalid-name
class FloorListTests(TestsBase):
    """
    Defines unit tests for 'list' api requests for views defined
    at 'locations/' url.
    """

    """Define the api url patterns used in this test unit."""
    api_urlpatterns = [
        path('locations/floors/', include('locations.api.urls')),
    ]

    """Define the the complete url pattern used in this test unit."""
    urlpatterns = [
        path('api/v1/', include(api_urlpatterns)),
    ]

    def setUp(self):
        """
        Sets up the test cases.
        """
        super(FloorListTests, self).setUp()
        self.test = [
            {
                'test_name': 'get_floors_list',
                'type': 'get',
                'path_name': 'floors_list_create_delete',
                'request': [
                    {   # get floors list by staff
                        'user': 'staff_user',
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                len(
                                    data.get('results', None)),
                                len(self.fs_dict))
                        )
                    },
                    {    # get floors list by org admin
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                len(data.get('results', None)),
                                len(self.fs_l1_o1_dict) +
                                len(self.fs_l1_sub1_o1_dict))
                        )
                    },
                    {   # get floors list by sub-org admin
                        'user': 'sub_org_11_admin_user',
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                len(data.get('results', None)),
                                len(self.fs_l1_sub1_o1_dict))
                        )
                    },
                    {   # get floors list by another org admin
                        'user': 'org_2_admin_user',
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                len(data.get('results', None)),
                                len(self.fs_l1_o2_dict) +
                                len(self.fs_l1_sub1_o2_dict))
                        )
                    },
                    {   # get floors list by employee, okay
                        'user': 'employee_user',
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                len(data.get('results', None)),
                                len(self.fs_l1_sub1_o1_dict)
                            )
                        )
                    },
                    {   # get floors list by random user, forbidden
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
