"""
Defines the unit tests related to 'create' api requests for this application.
"""
from django.urls import include, path
from rest_framework import status

from core.tests import TestsBase


# pylint: disable=pointless-string-statement
class LocationCreateTests(TestsBase):
    """
    Defines unit tests for 'create' api requests for views defined at
    'locations/' url.
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
        super(LocationCreateTests, self).setUp()
        self.test = [
            {
                'test_name': 'create_locations',
                'type': 'post',
                'path_name': 'locations_list_create_delete',
                'request': [
                    {   # create location without any data, bad
                        'test_name': 'create_location_by_staff',
                        'data': {},
                        'user': 'staff_user',
                        'status': status.HTTP_400_BAD_REQUEST,
                    },
                    {   # create location, okay for staff
                        'test_name': 'create_location_by_staff',
                        'data': {
                            'name': 'My location',
                            'organization': self.orgs['org_1'].id
                        },
                        'user': 'staff_user',
                        'status': status.HTTP_201_CREATED,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                data.get('name', None), 'My location')
                        )
                    },
                    {   # create location with wrong info, bad
                        'test_name': 'create_location_by_staff',
                        'data': {
                            'name': 'My location',
                        },
                        'user': 'staff_user',
                        'status': status.HTTP_400_BAD_REQUEST,
                    },
                    {   # create location with wrong info, bad
                        'test_name': 'create_location_by_staff',
                        'data': {
                            'organization': self.orgs['org_1'].id
                        },
                        'user': 'staff_user',
                        'status': status.HTTP_400_BAD_REQUEST,
                    },
                    {   # duplicate create by staff, bad
                        'test_name': 'create_dup_location_by_staff',
                        'data': {
                            'name': 'My location',
                            'organization': self.orgs['org_1'].id
                        },
                        'user': 'staff_user',
                        'status': status.HTTP_400_BAD_REQUEST
                    },
                    {   # create location by org-admin, okay
                        'test_name': 'create_location_org_admin_1_in_org_1',
                        'data': {
                            'name': 'My location 1',
                            'organization': self.orgs['org_1'].id
                        },
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_201_CREATED,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                data.get('name', None), 'My location 1')
                        )
                    },
                    {   # create location by org-admin in lower tree, okay
                        'test_name':
                            'create_location_org_admin_1_in_sub_1_org_1',
                        'data': {
                            'name': 'My location 2',
                            'organization': self.orgs['sub_1_org_1'].id
                        },
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_201_CREATED,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                data.get('name', None), 'My location 2')
                        )
                    },
                    {   # create location by org-admin in other organization,
                        # bad
                        'test_name': 'create_location_org_admin_1_in_org_2',
                        'data': {
                            'name': 'My location 3',
                            'organization': self.orgs['org_2'].id
                        },
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_400_BAD_REQUEST
                    },
                    {   # create location by org-admin in other organization
                        # lower tree, bad
                        'test_name':
                            'create_location_org_admin_1_in_sub_1_org_2',
                        'data': {
                            'name': 'My location 4',
                            'organization': self.orgs['sub_1_org_2'].id
                        },
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_400_BAD_REQUEST
                    },
                    {   # create location by sub-org-admin in upper tree, bad
                        'test_name': 'create_location_sub_org_admin_1_in_org_1',
                        'data': {
                            'name': 'My location 5',
                            'organization': self.orgs['org_1'].id
                        },
                        'user': 'sub_org_11_admin_user',
                        'status': status.HTTP_400_BAD_REQUEST
                    },
                    {   # create location by sub-org-admin in own tree, bad
                        'test_name':
                            'create_location_sub_org_admin_1_in_sub_1_org_1',
                        'data': {
                            'name': 'My location 6',
                            'organization': self.orgs['sub_1_org_1'].id
                        },
                        'user': 'sub_org_11_admin_user',
                        'status': status.HTTP_201_CREATED,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                data.get('name', None), 'My location 6')
                        )
                    },
                    {   # create location by random user, forbidden
                        'test_name': 'create_location_other_user',
                        'data': {
                            'name': 'My location 7',
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
