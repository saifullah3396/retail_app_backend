"""
Defines the unit tests related to 'retrieve' api requests for this application.
"""

from django.urls import include, path
from rest_framework import status

from core.tests import TestsBase


# pylint: disable=pointless-string-statement
class BlockUpdateTests(TestsBase):
    """
    Defines unit tests for 'update' api requests for views defined
    at 'locations/' url.
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
        super(BlockUpdateTests, self).setUp()
        self.test = [
            {
                'test_name': 'update_block_by_id',
                'type': 'patch',
                'path_name': 'blocks_retrieve_update_delete',
                'request': [
                    {   # update block by id. change name to an existing
                        # block name inside the floor, bad
                        'test_name': 'update_block_by_id',
                        'args': {'pk': self.blocks['b1_f0_l1_o1'].id},
                        'user': 'staff_user',
                        'data': {
                            'name': 'b2',  # b2 already exists in f0_l1_o1
                        },
                        'status': status.HTTP_400_BAD_REQUEST,
                    },
                    {   # update block by id. change floor to another floor with
                        # existing block name, bad
                        'test_name': 'update_block_by_id',
                        'args': {'pk': self.blocks['b1_f0_l1_o1'].id},
                        'user': 'staff_user',
                        'data': {
                            # b1 already exists in f1_l1_o1, floor just won't change
                            'floor': self.floors['f1_l1_o1'].id
                        },
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertDictContainsSubset(
                                {
                                    'floor': self.floors['f0_l1_o1'].id
                                }, data)
                        )
                    },
                    {   # update block by id, okay for staff
                        'test_name': 'update_b1_f0_l1_o1_by_staff',
                        'args': {'pk': self.blocks['b1_f0_l1_o1'].id},
                        'user': 'staff_user',
                        'data': {
                            'name': 'update_b1_f0_l1_o1_by_staff',
                            'pixels_to_m_x': 30,
                            'pixels_to_m_y': 30,
                            'floor': self.floors['f0_l1_o1'].id
                        },
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertDictContainsSubset(
                                {
                                    'name': 'update_b1_f0_l1_o1_by_staff',
                                    'pixels_to_m_x': 30,
                                    'pixels_to_m_y': 30,
                                    'floor': self.floors['f0_l1_o1'].id
                                }, data)
                        )
                    },
                    {   # update block by id, okay for org_1_admin
                        'test_name': 'update_b1_f0_l1_o1_by_org_1_admin',
                        'args': {'pk': self.blocks['b1_f0_l1_o1'].id},
                        'user': 'org_1_admin_user',
                        'data': {
                            'name': 'update_b1_f0_l1_o1_by_org_1_admin',
                            'pixels_to_m_x': 30,
                            'pixels_to_m_y': 30,
                            'floor': self.floors['f0_l1_o1'].id
                        },
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertDictContainsSubset(
                                {
                                    'name': 'update_b1_f0_l1_o1_by_org_1_admin',
                                    'pixels_to_m_x': 30,
                                    'pixels_to_m_y': 30,
                                    'floor': self.floors['f0_l1_o1'].id
                                }, data)
                        )
                    },
                    {   # update block of org, forbidden for sub-org admin
                        'test_name': 'update_b1_f0_l1_o1_by_sub_org_1_admin',
                        'args': {'pk': self.blocks['b1_f0_l1_o1'].id},
                        'user': 'sub_org_11_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # update block, bad for other org-admin
                        'test_name': 'update_b1_f0_l1_o1_by_org_2_admin',
                        'args': {'pk': self.blocks['b1_f0_l1_o1'].id},
                        'user': 'org_2_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # update block by id, forbidden for random user
                        'test_name': 'update_b1_f0_l1_o1_by_other_user',
                        'args': {'pk': self.blocks['b1_f0_l1_o1'].id},
                        'user': 'other_user',
                        'status': status.HTTP_403_FORBIDDEN
                    },
                ]
            },
            {
                'test_name': 'update_sub_block_by_id',
                'type': 'patch',
                'path_name': 'blocks_retrieve_update_delete',
                'request': [
                    {   # update sub-org block by id, okay for staff
                        'test_name': 'update_b1_f0_l1_sub1_o1_by_staff',
                        'args': {'pk': self.blocks['b1_f0_l1_sub1_o1'].id},
                        'user': 'staff_user',
                        'data': {
                            'name': 'update_b1_f0_l1_sub1_o1_by_staff',
                        },
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertDictContainsSubset(
                                {
                                    'name': 'update_b1_f0_l1_sub1_o1_by_staff',
                                }, data)
                        )
                    },
                    {   # update sub-org block by id, okay for org admin itself
                        # under which this sub-org exists
                        'test_name':
                            'update_b1_f0_l1_sub1_o1_by_org_1_admin',
                        'args': {'pk': self.blocks['b1_f0_l1_sub1_o1'].id},
                        'user': 'org_1_admin_user',
                        'data': {
                            'name': 'update_b1_f0_l1_sub1_o1_by_org_1_admin',
                        },
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertDictContainsSubset(
                                {
                                    'name': 'update_b1_f0_l1_sub1_o1_by_org_1_admin',
                                }, data)
                        )
                    },
                    {   # update sub-org block by id, okay for sub-org admin
                        # itself
                        'test_name':
                            'update_b1_f0_l1_sub1_o1_by_sub_1_org_1_admin',
                        'args': {'pk': self.blocks['b1_f0_l1_sub1_o1'].id},
                        'user': 'sub_org_11_admin_user',
                        'data': {
                            'name': 'update_b1_f0_l1_sub1_o1_by_sub_1_org_1_admin',
                        },
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertDictContainsSubset(
                                {
                                    'name': 'update_b1_f0_l1_sub1_o1_by_sub_1_org_1_admin',
                                }, data)
                        )
                    },
                    {   # update sub-org block by id, bad for other
                        # org-admin under which this sub-org does not exist
                        'test_name':
                            'update_b1_f0_l1_sub1_o1_by_org_2_admin',
                        'args': {'pk': self.blocks['b1_f0_l1_sub1_o1'].id},
                        'data': {
                            'name': 'update_b1_f0_l1_sub1_o1_by_org_2_admin',
                        },
                        'user': 'org_2_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # update sub-org block by id, bad for other
                        # sub-org admin to which this sub-org does not exist
                        'test_name':
                            'update_b1_f0_l1_sub1_o1_by_sub_1_org_2_admin',
                        'args': {'pk': self.blocks['b1_f0_l1_sub1_o1'].id},
                        'data': {
                            'name': 'update_b1_f0_l1_sub1_o1_by_sub_1_org_2_admin',
                        },
                        'user': 'sub_org_12_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # update sub-org block by id, forbidden for employees
                        'test_name': 'update_b1_f0_l1_sub1_o1_by_employee',
                        'args': {'pk': self.blocks['b1_f0_l1_sub1_o1'].id},
                        'user': 'employee_user',
                        'data': {
                            'name': 'update_b1_f0_l1_sub1_o1_by_employee',
                        },
                        'status': status.HTTP_403_FORBIDDEN,
                    },
                    {   # update sub-org by id, forbidden for random user
                        'test_name': 'update_b1_f0_l1_o2_by_other_user',
                        'args': {'pk': self.blocks['b1_f0_l1_o2'].id},
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
