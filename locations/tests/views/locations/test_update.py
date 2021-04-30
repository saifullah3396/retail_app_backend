"""
Defines the unit tests related to 'update' api requests for this application.
"""

from django.urls import include, path
from rest_framework import status

from core.tests import TestsBase


# pylint: disable=pointless-string-statement, line-too-long, invalid-name
class LocationUpdateTests(TestsBase):
    """
    Defines unit tests for 'update' api requests for views defined
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
        super(LocationUpdateTests, self).setUp()
        self.test = [
            {
                'test_name': 'update_location_by_id',
                'type': 'patch',
                'path_name': 'locations_retrieve_update_delete',
                'request': [
                    {
                        # update location 1 org 1 by staff, okay
                        'test_name': 'update_location_1_org_1_by_staff',
                        'args': {'pk': self.locations['l1_o1'].id},
                        'user': 'staff_user',
                        'data': {
                            'name': 'location_1_org_1_updated',
                        },
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                data.get('name', None),
                                'location_1_org_1_updated')
                        )
                    },
                    {   # update location_1_org_1 by id by org_1 admin, okay
                        'test_name': 'update_location_1_org_1_by_org_1_admin',
                        'args': {'pk': self.locations['l1_o1'].id},
                        'user': 'org_1_admin_user',
                        'data': {
                            'name': 'location_1_org_1_updated',
                        },
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                data.get('name', None),
                                'location_1_org_1_updated')
                        )
                    },
                    {   # update location in higher level organization,
                        # no access
                        'test_name':
                            'update_location_1_org_1_by_sub_1_org_1_admin',
                        'args': {'pk': self.locations['l1_o1'].id},
                        'user': 'sub_org_11_admin_user',
                        'data': {
                            'name': 'location_1_org_1_updated',
                        },
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # update location of different org, bad
                        'test_name': 'update_location_1_org_1_by_org_2_admin',
                        'args': {'pk': self.locations['l1_o1'].id},
                        'user': 'org_2_admin_user',
                        'data': {
                            'name': 'location_1_org_1_updated',
                        },
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # update location in org by id, forbidden for employee
                        'test_name':
                            'update_location_1_sub_1_org_1_by_sub_org_1_'
                            'employee',
                        'args': {'pk': self.locations['l1_sub1_o1'].id},
                        'user': 'employee_user',
                        'data': {
                            'name': 'location_1_sub_1_org_1_updated',
                        },
                        'status': status.HTTP_403_FORBIDDEN
                    },
                    {   # update location by id, forbidden for random user
                        'test_name':
                            'update_location_1_sub_1_org_1_by_other_user',
                        'args': {'pk': self.locations['l1_sub1_o1'].id},
                        'user': 'other_user',
                        'data': {
                            'name': 'location_1_sub_1_org_1_updated',
                        },
                        'status': status.HTTP_403_FORBIDDEN
                    }
                ]
            },
            {
                'test_name': 'update_sub_location_by_id',
                'type': 'patch',
                'path_name': 'locations_retrieve_update_delete',
                'request': [
                    {   # update sub-org location by id, okay for staff
                        'test_name':
                            'update_location_1_sub_1_org_1_by_staff_user',
                        'args': {'pk': self.locations['l1_sub1_o1'].id},
                        'user': 'staff_user',
                        'data': {
                            'name': 'location_1_sub_1_org_1_updated',
                        },
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                data.get('name', None),
                                'location_1_sub_1_org_1_updated')
                        )
                    },
                    {   # update sub-org by id, okay for org admin itself under
                        # which this sub-org exists
                        'test_name':
                            'update_location_1_sub_1_org_1_by_org_1_admin',
                        'args': {'pk': self.locations['l1_sub1_o1'].id},
                        'user': 'org_1_admin_user',
                        'data': {
                            'name': 'location_1_sub_1_org_1_updated',
                        },
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                data.get('name', None),
                                'location_1_sub_1_org_1_updated')
                        )
                    },
                    {   # update sub-org location by id, okay for sub-org
                        # admin itself
                        'test_name':
                            'update_location_1_sub_1_org_1_by_sub_1_org_1_'
                            'admin',
                        'args': {'pk': self.locations['l1_sub1_o1'].id},
                        'user': 'sub_org_11_admin_user',
                        'data': {
                            'name': 'location_1_sub_1_org_1_updated',
                        },
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                data.get('name', None),
                                'location_1_sub_1_org_1_updated')
                        )
                    },
                    {   # test for bad duplicate name
                        'test_name':
                            'update_location_1_sub_1_org_2_by_sub_1_org_2_'
                            'admin',
                        'args': {'pk': self.locations['l2_sub1_o1'].id},
                        'user': 'sub_org_11_admin_user',
                        'data': {
                            'name': 'location_1_sub_1_org_1_updated',
                        },
                        'status': status.HTTP_400_BAD_REQUEST
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
