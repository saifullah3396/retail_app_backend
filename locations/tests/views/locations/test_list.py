"""
Defines the unit tests related to 'list' api requests for this application.
"""

from django.urls import include, path
from rest_framework import status

from core.tests import TestsBase


# pylint: disable=pointless-string-statement, line-too-long, invalid-name
class LocationListTests(TestsBase):
    """
    Defines unit tests for 'list' api requests for views defined
    at 'locations/' url.
    """

    """Define the api url patterns used in this test unit."""
    api_urlpatterns = [
        path('locations/', include('locations.api.urls')),
    ]

    """Define the the complete url pattern used in this test unit."""
    urlpatterns = [
        path('api/v1/', include(api_urlpatterns)),
    ]

    def setUp(self):
        """
        Sets up the test cases.
        """
        super(LocationListTests, self).setUp()
        self.test = [
            {
                'test_name': 'get_locations_list',
                'type': 'get',
                'path_name': 'locations_list_create_delete',
                'request': [
                    {   # get locations list by staff
                        'user': 'staff_user',
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                len(
                                    data.get('results', None)),
                                len(self.ls_dict))
                        )
                    },
                    {    # get locations list by org admin
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                len(data.get('results', None)),
                                len(self.ls_o1_dict) +
                                len(self.ls_sub1_o1_dict))
                        )
                    },
                    {   # get locations list by sub-org admin
                        'user': 'sub_org_11_admin_user',
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                len(data.get('results', None)),
                                len(self.ls_sub1_o1_dict))
                        )
                    },
                    {   # get locations list by another org admin
                        'user': 'org_2_admin_user',
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                len(data.get('results', None)),
                                len(self.ls_o2_dict) +
                                len(self.ls_sub1_o2_dict))
                        )
                    },
                    {   # get locations list by employee, okay
                        'user': 'employee_user',
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                len(data.get('results', None)),
                                len(self.users_dict['employee_user']
                                    ['authorized_locations']))
                        )
                    },
                    {   # get locations list by random user, forbidden
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
