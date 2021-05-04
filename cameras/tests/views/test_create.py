"""
Defines the unit tests related to 'create' api requests for this application.
"""
from django.urls import include, path
from rest_framework import status

from core.tests import TestsBase


# pylint: disable=pointless-string-statement, invalid-name
class CameraCreateTests(TestsBase):
    """
    Defines unit tests for 'create' api requests for views defined at
    'cameras/' url.
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
        super(CameraCreateTests, self).setUp()
        camera_data = {
            'ip_addr': 'rtsp://192.168.1.1',
            'coords': [0, 0],
            'point_coords_in_frame': [0, 1, 2, 3, 4, 5, 6, 7],
            'point_coords_in_image': [0, 1, 2, 3, 4, 5, 6, 7],
        }

        expected_data = {
            'ip_addr': 'rtsp://192.168.1.1',
            'coords': {"x": 0, "y": 0},
            'point_coords_in_frame': {
                "x1": 0, "y1": 1,
                "x2": 2, "y2": 3,
                "x3": 4, "y3": 5,
                "x4": 6, "y4": 7,
            },
            'point_coords_in_image': {
                "x1": 0, "y1": 1,
                "x2": 2, "y2": 3,
                "x3": 4, "y3": 5,
                "x4": 6, "y4": 7,
            }
        }
        self.test = [
            {
                'test_name': 'create_cameras',
                'type': 'post',
                'path_name': 'cameras_list_create_delete',
                'request': [
                    {   # create camera without any data, bad
                        'test_name': 'create_camera_by_staff_no_data',
                        'data': {},
                        'user': 'staff_user',
                        'status': status.HTTP_400_BAD_REQUEST,
                    },
                    {   # create camera with same data, works since cameras are
                        # not necessarily unique
                        'test_name': 'create_camera_by_staff_duplicate',
                        'data': {
                            **camera_data,
                            'block': self.blocks['b1_f0_l1_o1'].id
                        },
                        'user': 'staff_user',
                        'status': status.HTTP_201_CREATED,
                        'response_check': lambda test, data: (
                            test.assertDictContainsSubset(
                                {
                                    **expected_data,
                                    'block': self.blocks['b1_f0_l1_o1'].id
                                }, data)
                        )
                    },
                    {   # create a new unique camera, okay for staff
                        'test_name': 'create_camera_by_staff',
                        'data': {
                            **camera_data,
                            'block': self.blocks['b1_f0_l1_o1'].id
                        },
                        'user': 'staff_user',
                        'status': status.HTTP_201_CREATED,
                        'response_check': lambda test, data: (
                            test.assertDictContainsSubset(
                                {
                                    **expected_data,
                                    'block': self.blocks['b1_f0_l1_o1'].id
                                }, data)
                        )
                    },
                    {   # create camera by org-admin, okay
                        'test_name': 'create_camera_org_admin_1_in_org_1',
                        'data': {
                            **camera_data,
                            'block': self.blocks['b1_f0_l1_o1'].id
                        },
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_201_CREATED,
                        'response_check': lambda test, data: (
                            test.assertDictContainsSubset(
                                {
                                    **expected_data,
                                    'block': self.blocks['b1_f0_l1_o1'].id
                                }, data)
                        )
                    },
                    {   # create camera by org-admin in lower tree, okay
                        'test_name':
                            'create_camera_org_admin_1_in_sub_1_org_1',
                        'data': {
                            **camera_data,
                            'block': self.blocks['b1_f0_l1_sub1_o1'].id
                        },
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_201_CREATED,
                        'response_check': lambda test, data: (
                            test.assertDictContainsSubset(
                                {
                                    **expected_data,
                                    'block': self.blocks['b1_f0_l1_sub1_o1'].id
                                }, data)
                        )
                    },
                    {   # create camera by org-admin in other organization,
                        # bad
                        'test_name': 'create_camera_org_admin_1_in_org_2',
                        'data': {
                            **camera_data,
                            'block': self.blocks['b1_f0_l1_o2'].id
                        },
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_400_BAD_REQUEST
                    },
                    {   # create camera by sub-org-admin in upper tree, bad
                        'test_name': 'create_camera_sub_org_admin_1_in_org_1',
                        'data': {
                            **camera_data,
                            'block': self.blocks['b1_f0_l1_o1'].id
                        },
                        'user': 'sub_org_11_admin_user',
                        'status': status.HTTP_400_BAD_REQUEST
                    },
                    {   # create camera by sub-org-admin in own tree, okay
                        'test_name':
                            'create_camera_sub_org_admin_1_in_sub_1_org_1',
                        'data': {
                            **camera_data,
                            'block': self.blocks['b1_f0_l1_sub1_o1'].id
                        },
                        'user': 'sub_org_11_admin_user',
                        'status': status.HTTP_201_CREATED,
                        'response_check': lambda test, data: (
                            test.assertDictContainsSubset(
                                {
                                    **expected_data,
                                    'block': self.blocks['b1_f0_l1_sub1_o1'].id
                                }, data)
                        )
                    },
                    {   # create camera by employee user, forbidden
                        'test_name': 'create_camera_employee_user',
                        'data': {
                            **camera_data,
                            'block': self.blocks['b1_f0_l1_sub1_o1'].id
                        },
                        'user': 'employee_user',
                        'status': status.HTTP_403_FORBIDDEN
                    },
                    {   # create camera by random user, forbidden
                        'test_name': 'create_camera_other_user',
                        'data': {
                            **camera_data,
                            'block': self.blocks['b1_f0_l1_sub1_o1'].id
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
