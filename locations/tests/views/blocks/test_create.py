"""
Defines the unit tests related to 'create' api requests for this application.
"""
from django.urls import include, path
from rest_framework import status

from core.tests import TestsBase


# pylint: disable=pointless-string-statement, line-too-long
class BlockCreateTests(TestsBase):
    """
    Defines unit tests for 'create' api requests for views defined at
    'locations/blocks/' url.
    """

    """Define the api url patterns used in this test unit."""
    api_urlpatterns = [
        path('locations/blocks/', include('locations.api.urls')),
    ]

    """Define the the complete url pattern used in this test unit."""
    urlpatterns = [
        path('api/v1/', include(api_urlpatterns)),
    ]

    def setUp(self):
        """
        Sets up the test cases.
        """
        super(BlockCreateTests, self).setUp()
        self.test = [
            {
                'test_name': 'create_blocks',
                'type': 'post',
                'path_name': 'blocks_list_create_delete',
                'request': [
                    {   # create block without any data, bad
                        'test_name': 'create_block_by_staff_no_data',
                        'data': {},
                        'data_format': 'multipart',
                        'user': 'staff_user',
                        'status': status.HTTP_400_BAD_REQUEST,
                    },
                    {   # create block, okay for staff but error since block 0
                        # already exists in this location
                        'test_name': 'create_block_by_staff_not_unique',
                        'data': {
                            'name': 'b1',  # b1 name already exists
                            'pixels_to_m_x': 40,
                            'pixels_to_m_y': 40,
                            'floor_map': self.get_test_floor_map_image(),
                            'floor': self.floors['f0_l1_o1'].id
                        },
                        'data_format': 'multipart',
                        'user': 'staff_user',
                        'status': status.HTTP_400_BAD_REQUEST,
                    },
                    {   # create a new unique block, okay for staff
                        # bad (location_1_org_1 has 0, 1, 2 blocks)
                        'test_name': 'create_block_by_staff',
                        'data': {
                            'name': 'create_block_by_staff',
                            'pixels_to_m_x': 40,
                            'pixels_to_m_y': 40,
                            'floor_map': self.get_test_floor_map_image(),
                            'floor': self.floors['f0_l1_o1'].id
                        },
                        'data_format': 'multipart',
                        'user': 'staff_user',
                        'status': status.HTTP_201_CREATED,
                        'response_check': lambda test, data: (
                            test.assertDictContainsSubset(
                                {
                                    'name': 'create_block_by_staff',
                                    'pixels_to_m_x': 40,
                                    'pixels_to_m_y': 40,
                                    'floor': self.floors['f0_l1_o1'].id
                                }, data)
                        )
                    },
                    {   # create block by org-admin, okay
                        'test_name': 'create_block_org_admin_1_in_org_1',
                        'data': {
                            'name': 'create_block_org_admin_1_in_org_1',
                            'pixels_to_m_x': 40,
                            'pixels_to_m_y': 40,
                            'floor_map': self.get_test_floor_map_image(),
                            'floor': self.floors['f0_l1_o1'].id
                        },
                        'data_format': 'multipart',
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_201_CREATED,
                        'response_check': lambda test, data: (
                            test.assertDictContainsSubset(
                                {
                                    'name': 'create_block_org_admin_1_in_org_1',
                                    'pixels_to_m_x': 40,
                                    'pixels_to_m_y': 40,
                                    'floor': self.floors['f0_l1_o1'].id
                                }, data)
                        )
                    },
                    {   # create block by org-admin in lower tree, okay
                        # location_1_sub_1_org_1 has blocks 0, 1, 2
                        'test_name':
                            'create_block_org_admin_1_in_sub_1_org_1',
                        'data': {
                            'name': 'create_block_org_admin_1_in_sub_1_org_1',
                            'pixels_to_m_x': 40,
                            'pixels_to_m_y': 40,
                            'floor_map': self.get_test_floor_map_image(),
                            'floor': self.floors['f0_l1_sub1_o1'].id
                        },
                        'data_format': 'multipart',
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_201_CREATED,
                        'response_check': lambda test, data: (
                            test.assertDictContainsSubset(
                                {
                                    'name': 'create_block_org_admin_1_in_sub_1_org_1',
                                    'pixels_to_m_x': 40,
                                    'pixels_to_m_y': 40,
                                    'floor': self.floors['f0_l1_sub1_o1'].id
                                }, data)
                        )
                    },
                    {   # create block by org-admin in other organization,
                        # bad
                        'test_name': 'create_block_org_admin_1_in_org_2',
                        'data': {
                            'name': 'create_block_org_admin_1_in_org_2',
                            'pixels_to_m_x': 40,
                            'pixels_to_m_y': 40,
                            'floor_map': self.get_test_floor_map_image(),
                            'floor': self.floors['f0_l1_o2'].id
                        },
                        'data_format': 'multipart',
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_400_BAD_REQUEST
                    },
                    {   # create block by org-admin in other organization
                        # lower tree, bad
                        'test_name':
                            'create_block_org_admin_1_in_sub_1_org_2',
                        'data': {
                            'name': 'create_block_org_admin_1_in_sub_1_org_2',
                            'pixels_to_m_x': 40,
                            'pixels_to_m_y': 40,
                            'floor_map': self.get_test_floor_map_image(),
                            'floor': self.floors['f0_l1_sub1_o2'].id
                        },
                        'data_format': 'multipart',
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_400_BAD_REQUEST
                    },
                    {   # create block by sub-org-admin in upper tree, bad
                        'test_name': 'create_block_sub_org_admin_1_in_org_1',
                        'data': {
                            'name': 'create_block_sub_org_admin_1_in_org_1',
                            'pixels_to_m_x': 40,
                            'pixels_to_m_y': 40,
                            'floor_map': self.get_test_floor_map_image(),
                            'floor': self.floors['f0_l1_o1'].id
                        },
                        'data_format': 'multipart',
                        'user': 'sub_org_11_admin_user',
                        'status': status.HTTP_400_BAD_REQUEST
                    },
                    {   # create block by sub-org-admin in own tree, okay
                        'test_name':
                            'create_block_sub_org_admin_1_in_sub_1_org_1',
                        'data': {
                            'name': 'create_block_sub_org_admin_1_in_sub_1_org_1',
                            'pixels_to_m_x': 40,
                            'pixels_to_m_y': 40,
                            'floor_map': self.get_test_floor_map_image(),
                            'floor': self.floors['f0_l1_sub1_o1'].id
                        },
                        'data_format': 'multipart',
                        'user': 'sub_org_11_admin_user',
                        'status': status.HTTP_201_CREATED,
                        'response_check': lambda test, data: (
                            test.assertDictContainsSubset(
                                {
                                    'name': 'create_block_sub_org_admin_1_in_sub_1_org_1',
                                    'pixels_to_m_x': 40,
                                    'pixels_to_m_y': 40,
                                    'floor': self.floors['f0_l1_sub1_o1'].id
                                }, data)
                        )
                    },
                    {   # create block by employee user, forbidden
                        'test_name': 'create_block_employee_user',
                        'data': {
                            'name': 'create_block_employee_user',
                            'pixels_to_m_x': 40,
                            'pixels_to_m_y': 40,
                            'floor_map': self.get_test_floor_map_image(),
                            'floor': self.floors['f0_l1_sub1_o1'].id
                        },
                        'data_format': 'multipart',
                        'user': 'employee_user',
                        'status': status.HTTP_403_FORBIDDEN
                    },
                    {   # create block by random user, forbidden
                        'test_name': 'create_block_other_user',
                        'data': {
                            'name': 'create_block_other_user',
                            'pixels_to_m_x': 40,
                            'pixels_to_m_y': 40,
                            'floor_map': self.get_test_floor_map_image(),
                            'floor': self.floors['f0_l1_sub1_o1'].id
                        },
                        'data_format': 'multipart',
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
