"""
Defines the unit tests related to 'delete' api requests for this application.
"""

from django.urls import include, path
from rest_framework import status

from core.tests import TestsBase


# pylint: disable=pointless-string-statement
class LocationDeleteTests(TestsBase):
    """
    Defines unit tests for 'delete' api requests for views defined
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
        super(LocationDeleteTests, self).setUp()
        self.test = [
            {
                'test_name': 'delete_location_by_id',
                'type': 'patch',
                'path_name': 'locations_retrieve_update_delete',
                'request': [
                    {
                        # delete location 1 org 1 by staff, okay
                        'test_name': 'delete_location_1_org_1_by_staff',
                        'args': [self.locations['location_1_org_1'].id],
                        'user': 'staff_user',
                        'status': status.HTTP_200_OK
                    },
                    {   # delete location_2_org_1 by id by org_1 admin, okay
                        'test_name': 'delete_location_2_org_1_by_org_1_admin',
                        'args': [self.locations['location_2_org_1'].id],
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_200_OK
                    },
                    {   # delete location in higher level organization,
                        # no access
                        'test_name':
                            'delete_location_1_org_2_by_sub_1_org_2_admin',
                        'args': [self.locations['location_1_org_2'].id],
                        'user': 'sub_org_12_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # delete location of different org, bad
                        'test_name': 'delete_location_1_org_1_by_org_2_admin',
                        'args': [self.locations['location_3_org_1'].id],
                        'user': 'org_2_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # delete location in org by id, forbidden for employee
                        'test_name':
                            'delete_location_1_sub_1_org_1_by_sub_org_1_'
                            'employee',
                        'args': [self.locations['location_1_sub_1_org_1'].id],
                        'user': 'employee_user',
                        'status': status.HTTP_403_FORBIDDEN
                    },
                    {   # delete location by id, forbidden for random user
                        'test_name':
                            'delete_location_1_sub_1_org_1_by_other_user',
                        'args': [self.locations['location_1_sub_1_org_1'].id],
                        'user': 'other_user',
                        'status': status.HTTP_403_FORBIDDEN
                    }
                ]
            },
            {
                'test_name': 'delete_sub_location_by_id',
                'type': 'patch',
                'path_name': 'locations_retrieve_update_delete',
                'request': [
                    {   # delete sub-org location by id, okay for staff
                        'test_name':
                            'delete_location_1_sub_1_org_1_by_staff_user',
                        'args': [self.locations['location_1_sub_1_org_1'].id],
                        'user': 'staff_user',
                        'status': status.HTTP_200_OK
                    },
                    {   # delete sub-org by id, okay for org admin itself under
                        # which this sub-org exists
                        'test_name':
                            'delete_location_2_sub_1_org_1_by_org_1_admin',
                        'args': [self.locations['location_2_sub_1_org_1'].id],
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_200_OK
                    },
                    {   # delete sub-org location by id, okay for sub-org admin
                        # itself
                        'test_name':
                            'delete_location_3_sub_1_org_1_by_sub_1_org_1_'
                            'admin',
                        'args': [self.locations['location_3_sub_1_org_1'].id],
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
