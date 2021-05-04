"""
Defines the unit tests related to 'create' api requests for this application.
"""
from django.urls import include, path
from rest_framework import status

from core.tests import TestsBase


# pylint: disable=pointless-string-statement
class FrameCreateTests(TestsBase):
    """
    Defines unit tests for 'create' api requests for views defined at
    'frames/' url.
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
        super(FrameCreateTests, self).setUp()
        self.test = [
            {
                'test_name': 'create_frames',
                'type': 'post',
                'path_name': 'frames_list_create_delete',
                'request': [
                    {   # create frame without any data, bad
                        'test_name': 'create_frame_by_staff_no_data',
                        'data': {},
                        'user': 'staff_user',
                        'status': status.HTTP_400_BAD_REQUEST,
                    },
                    {   # create frame, okay for staff but error since frame 0
                        # already exists in this block
                        'test_name': 'create_frame_by_staff_not_unique',
                        'data': {
                            'name': "mf0",
                            'pixel_pose_x': 200,
                            'pixel_pose_y': 100,
                            'pixel_pose_theta': 90,
                            'block': self.blocks['b1_f0_l1_o1'].id
                        },
                        'user': 'staff_user',
                        'status': status.HTTP_400_BAD_REQUEST,
                    },
                    {   # create a new unique frame, okay for staff
                        'test_name': 'create_frame_by_staff',
                        'data': {
                            'name': "create_frame_by_staff",
                            'pixel_pose_x': 200,
                            'pixel_pose_y': 100,
                            'pixel_pose_theta': 90,
                            'block': self.blocks['b1_f0_l1_o1'].id
                        },
                        'user': 'staff_user',
                        'status': status.HTTP_201_CREATED,
                        'response_check': lambda test, data: (
                            test.assertDictContainsSubset(
                                {
                                    'name': "create_frame_by_staff",
                                    'pixel_pose_x': 200,
                                    'pixel_pose_y': 100,
                                    'pixel_pose_theta': 90,
                                    'block': self.blocks['b1_f0_l1_o1'].id
                                }, data)
                        )
                    },
                    {   # create frame by org-admin, okay
                        'test_name': 'create_frame_org_admin_1_in_org_1',
                        'data': {
                            'name': "create_frame_org_admin_1_in_org_1",
                            'pixel_pose_x': 200,
                            'pixel_pose_y': 100,
                            'pixel_pose_theta': 90,
                            'block': self.blocks['b1_f0_l1_o1'].id
                        },
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_201_CREATED,
                        'response_check': lambda test, data: (
                            test.assertDictContainsSubset(
                                {
                                    'name': "create_frame_org_admin_1_in_org_1",
                                    'pixel_pose_x': 200,
                                    'pixel_pose_y': 100,
                                    'pixel_pose_theta': 90,
                                    'block': self.blocks['b1_f0_l1_o1'].id
                                }, data)
                        )
                    },
                    {   # create frame by org-admin in lower tree, okay
                        'test_name':
                            'create_frame_org_admin_1_in_sub_1_org_1',
                        'data': {
                            'name': "create_frame_org_admin_1_in_sub_1_org_1",
                            'pixel_pose_x': 200,
                            'pixel_pose_y': 100,
                            'pixel_pose_theta': 90,
                            'block': self.blocks['b1_f0_l1_sub1_o1'].id
                        },
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_201_CREATED,
                        'response_check': lambda test, data: (
                            test.assertDictContainsSubset(
                                {
                                    'name': "create_frame_org_admin_1_in_sub_1_org_1",
                                    'pixel_pose_x': 200,
                                    'pixel_pose_y': 100,
                                    'pixel_pose_theta': 90,
                                    'block': self.blocks['b1_f0_l1_sub1_o1'].id
                                }, data)
                        )
                    },
                    {   # create frame by org-admin in other organization,
                        # bad
                        'test_name': 'create_frame_org_admin_1_in_org_2',
                        'data': {
                            'name': "create_frame_org_admin_1_in_org_2",
                            'pixel_pose_x': 200,
                            'pixel_pose_y': 100,
                            'pixel_pose_theta': 90,
                            'block': self.blocks['b1_f0_l1_o2'].id
                        },
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_400_BAD_REQUEST
                    },
                    {   # create frame by sub-org-admin in upper tree, bad
                        'test_name': 'create_frame_sub_org_admin_1_in_org_1',
                        'data': {
                            'name': "create_frame_sub_org_admin_1_in_org_1",
                            'pixel_pose_x': 200,
                            'pixel_pose_y': 100,
                            'pixel_pose_theta': 90,
                            'block': self.blocks['b1_f0_l1_o1'].id
                        },
                        'user': 'sub_org_11_admin_user',
                        'status': status.HTTP_400_BAD_REQUEST
                    },
                    {   # create frame by sub-org-admin in own tree, okay
                        'test_name':
                            'create_frame_sub_org_admin_1_in_sub_1_org_1',
                        'data': {
                            'name': "create_frame_sub_org_admin_1_in_sub_1_org_1",
                            'pixel_pose_x': 200,
                            'pixel_pose_y': 100,
                            'pixel_pose_theta': 90,
                            'block': self.blocks['b1_f0_l1_sub1_o1'].id
                        },
                        'user': 'sub_org_11_admin_user',
                        'status': status.HTTP_201_CREATED,
                        'response_check': lambda test, data: (
                            test.assertDictContainsSubset(
                                {
                                    'name': "create_frame_sub_org_admin_1_in_sub_1_org_1",
                                    'pixel_pose_x': 200,
                                    'pixel_pose_y': 100,
                                    'pixel_pose_theta': 90,
                                    'block': self.blocks['b1_f0_l1_sub1_o1'].id
                                }, data)
                        )
                    },
                    {   # create frame by employee user, forbidden
                        'test_name': 'create_frame_employee_user',
                        'data': {
                            'name': "create_frame_employee_user",
                            'pixel_pose_x': 200,
                            'pixel_pose_y': 100,
                            'pixel_pose_theta': 90,
                            'block': self.blocks['b1_f0_l1_sub1_o1'].id
                        },
                        'user': 'employee_user',
                        'status': status.HTTP_403_FORBIDDEN
                    },
                    {   # create frame by random user, forbidden
                        'test_name': 'create_frame_other_user',
                        'data': {
                            'name': "create_frame_other_user",
                            'pixel_pose_x': 200,
                            'pixel_pose_y': 100,
                            'pixel_pose_theta': 90,
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
