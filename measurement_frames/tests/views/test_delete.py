"""
Defines the unit tests related to 'delete' api requests for this application.
"""

from django.urls import include, path
from rest_framework import status

from core.tests import TestsBase


# pylint: disable=pointless-string-statement, line-too-long, invalid-name
class FrameDeleteTests(TestsBase):
    """
    Defines unit tests for 'delete' api requests for views defined
    at 'locations/' url.
    """

    """Define the api url patterns used in this test unit."""
    api_urlpatterns = [
        path('frames/', include('measurement_frames.api.urls')),
    ]

    """Define the the complete url pattern used in this test unit."""
    urlpatterns = [
        path('api/v1/', include(api_urlpatterns)),
    ]

    def setUp(self):
        """
        Sets up the test cases.
        """
        super(FrameDeleteTests, self).setUp()
        self.test = [
            {
                'test_name': 'delete_frame_by_id',
                'type': 'delete',
                'path_name': 'frames_retrieve_update_delete',
                'request': [
                    {
                        # delete mf5_del_b1_f0_l1_o1 by staff
                        'test_name': 'delete_mf5_del_b1_f0_l1_o1_staff',
                        'args': {'pk': self.frames['mf5_del_b1_f0_l1_o1'].id},
                        'user': 'staff_user',
                        'status': status.HTTP_200_OK
                    },
                    {   # delete mf4_del_b1_f0_l1_o1 by org 1 admin
                        'test_name': 'delete_mf4_del_b1_f0_l1_o1_by_org1_admin',
                        'args': {'pk': self.frames['mf4_del_b1_f0_l1_o1'].id},
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_200_OK
                    },
                    {   # delete frame in higher level organization,
                        'test_name':
                            'delete_mf3_del_b1_f0_l1_o1_by_sub_1_org_1_admin',
                        'args': {'pk': self.frames['mf3_del_b1_f0_l1_o1'].id},
                        'user': 'sub_org_11_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # delete frame of different org, bad (location 1 is in
                        # org 1)
                        'test_name': 'delete_mf3_del_b1_f0_l1_o1_by_org_2_admin',
                        'args': {'pk': self.frames['mf3_del_b1_f0_l1_o1'].id},
                        'user': 'org_2_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # delete frame in org by id, forbidden for employee
                        'test_name':
                            'delete_mf3_del_b1_f0_l1_o1_by_sub_org_1_'
                            'employee',
                        'args': {'pk': self.frames['mf3_del_b1_f0_l1_o1'].id},
                        'user': 'employee_user',
                        'status': status.HTTP_403_FORBIDDEN
                    },
                    {   # delete frame by id, forbidden for random user
                        'test_name':
                            'delete_mf3_del_b1_f0_l1_o1_by_other_user',
                        'args': {'pk': self.frames['mf3_del_b1_f0_l1_o1'].id},
                        'user': 'other_user',
                        'status': status.HTTP_403_FORBIDDEN
                    }
                ]
            },
            {
                'test_name': 'delete_sub_frame_by_id',
                'type': 'delete',
                'path_name': 'frames_retrieve_update_delete',
                'request': [
                    {   # delete sub-org frame by id, okay for staff
                        'test_name':
                            'delete_mf5_del_b1_f0_l1_sub1_o1_by_staff_user',
                        'args': {'pk': self.frames['mf5_del_b1_f0_l1_sub1_o1'].id},
                        'user': 'staff_user',
                        'status': status.HTTP_200_OK
                    },
                    {   # delete sub-org frame by id, okay for org admin itself under
                        # which this sub-org exists
                        'test_name':
                            'delete_mf4_del_b1_f0_l1_sub1_o1_by_org_1_admin',
                        'args': {'pk': self.frames['mf4_del_b1_f0_l1_sub1_o1'].id},
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_200_OK
                    },
                    {   # delete sub-org frame by id, okay for sub-org admin
                        # itself
                        'test_name':
                            'delete_mf3_del_b1_f0_l1_sub1_o1_by_sub_1_org_1_admin',
                        'args': {'pk': self.frames['mf3_del_b1_f0_l1_sub1_o1'].id},
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
