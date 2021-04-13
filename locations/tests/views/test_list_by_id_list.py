"""
Defines the unit tests related to 'list-by-id-list' api requests for this
application.
"""
from django.urls import include, path
from rest_framework import status

from core.tests import TestsBase


# pylint: disable=pointless-string-statement
class LocationListByIdListTests(TestsBase):
    """
    Defines unit tests for 'list-by-id-list' api requests for views defined
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
        super(LocationListByIdListTests, self).setUp()
        self.test = [
            {
                'test_name': 'get_locations_list_multiple',
                'type': 'get',
                'path_name': 'locations_list_create_delete',
                'request': [
                    {   # get locations list by staff
                        'test_name': 'test_get_locations_list_by_ids_by_staff',
                        'args': None,
                        'data': {
                            'id': [
                                self.locations['location_1_org_1'].id,
                                self.locations['location_2_org_1'].id,
                                self.locations['location_1_org_2'].id]
                        },
                        'user': 'staff_user',
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(len(data.get('results', None)), 3)
                        )
                    },
                    {   # get locations of different org (1) by org admin (2),
                        # forbidden
                        'test_name':
                            'test_get_org_1_locations_by_id_by_org_2_admin',
                        'args': None,
                        'data': {
                            'id': [
                                self.locations['location_1_org_1'].id,
                                self.locations['location_2_org_1'].id]
                        },
                        'user': 'org_2_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # get locations of different org (2) by sub-org
                        # admin (1), forbidden
                        'test_name':
                            'test_get_org_2_locations_by_id_by_sub_org_1_admin',
                        'args': None,
                        'data': {
                            'id': [
                                self.locations['location_1_org_2'].id,
                                self.locations['location_2_org_2'].id]
                        },
                        'user': 'sub_org_11_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # get locations of same org (1) by sub-org
                        # admin (1), forbidden
                        'test_name':
                            'test_get_org_1_locations_by_id_by_sub_org_1_admin',
                        'args': None,
                        'data': {
                            'id': [
                                self.locations['location_1_org_1'].id,
                                self.locations['location_1_org_2'].id]
                        },
                        'user': 'sub_org_11_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # get locations of same org (1) by sub-org
                        # admin (1), okay
                        'test_name':
                            'test_get_sub_org_1_locations_by_id_by_sub_org_1_'
                            'admin',
                        'args': None,
                        'data': {
                            'id': [
                                self.locations['location_1_sub_1_org_1'].id,
                                self.locations['location_2_sub_1_org_1'].id]
                        },
                        'user': 'sub_org_11_admin_user',
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(len(data.get('results', None)), 2)
                        )
                    },
                    {   # get locations of org (1) by org admin (1),
                        # should work
                        'test_name':
                            'test_get_org_1_locations_by_id_by_org_1_admin',
                        'args': None,
                        'data': {
                            'id': [
                                self.locations['location_1_org_1'].id,
                                self.locations['location_2_org_1'].id]
                        },
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(len(data.get('results', None)), 2)
                        )
                    },
                    {   # get authorized locations list of locations by
                        # employee
                        'test_name':
                            'test_get_auth_locations_by_sub_org_1_employee',
                        'args': None,
                        'data': {
                            'id': [
                                self.locations['location_1_sub_1_org_1'].id,
                                self.locations['location_2_sub_1_org_1'].id]
                        },
                        'user': 'employee_user',
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(len(data.get('results', None)), 2)
                        )
                    },
                    {   # get unauthorized locations list of locations by
                        # employee
                        'test_name':
                            'test_get_unauth_locations_by_sub_org_1_employee',
                        'args': None,
                        'data': {
                            'id': [
                                self.locations['location_1_org_1'].id,
                                self.locations['location_2_org_1'].id]
                        },
                        'user': 'employee_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # get locations list of locations by some random user
                        'test_name': 'test_get_locations_by_other_user',
                        'args': None,
                        'data': {
                            'id': [
                                self.locations['location_1_org_1'].id,
                                self.locations['location_2_org_1'].id]
                        },
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
