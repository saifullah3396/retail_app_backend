"""
Defines the unit tests related to 'delete-by-id-list' api requests for this
application.
"""

from django.urls import include, path
from rest_framework import status

from core.tests import TestsBase


# pylint: disable=pointless-string-statement
class FrameDeleteByIdListTests(TestsBase):
    """
    Defines unit tests for 'delete-by-id-list' api requests for views defined
    at 'blocks/' url.
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
        super(FrameDeleteByIdListTests, self).setUp()
        self.test = [
            {
                'test_name': 'delete_multiple_frames',
                'type': 'delete',
                'path_name': 'frames_list_create_delete',
                'request': [
                    # {   # delete frame, okay for staff but bad because its
                    #     # protected
                    #     'test_name': 'delete_frame_by_staff',
                    #     'query_params': [
                    #         ('id', self.frames['mf0_b1_f0_l1_o1'].id),
                    #     ],
                    #     'user': 'staff_user',
                    #     'status': status.HTTP_400_BAD_REQUEST
                    # },
                    {   # delete frame by org-admin in other organization,
                        # bad
                        'test_name': 'delete_frame_org_admin_1_in_org_2',
                        'query_params': [
                            ('id', self.frames['mf0_b1_f0_l1_o2'].id),
                            ('id', self.frames['mf1_b1_f0_l1_o2'].id),
                        ],
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # delete frame by org-admin in other organization
                        # lower tree, bad
                        'test_name':
                            'delete_frame_org_admin_1_in_sub_1_org_2',
                        'query_params': [
                            ('id', self.frames['mf0_b1_f0_l1_sub1_o2'].id),
                            ('id', self.frames['mf1_b1_f0_l1_sub1_o2'].id),
                        ],
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # delete frame by sub-org-admin in upper tree, bad
                        'test_name': 'delete_frame_sub_org_admin_1_in_org_1',
                        'query_params': [
                            ('id', self.frames['mf0_b1_f0_l1_o1'].id),
                            ('id', self.frames['mf1_b1_f0_l1_o1'].id),
                        ],
                        'user': 'sub_org_11_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # delete frame by employee user, forbidden
                        'test_name': 'delete_frame_other_user',
                        'query_params': [
                            ('id', self.frames['mf0_b1_f0_l1_sub1_o1'].id),
                            ('id', self.frames['mf1_b1_f0_l1_sub1_o1'].id),
                        ],
                        'user': 'employee_user',
                        'status': status.HTTP_403_FORBIDDEN
                    },
                    {   # delete frame by random user, forbidden
                        'test_name': 'delete_frame_other_user',
                        'query_params': [
                            ('id', self.frames['mf0_b1_f0_l1_sub1_o1'].id),
                            ('id', self.frames['mf1_b1_f0_l1_sub1_o1'].id),
                        ],
                        'user': 'other_user',
                        'status': status.HTTP_403_FORBIDDEN
                    },
                    {   # delete frame, okay for staff
                        'test_name': 'delete_frame_by_staff',
                        'query_params': [
                            ('id', self.frames['mf2_del_b1_f0_l1_o1'].id),
                            ('id', self.frames['mf3_del_b1_f0_l1_o1'].id),
                        ],
                        'user': 'staff_user',
                        'status': status.HTTP_200_OK
                    },
                    {   # duplicate delete by staff, bad
                        'test_name': 'delete_dup_frame_by_staff',
                        'query_params': [
                            ('id', self.frames['mf2_del_b1_f0_l1_o1'].id),
                            ('id', self.frames['mf3_del_b1_f0_l1_o1'].id),
                        ],
                        'user': 'staff_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # delete frame by org-admin, okay
                        'test_name': 'delete_frame_org_admin_1_in_org_1',
                        'query_params': [
                            ('id', self.frames['mf4_del_b1_f0_l1_o1'].id),
                            ('id', self.frames['mf5_del_b1_f0_l1_o1'].id),
                        ],
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_200_OK
                    },
                    {   # delete frame by org-admin in lower tree, okay
                        'test_name':
                            'delete_frame_org_admin_1_in_sub_1_org_1',
                        'query_params': [
                            ('id', self.frames['mf2_del_b1_f0_l1_sub1_o1'].id),
                            ('id', self.frames['mf3_del_b1_f0_l1_sub1_o1'].id),
                        ],
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_200_OK
                    },
                    {   # delete frame by sub-org-admin in own tree, okay
                        'test_name':
                            'delete_frame_sub_org_admin_2_in_sub_1_org_2',
                        'query_params': [
                            ('id', self.frames['mf4_del_b1_f0_l1_sub1_o1'].id),
                            ('id', self.frames['mf5_del_b1_f0_l1_sub1_o1'].id),
                        ],
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
