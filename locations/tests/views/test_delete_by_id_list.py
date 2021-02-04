"""
Defines the unit tests related to 'delete-by-id-list' api requests for this
application.
"""
import copy

from core.tests import TestsBase
from django.urls import include, path, reverse
from rest_framework import status


class LocationDeleteByIdListTests(TestsBase):
    """
    Defines unit tests for 'delete-by-id-list' api requests for views defined
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
        super(LocationDeleteByIdListTests, self).setUp()
        self.test = [
            {
                'test_name': 'delete_multiple_locations',
                'type': 'delete',
                'path_name': 'locations_list_create_delete',
                'request': [
                    {   # delete location, okay for staff
                        'test_name': 'delete_location_by_staff',
                        'data': {
                            'id': [
                                self.locations['location_1_org_1'].id,
                                self.locations['location_2_org_1'].id]
                        },
                        'user': 'staff_user',
                        'status': status.HTTP_200_OK
                    },
                    {   # duplicate delete by staff, bad
                        'test_name': 'delete_dup_location_by_staff',
                        'data': {
                            'id': [
                                self.locations['location_1_org_1'].id,
                                self.locations['location_2_org_1'].id]
                        },
                        'user': 'staff_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # delete location by org-admin, okay
                        'test_name': 'delete_location_org_admin_2_in_org_2',
                        'data': {
                            'id': [
                                self.locations['location_1_org_2'].id,
                                self.locations['location_2_org_2'].id]
                        },
                        'user': 'org_2_admin_user',
                        'status': status.HTTP_200_OK
                    },
                    {   # delete location by org-admin in lower tree, okay
                        'test_name': 'delete_location_org_admin_1_in_sub_1_org_1',
                        'data': {
                            'id': [
                                self.locations['location_1_sub_1_org_1'].id]
                        },
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_200_OK
                    },
                    {   # delete location by org-admin in other organization,
                        # bad
                        'test_name': 'delete_location_org_admin_1_in_org_2',
                        'data': {
                            'id': [
                                self.locations['location_3_org_2'].id]
                        },
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # delete location by org-admin in other organization
                        # lower tree, bad
                        'test_name': 'delete_location_org_admin_1_in_sub_1_org_2',
                        'data': {
                            'id': [
                                self.locations['location_1_sub_1_org_2'].id]
                        },
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # delete location by sub-org-admin in upper tree, bad
                        'test_name': 'delete_location_sub_org_admin_1_in_org_1',
                        'data': {
                            'id': [
                                self.locations['location_4_org_1'].id,
                                self.locations['location_5_org_1'].id
                            ]
                        },
                        'user': 'sub_org_11_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # delete location by sub-org-admin in own tree, okay
                        'test_name': 'delete_location_sub_org_admin_1_in_sub_1_org_1',
                        'data': {
                            'id': [
                                self.locations['location_3_sub_1_org_1'].id,
                                self.locations['location_4_sub_1_org_1'].id
                            ]
                        },
                        'user': 'sub_org_11_admin_user',
                        'status': status.HTTP_200_OK
                    },
                    {   # delete location by employee user, forbidden
                        'test_name': 'delete_location_other_user',
                        'data': {
                            'id': [
                                self.locations['location_3_sub_1_org_1'].id,
                                self.locations['location_4_sub_1_org_1'].id
                            ]
                        },
                        'user': 'employee_user',
                        'status': status.HTTP_403_FORBIDDEN
                    },
                    {   # delete location by random user, forbidden
                        'test_name': 'delete_location_other_user',
                        'data': {
                            'id': [
                                self.locations['location_1_org_1'].id,
                                self.locations['location_2_org_2'].id
                            ]
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
