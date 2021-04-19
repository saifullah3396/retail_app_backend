"""
Defines the unit tests related to 'create' api requests for this application.
"""
from django.urls import include, path
from rest_framework import status

from core.tests import TestsBase


# pylint: disable=pointless-string-statement
class FloorCreateTests(TestsBase):
    """
    Defines unit tests for 'create' api requests for views defined at
    'locations/floors/' url.
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
        super(FloorCreateTests, self).setUp()
        self.test = [
            {
                'test_name': 'create_floors',
                'type': 'post',
                'path_name': 'floors_list_create_delete',
                'request': [
                    {   # create floor without any data, bad
                        'test_name': 'create_floor_by_staff_no_data',
                        'data': {},
                        'user': 'staff_user',
                        'status': status.HTTP_400_BAD_REQUEST,
                    },
                    {   # create floor, okay for staff but error since floor 0
                        # already exists in this location
                        'test_name': 'create_floor_by_staff_not_unique',
                        'data': {
                            'number': 0,
                            'location': self.locations['location_1_org_1'].id
                        },
                        'user': 'staff_user',
                        'status': status.HTTP_400_BAD_REQUEST,
                    },
                    {   # create a new unique floor with no floor in between,
                        # bad (location_1_org_1 has 0, 1, 2 floors)
                        'test_name': 'create_floor_by_staff_no_floor_in_between',
                        'data': {
                            'number': 4,
                            'location': self.locations['location_1_org_1'].id
                        },
                        'user': 'staff_user',
                        'status': status.HTTP_400_BAD_REQUEST,
                    },
                    {   # create a new unique floor, okay for staff
                        # bad (location_1_org_1 has 0, 1, 2 floors)
                        'test_name': 'create_floor_by_staff',
                        'data': {
                            'number': 3,
                            'location': self.locations['location_1_org_1'].id
                        },
                        'user': 'staff_user',
                        'status': status.HTTP_201_CREATED,
                        'response_check': lambda test, data: (
                            test.assertDictContainsSubset(
                                {
                                    'number': 3,
                                    'location':
                                        self.locations['location_1_org_1'].id
                                }, data)
                        )
                    },
                    {   # create floor by org-admin, okay
                        'test_name': 'create_floor_org_admin_1_in_org_1',
                        'data': {
                            'number': 4,
                            'location': self.locations['location_1_org_1'].id
                        },
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_201_CREATED,
                        'response_check': lambda test, data: (
                            test.assertDictContainsSubset(
                                {
                                    'number': 4,
                                    'location':
                                        self.locations['location_1_org_1'].id
                                }, data)
                        )
                    },
                    {   # create floor by org-admin in lower tree, okay
                        'test_name':
                            'create_floor_org_admin_1_in_sub_1_org_1',
                        'data': {
                            'number': 0,
                            'location': self.locations['location_1_sub_1_org_1'].id
                        },
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_201_CREATED,
                        'response_check': lambda test, data: (
                            test.assertDictContainsSubset(
                                {
                                    'number': 0,
                                    'location':
                                        self.locations['location_1_sub_1_org_1'].id
                                }, data)
                        )
                    },
                    {   # create floor by org-admin in other organization,
                        # bad
                        'test_name': 'create_floor_org_admin_1_in_org_2',
                        'data': {
                            'number': 0,
                            'location': self.locations['location_1_org_2'].id
                        },
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_400_BAD_REQUEST
                    },
                    {   # create floor by org-admin in other organization
                        # lower tree, bad
                        'test_name':
                            'create_floor_org_admin_1_in_sub_1_org_2',
                        'data': {
                            'number': 0,
                            'location': self.locations['location_1_sub_1_org_2'].id
                        },
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_400_BAD_REQUEST
                    },
                    {   # create floor by sub-org-admin in upper tree, bad
                        'test_name': 'create_floor_sub_org_admin_1_in_org_1',
                        'data': {
                            'number': 0,
                            'location': self.locations['location_1_org_1'].id
                        },
                        'user': 'sub_org_11_admin_user',
                        'status': status.HTTP_400_BAD_REQUEST
                    },
                    {   # create floor by sub-org-admin in own tree, bad
                        'test_name':
                            'create_floor_sub_org_admin_1_in_sub_1_org_1',
                        'data': {
                            'number': 0,
                            'location': self.locations['location_2_sub_1_org_1'].id
                        },
                        'user': 'sub_org_11_admin_user',
                        'status': status.HTTP_201_CREATED,
                        'response_check': lambda test, data: (
                            test.assertDictContainsSubset(
                                {
                                    'number': 0,
                                    'location':
                                        self.locations['location_2_sub_1_org_1'].id
                                }, data)
                        )
                    },
                    {   # create floor by employee user, forbidden
                        'test_name': 'create_floor_employee_user',
                        'data': {
                            'number': 0,
                            'location': self.locations['location_1_org_1'].id
                        },
                        'user': 'employee_user',
                        'status': status.HTTP_403_FORBIDDEN
                    },
                    {   # create floor by random user, forbidden
                        'test_name': 'create_floor_other_user',
                        'data': {
                            'number': 0,
                            'location': self.locations['location_1_org_1'].id
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
