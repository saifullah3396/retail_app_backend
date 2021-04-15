"""
Defines the unit tests related to 'retrieve' api requests for this application.
"""

from django.urls import include, path
from rest_framework import status

from core.tests import TestsBase


# pylint: disable=pointless-string-statement
class LocationRetrieveTests(TestsBase):
    """
    Defines unit tests for 'retrieve' api requests for views defined
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
        super(LocationRetrieveTests, self).setUp()
        self.test = [
            {
                'test_name': 'get_location_by_id',
                'type': 'get',
                'path_name': 'locations_retrieve_update_delete',
                'request': [
                    {   # get location by id, okay for staff
                        'test_name': 'get_location_1_org_1_by_staff',
                        'args': [self.locations['location_1_org_1'].id],
                        'user': 'staff_user',
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                data.get('id', None),
                                str(self.locations['location_1_org_1'].id))
                        )
                    },
                    {   # get location by id, okay for org admin itself
                        'test_name': 'get_location_1_org_1_by_org_1_admin',
                        'args': [self.locations['location_1_org_1'].id],
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                data.get('id', None),
                                str(self.locations['location_1_org_1'].id))
                        )
                    },
                    {   # get location of org, forbidden for sub-org admin
                        'test_name': 'get_location_1_org_1_by_sub_org_1_admin',
                        'args': [self.locations['location_1_org_1'].id],
                        'user': 'sub_org_11_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # get location, bad for other org-admin
                        'test_name': 'get_location_1_org_1_by_org_2_admin',
                        'args': [self.locations['location_1_org_1'].id],
                        'user': 'org_2_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # get location by id, forbidden for random user
                        'test_name': 'get_location_1_org_1_by_other_user',
                        'args': [self.locations['location_1_org_1'].id],
                        'user': 'other_user',
                        'status': status.HTTP_403_FORBIDDEN
                    },
                ]
            },
            {
                'test_name': 'get_sub_location_by_id',
                'type': 'get',
                'path_name': 'locations_retrieve_update_delete',
                'request': [
                    {   # get sub-org location by id, okay for staff
                        'test_name': 'get_location_1_sub_1_org_1_by_staff',
                        'args': [self.locations['location_1_sub_1_org_1'].id],
                        'user': 'staff_user',
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                data.get('id', None),
                                str(
                                    self.locations[
                                        'location_1_sub_1_org_1'].id))
                        )
                    },
                    {   # get sub-org location by id, okay for org admin itself
                        # under which this sub-org exists
                        'test_name':
                            'get_location_1_sub_1_org_1_by_org_1_admin',
                        'args': [self.locations['location_1_sub_1_org_1'].id],
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                data.get('id', None),
                                str(
                                    self.locations[
                                        'location_1_sub_1_org_1'].id))
                        )
                    },
                    {   # get sub-org location by id, okay for sub-org admin
                        # itself
                        'test_name':
                            'get_location_1_sub_1_org_1_by_sub_1_org_1_admin',
                        'args': [self.locations['location_1_sub_1_org_1'].id],
                        'user': 'sub_org_11_admin_user',
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                data.get('id', None),
                                str(
                                    self.locations[
                                        'location_1_sub_1_org_1'].id))
                        )
                    },
                    {   # get sub-org location by id, bad for other
                        # org-admin under which this sub-org does not exist
                        'test_name':
                            'get_location_1_sub_1_org_1_by_org_2_admin',
                        'args': [self.locations['location_1_sub_1_org_1'].id],
                        'user': 'org_2_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # get sub-org location by id, bad for other
                        # sub-org admin to which this sub-org does not exist
                        'test_name':
                            'get_location_1_sub_1_org_1_by_sub_1_org_2_admin',
                        'args': [self.locations['location_1_sub_1_org_1'].id],
                        'user': 'sub_org_12_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # get employees auth location info, okay
                        'test_name': 'get_location_1_sub_1_org_1_by_employee',
                        'args': [self.locations['location_1_sub_1_org_1'].id],
                        'user': 'employee_user',
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                data.get('id', None),
                                str(self.locations[
                                    'location_1_sub_1_org_1'].id))
                        )
                    },
                    {   # get employees unauth location info, bad
                        'test_name': 'get_location_1_sub_1_org_1_by_employee',
                        'args': [self.locations['location_1_sub_1_org_2'].id],
                        'user': 'employee_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # get sub-org by id, forbidden for random user
                        'test_name': 'get_location_1_sub_1_org_1_by_other_user',
                        'args': [self.locations['location_1_sub_1_org_1'].id],
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
