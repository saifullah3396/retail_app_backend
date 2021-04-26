"""
Defines the unit tests related to 'update' api requests for this application.
"""

from django.urls import include, path
from rest_framework import status

from core.tests import TestsBase


# pylint: disable=pointless-string-statement
class FloorUpdateTests(TestsBase):
    """
    Defines unit tests for 'update' api requests for views defined
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
        super(FloorUpdateTests, self).setUp()
        self.test = [
            {
                'test_name': 'update_floor_by_id',
                'type': 'patch',
                'path_name': 'floors_retrieve_update_delete',
                'request': [
                    {
                        # update f0_l1_sub1_o1 by staff, not
                        # permissable
                        'test_name': 'update_f0_l1_sub1_o1_by_staff',
                        'args': {'pk': self.floors['f0_l1_sub1_o1'].id},
                        'user': 'staff_user',
                        'data': {
                            'number': 3,
                        },
                        'status': status.HTTP_403_FORBIDDEN,
                    },
                    {
                        # update f0_l1_sub1_o1 by org 1 admin, not
                        # permissable
                        'test_name': 'update_f0_l1_sub1_o1_by_org_1_admin',
                        'args': {'pk': self.floors['f0_l1_sub1_o1'].id},
                        'user': 'org_1_admin_user',
                        'data': {
                            'number': 3,
                        },
                        'status': status.HTTP_403_FORBIDDEN,
                    },
                    {   # update f0_l1_sub1_o1 by employee user, forbidden
                        'test_name': 'update_f0_l1_sub1_o1_by_employee',
                        'args': {'pk': self.floors['f0_l1_sub1_o1'].id},
                        'user': 'employee_user',
                        'data': {
                            'number': 0,
                            'location': self.floors['f0_l1_sub1_o1'].id
                        },
                        'status': status.HTTP_403_FORBIDDEN
                    },
                ]
            },
        ]

    def test_(self):
        """
        The single test function that runs all the test cases defined in
        the self.test_sets.
        """
        for test_config in self.test:
            self.run_single_test(test_config)
