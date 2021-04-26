"""
Defines the unit tests related to 'delete' api requests for this application.
"""

from django.urls import include, path
from rest_framework import status

from core.tests import TestsBase


# pylint: disable=pointless-string-statement
class BlockDeleteTests(TestsBase):
    """
    Defines unit tests for 'delete' api requests for views defined
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
        super(BlockDeleteTests, self).setUp()
        self.test = [
            {
                'test_name': 'delete_block_by_id',
                'type': 'delete',
                'path_name': 'blocks_retrieve_update_delete',
                'request': [
                    {
                        # delete b3_f0_l1_o1 by staff
                        'test_name': 'delete_b3_f0_l1_o1_staff',
                        'args': {'pk': self.blocks['b3_f0_l1_o1_for_deletion'].id},
                        'user': 'staff_user',
                        'status': status.HTTP_200_OK
                    },
                    {   # delete b4_f0_l1_o1 by org 1 admin
                        'test_name': 'delete_b4_f0_l1_o1_by_org1_admin',
                        'args': {'pk': self.blocks['b4_f0_l1_o1_for_deletion'].id},
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_200_OK
                    },
                    {   # delete block in higher level organization,
                        'test_name':
                            'delete_b5_f0_l1_o1_by_sub_1_org_1_admin',
                        'args': {'pk': self.blocks['b5_f0_l1_o1_for_deletion'].id},
                        'user': 'sub_org_11_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # delete block of different org, bad (location 1 is in
                        # org 1)
                        'test_name': 'delete_b5_f0_l1_o1_by_org_2_admin',
                        'args': {'pk': self.blocks['b5_f0_l1_o1_for_deletion'].id},
                        'user': 'org_2_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # delete block in org by id, forbidden for employee
                        'test_name':
                            'delete_b5_f0_l1_o1_by_sub_org_1_'
                            'employee',
                        'args': {'pk': self.blocks['b5_f0_l1_o1_for_deletion'].id},
                        'user': 'employee_user',
                        'status': status.HTTP_403_FORBIDDEN
                    },
                    {   # delete block by id, forbidden for random user
                        'test_name':
                            'delete_b5_f0_l1_o1_by_other_user',
                        'args': {'pk': self.blocks['b5_f0_l1_o1_for_deletion'].id},
                        'user': 'other_user',
                        'status': status.HTTP_403_FORBIDDEN
                    }
                ]
            },
            {
                'test_name': 'delete_sub_block_by_id',
                'type': 'delete',
                'path_name': 'blocks_retrieve_update_delete',
                'request': [
                    {   # delete sub-org block by id, okay for staff
                        'test_name':
                            'delete_b3_f0_l1_sub1_o1_by_staff_user',
                        'args': {'pk': self.blocks['b3_f0_l1_sub1_o1_for_deletion'].id},
                        'user': 'staff_user',
                        'status': status.HTTP_200_OK
                    },
                    {   # delete sub-org block by id, okay for org admin itself under
                        # which this sub-org exists
                        'test_name':
                            'delete_b4_f0_l1_sub1_o1_by_org_1_admin',
                        'args': {'pk': self.blocks['b4_f0_l1_sub1_o1_for_deletion'].id},
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_200_OK
                    },
                    {   # delete sub-org block by id, okay for sub-org admin
                        # itself
                        'test_name':
                            'delete_b5_f0_l1_sub1_o1_by_sub_1_org_1_admin',
                        'args': {'pk': self.blocks['b5_f0_l1_sub1_o1_for_deletion'].id},
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
