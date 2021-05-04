"""
Defines the unit tests related to 'delete' api requests for this application.
"""

from django.urls import include, path
from rest_framework import status

from core.tests import TestsBase


# pylint: disable=pointless-string-statement, line-too-long, invalid-name
class CameraDeleteTests(TestsBase):
    """
    Defines unit tests for 'delete' api requests for views defined
    at 'locations/' url.
    """

    """Define the api url patterns used in this test unit."""
    api_urlpatterns = [
        path('cameras/', include('cameras.api.urls')),
    ]

    """Define the the complete url pattern used in this test unit."""
    urlpatterns = [
        path('api/v1/', include(api_urlpatterns)),
    ]

    def setUp(self):
        """
        Sets up the test cases.
        """
        super(CameraDeleteTests, self).setUp()
        self.test = [
            {
                'test_name': 'delete_camera_by_id',
                'type': 'delete',
                'path_name': 'cameras_retrieve_update_delete',
                'request': [
                    {
                        # delete c5_del_b1_f0_l1_o1 by staff
                        'test_name': 'delete_c5_del_b1_f0_l1_o1_staff',
                        'args': {'pk': self.cameras['c5_del_b1_f0_l1_o1'].id},
                        'user': 'staff_user',
                        'status': status.HTTP_200_OK
                    },
                    {   # delete c4_del_b1_f0_l1_o1 by org 1 admin
                        'test_name': 'delete_c4_del_b1_f0_l1_o1_by_org1_admin',
                        'args': {'pk': self.cameras['c4_del_b1_f0_l1_o1'].id},
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_200_OK
                    },
                    {   # delete camera in higher level organization,
                        'test_name':
                            'delete_c3_del_b1_f0_l1_o1_by_sub_1_org_1_admin',
                        'args': {'pk': self.cameras['c3_del_b1_f0_l1_o1'].id},
                        'user': 'sub_org_11_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # delete camera of different org, bad (location 1 is in
                        # org 1)
                        'test_name': 'delete_c3_del_b1_f0_l1_o1_by_org_2_admin',
                        'args': {'pk': self.cameras['c3_del_b1_f0_l1_o1'].id},
                        'user': 'org_2_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # delete camera in org by id, forbidden for employee
                        'test_name':
                            'delete_c3_del_b1_f0_l1_o1_by_sub_org_1_'
                            'employee',
                        'args': {'pk': self.cameras['c3_del_b1_f0_l1_o1'].id},
                        'user': 'employee_user',
                        'status': status.HTTP_403_FORBIDDEN
                    },
                    {   # delete camera by id, forbidden for random user
                        'test_name':
                            'delete_c3_del_b1_f0_l1_o1_by_other_user',
                        'args': {'pk': self.cameras['c3_del_b1_f0_l1_o1'].id},
                        'user': 'other_user',
                        'status': status.HTTP_403_FORBIDDEN
                    }
                ]
            },
            {
                'test_name': 'delete_sub_camera_by_id',
                'type': 'delete',
                'path_name': 'cameras_retrieve_update_delete',
                'request': [
                    {   # delete sub-org camera by id, okay for staff
                        'test_name':
                            'delete_c5_del_b1_f0_l1_sub1_o1_by_staff_user',
                        'args': {'pk': self.cameras['c5_del_b1_f0_l1_sub1_o1'].id},
                        'user': 'staff_user',
                        'status': status.HTTP_200_OK
                    },
                    {   # delete sub-org camera by id, okay for org admin itself under
                        # which this sub-org exists
                        'test_name':
                            'delete_c4_del_b1_f0_l1_sub1_o1_by_org_1_admin',
                        'args': {'pk': self.cameras['c4_del_b1_f0_l1_sub1_o1'].id},
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_200_OK
                    },
                    {   # delete sub-org camera by id, okay for sub-org admin
                        # itself
                        'test_name':
                            'delete_c3_del_b1_f0_l1_sub1_o1_by_sub_1_org_1_admin',
                        'args': {'pk': self.cameras['c3_del_b1_f0_l1_sub1_o1'].id},
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
