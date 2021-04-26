"""
Defines the unit tests related to 'delete' api requests for this application.
"""

from django.urls import include, path
from rest_framework import status

from core.tests import TestsBase


# pylint: disable=pointless-string-statement
class FloorDeleteTests(TestsBase):
    """
    Defines unit tests for 'delete' api requests for views defined
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
        super(FloorDeleteTests, self).setUp()
        self.test = [
            {
                'test_name': 'delete_floor_by_id',
                'type': 'delete',
                'path_name': 'floors_retrieve_update_delete',
                'request': [
                    {
                        # delete floor 0 location 1 org 1 by staff, bad
                        # can only start from top floor (location has
                        # floors 0, 1, 2, 3, 4)
                        'test_name': 'delete_lower_floor_by_staff',
                        'args': {'pk': self.floors['f0_l1_o1'].id},
                        'user': 'staff_user',
                        'status': status.HTTP_400_BAD_REQUEST
                    },
                    {
                        # delete floor 4 location 1 org 1 by staff, okay
                        # (location has floors 0, 1, 2, 3, 4)
                        'test_name': 'delete_floor_by_staff',
                        'args': {'pk': self.floors['f4_l1_o1_for_deletion'].id},
                        'user': 'staff_user',
                        'status': status.HTTP_200_OK
                    },
                    {   # delete floor 3 location 1 org 1 by org 1 admin, okay
                        # (location has floors 0, 1,2 , 3 now)
                        'test_name': 'delete_floor_in_org_1_by_org_1_admin',
                        'args': {'pk': self.floors['f3_l1_o1_for_deletion'].id},
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_200_OK
                    },
                    {   # delete floor in higher level organization,
                        # no access (location_1 is in org_1)
                        'test_name':
                            'delete_floor_0_location_1_by_sub_1_org_1_admin',
                        'args': {'pk': self.floors['f0_l1_o1'].id},
                        'user': 'sub_org_11_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # delete floor of different org, bad (location 1 is in
                        # org 1)
                        'test_name': 'delete_floor_0_location_1_by_org_2_admin',
                        'args': {'pk': self.floors['f0_l1_o1'].id},
                        'user': 'org_2_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # delete floor in org by id, forbidden for employee
                        'test_name':
                            'delete_f0_l1_o1_by_sub_org_1_'
                            'employee',
                        'args': {'pk': self.floors['f0_l1_sub1_o1'].id},
                        'user': 'employee_user',
                        'status': status.HTTP_403_FORBIDDEN
                    },
                    {   # delete floor by id, forbidden for random user
                        'test_name':
                            'delete_f0_l1_sub1_o1_by_other_user',
                        'args': {'pk': self.floors['f0_l1_sub1_o1'].id},
                        'user': 'other_user',
                        'status': status.HTTP_403_FORBIDDEN
                    }
                ]
            },
            {
                'test_name': 'delete_sub_floor_by_id',
                'type': 'delete',
                'path_name': 'floors_retrieve_update_delete',
                'request': [
                    {   # delete sub-org floor by id, okay for staff
                        'test_name':
                            'delete_floor_2_location_1_sub_1_by_staff_user',
                        'args': {'pk': self.floors['f4_l1_sub1_o1'].id},
                        'user': 'staff_user',
                        'status': status.HTTP_200_OK
                    },
                    {   # delete sub-org floor by id, okay for org admin itself under
                        # which this sub-org exists
                        'test_name':
                            'delete_f1_l1_sub1_o1_by_org_1_admin',
                        'args': {'pk': self.floors['f3_l1_sub1_o1'].id},
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_200_OK
                    },
                    {   # delete sub-org floor by id, okay for sub-org admin
                        # itself
                        'test_name':
                            'delete_f0_l1_sub1_o1_by_sub_1_org_1_admin',
                        'args': {'pk': self.floors['f2_l1_sub1_o1'].id},
                        'user': 'sub_org_11_admin_user',
                        'status': status.HTTP_200_OK
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
