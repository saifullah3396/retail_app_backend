"""
Defines the unit tests related to 'retrieve' api requests for this application.
"""

from django.urls import include, path
from rest_framework import status

from core.tests import TestsBase


# pylint: disable=pointless-string-statement
class CameraRetrieveTests(TestsBase):
    """
    Defines unit tests for 'retrieve' api requests for views defined
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
        super(CameraRetrieveTests, self).setUp()
        camera_data = {
            'ip_addr': 'rtsp://192.168.1.2',
            'coords': [1, 1],
            'point_coords_in_frame': [1, 1, 1, 1, 1, 1, 1, 1],
            'point_coords_in_image': [1, 1, 1, 1, 1, 1, 1, 1],
        }

        expected_data = {
            'ip_addr': 'rtsp://192.168.1.2',
            'coords': {"x": 1, "y": 1},
            'point_coords_in_frame': {
                "x1": 1, "y1": 1,
                "x2": 1, "y2": 1,
                "x3": 1, "y3": 1,
                "x4": 1, "y4": 1,
            },
            'point_coords_in_image': {
                "x1": 1, "y1": 1,
                "x2": 1, "y2": 1,
                "x3": 1, "y3": 1,
                "x4": 1, "y4": 1,
            }
        }
        self.test = [
            {
                'test_name': 'update_camera_by_id',
                'type': 'patch',
                'path_name': 'cameras_retrieve_update_delete',
                'request': [
                    {   # update camera by id. change block to another block with
                        # existing camera name, works but block id remains unchanged
                        'test_name': 'change_c0_block',
                        'args': {'pk': self.cameras['c0_b1_f0_l1_o1'].id},
                        'user': 'staff_user',
                        'data': {
                            'block': self.blocks['b2_f0_l1_o1'].id
                        },
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertDictContainsSubset(
                                {
                                    'block': self.blocks['b1_f0_l1_o1'].id
                                }, data)
                        )
                    },
                    {   # update camera by id, okay for staff
                        'test_name': 'update_c0_b1_f0_l1_o1_by_staff',
                        'args': {'pk': self.cameras['c0_b1_f0_l1_o1'].id},
                        'user': 'staff_user',
                        'data': {
                            **camera_data,
                            'block': self.blocks['b1_f0_l1_o1'].id
                        },
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertDictContainsSubset(
                                {
                                    **expected_data,
                                    'block': self.blocks['b1_f0_l1_o1'].id
                                }, data)
                        )
                    },
                    {   # update camera by id, okay for org_1_admin
                        'test_name': 'update_c0_b1_f0_l1_o1_by_org_1_admin',
                        'args': {'pk': self.cameras['c0_b1_f0_l1_o1'].id},
                        'user': 'org_1_admin_user',
                        'data': {
                            **camera_data,
                            'block': self.blocks['b1_f0_l1_o1'].id
                        },
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertDictContainsSubset(
                                {
                                    **expected_data,
                                    'block': self.blocks['b1_f0_l1_o1'].id
                                }, data)
                        )
                    },
                    {   # update camera of org, forbidden for sub-org admin
                        'test_name': 'update_c0_b1_f0_l1_o1_by_sub_org_1_admin',
                        'args': {'pk': self.cameras['c0_b1_f0_l1_o1'].id},
                        'user': 'sub_org_11_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # update camera, bad for other org-admin
                        'test_name': 'update_c0_b1_f0_l1_o1_by_org_2_admin',
                        'args': {'pk': self.cameras['c0_b1_f0_l1_o1'].id},
                        'user': 'org_2_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # update camera by id, forbidden for random user
                        'test_name': 'update_c0_b1_f0_l1_o1_by_other_user',
                        'args': {'pk': self.cameras['c0_b1_f0_l1_o1'].id},
                        'user': 'other_user',
                        'status': status.HTTP_403_FORBIDDEN
                    },
                ]
            },
            {
                'test_name': 'update_sub_camera_by_id',
                'type': 'patch',
                'path_name': 'cameras_retrieve_update_delete',
                'request': [
                    {   # update sub-org camera by id, okay for staff
                        'test_name': 'update_c0_b1_f0_l1_sub1_o1_by_staff',
                        'args': {'pk': self.cameras['c0_b1_f0_l1_sub1_o1'].id},
                        'user': 'staff_user',
                        'data': {
                            **camera_data,
                        },
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertDictContainsSubset(
                                {
                                    **expected_data,
                                }, data)
                        )
                    },
                    {   # update sub-org camera by id, okay for org admin itself
                        # under which this sub-org exists
                        'test_name':
                            'update_c0_b1_f0_l1_sub1_o1_by_org_1_admin',
                        'args': {'pk': self.cameras['c0_b1_f0_l1_sub1_o1'].id},
                        'user': 'org_1_admin_user',
                        'data': {
                            **camera_data,
                        },
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertDictContainsSubset(
                                {
                                    **expected_data,
                                }, data)
                        )
                    },
                    {   # update sub-org camera by id, okay for sub-org admin
                        # itself
                        'test_name':
                            'update_c0_b1_f0_l1_sub1_o1_by_sub_1_org_1_admin',
                        'args': {'pk': self.cameras['c0_b1_f0_l1_sub1_o1'].id},
                        'user': 'sub_org_11_admin_user',
                        'data': {
                            **camera_data,
                        },
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertDictContainsSubset(
                                {
                                    **expected_data,
                                }, data)
                        )
                    },
                    {   # update sub-org camera by id, bad for other
                        # org-admin under which this sub-org does not exist
                        'test_name':
                            'update_c0_b1_f0_l1_sub1_o1_by_org_2_admin',
                        'args': {'pk': self.cameras['c0_b1_f0_l1_sub1_o1'].id},
                        'data': {
                            **camera_data,
                        },
                        'user': 'org_2_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # update sub-org camera by id, bad for other
                        # sub-org admin to which this sub-org does not exist
                        'test_name':
                            'update_c0_b1_f0_l1_sub1_o1_by_sub_1_org_2_admin',
                        'args': {'pk': self.cameras['c0_b1_f0_l1_sub1_o1'].id},
                        'data': {
                            **camera_data,
                        },
                        'user': 'sub_org_12_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # update sub-org camera by id, forbidden for employees
                        'test_name': 'update_c0_b1_f0_l1_sub1_o1_by_employee',
                        'args': {'pk': self.cameras['c0_b1_f0_l1_sub1_o1'].id},
                        'user': 'employee_user',
                        'data': {
                            **camera_data,
                        },
                        'status': status.HTTP_403_FORBIDDEN,
                    },
                    {   # update sub-org by id, forbidden for random user
                        'test_name': 'update_c0_b1_f0_l1_o1_by_other_user',
                        'args': {'pk': self.cameras['c0_b1_f0_l1_o1'].id},
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
