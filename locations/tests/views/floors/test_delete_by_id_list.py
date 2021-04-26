"""
Defines the unit tests related to 'delete-by-id-list' api requests for this
application.
"""

from django.urls import include, path
from rest_framework import status

from core.tests import TestsBase


# pylint: disable=pointless-string-statement
class FloorDeleteByIdListTests(TestsBase):
    """
    Defines unit tests for 'delete-by-id-list' api requests for views defined
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
        super(FloorDeleteByIdListTests, self).setUp()
        self.test = [
            {
                'test_name': 'delete_multiple_floors',
                'type': 'delete',
                'path_name': 'floors_list_create_delete',
                'request': [
                    {   # delete floor, forbidden operation by staff
                        'test_name': 'delete_floor_by_staff',
                        'query_params': [
                            ('id', self.floors['f0_l1_sub1_o1'].id),
                        ],
                        'user': 'staff_user',
                        'status': status.HTTP_403_FORBIDDEN
                    },
                    {   # delete floor, forbidden operation for organization admin
                        'test_name': 'delete_floor_by_organization_admin',
                        'query_params': [
                            ('id', self.floors['f0_l1_sub1_o1'].id),
                        ],
                        'user': 'staff_user',
                        'status': status.HTTP_403_FORBIDDEN
                    },
                    {   # delete floor, forbidden operation for employee
                        'test_name': 'delete_floor_by_employee',
                        'query_params': [
                            ('id', self.floors['f0_l1_sub1_o1'].id),
                        ],
                        'user': 'staff_user',
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
