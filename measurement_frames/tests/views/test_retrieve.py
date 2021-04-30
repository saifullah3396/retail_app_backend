"""
Defines the unit tests related to 'retrieve' api requests for this application.
"""

from django.urls import include, path
from rest_framework import status

from core.tests import TestsBase


# pylint: disable=pointless-string-statement
class FrameRetrieveTests(TestsBase):
    """
    Defines unit tests for 'retrieve' api requests for views defined
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
        super(FrameRetrieveTests, self).setUp()
        self.test = [
            {
                'test_name': 'get_frame_by_id',
                'type': 'get',
                'path_name': 'frames_retrieve_update_delete',
                'request': [
                    {   # get frame by id, okay for staff
                        'test_name': 'get_mf0_b1_f0_l1_o1_by_staff',
                        'args': {'pk': self.frames['mf0_b1_f0_l1_o1'].id},
                        'user': 'staff_user',
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                data.get('id', None),
                                str(self.frames['mf0_b1_f0_l1_o1'].id))
                        )
                    },
                    {   # get frame by id, okay for org admin itself
                        'test_name': 'get_mf0_b1_f0_l1_o1_by_org_1_admin',
                        'args': {'pk': self.frames['mf0_b1_f0_l1_o1'].id},
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                data.get('id', None),
                                str(self.frames['mf0_b1_f0_l1_o1'].id))
                        )
                    },
                    {   # get frame of org, forbidden for sub-org admin
                        'test_name': 'get_mf0_b1_f0_l1_o1_by_sub_org_1_admin',
                        'args': {'pk': self.frames['mf0_b1_f0_l1_o1'].id},
                        'user': 'sub_org_11_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # get frame, bad for other org-admin
                        'test_name': 'get_mf0_b1_f0_l1_o1_by_org_2_admin',
                        'args': {'pk': self.frames['mf0_b1_f0_l1_o1'].id},
                        'user': 'org_2_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # get frame by id, forbidden for random user
                        'test_name': 'get_mf0_b1_f0_l1_o1_by_other_user',
                        'args': {'pk': self.frames['mf0_b1_f0_l1_o1'].id},
                        'user': 'other_user',
                        'status': status.HTTP_403_FORBIDDEN
                    },
                ]
            },
            {
                'test_name': 'get_sub_frame_by_id',
                'type': 'get',
                'path_name': 'frames_retrieve_update_delete',
                'request': [
                    {   # get sub-org frame by id, okay for staff
                        'test_name': 'get_mf0_b1_f0_l1_sub1_o1_by_staff',
                        'args': {'pk': self.frames['mf0_b1_f0_l1_sub1_o1'].id},
                        'user': 'staff_user',
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                data.get('id', None),
                                str(
                                    self.frames[
                                        'mf0_b1_f0_l1_sub1_o1'].id))
                        )
                    },
                    {   # get sub-org frame by id, okay for org admin itself
                        # under which this sub-org exists
                        'test_name':
                            'get_mf0_b1_f0_l1_sub1_o1_by_org_1_admin',
                        'args': {'pk': self.frames['mf0_b1_f0_l1_sub1_o1'].id},
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                data.get('id', None),
                                str(
                                    self.frames[
                                        'mf0_b1_f0_l1_sub1_o1'].id))
                        )
                    },
                    {   # get sub-org frame by id, okay for sub-org admin
                        # itself
                        'test_name':
                            'get_mf0_b1_f0_l1_sub1_o1_by_sub_1_org_1_admin',
                        'args': {'pk': self.frames['mf0_b1_f0_l1_sub1_o1'].id},
                        'user': 'sub_org_11_admin_user',
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                data.get('id', None),
                                str(
                                    self.frames[
                                        'mf0_b1_f0_l1_sub1_o1'].id))
                        )
                    },
                    {   # get sub-org frame by id, bad for other
                        # org-admin under which this sub-org does not exist
                        'test_name':
                            'get_mf0_b1_f0_l1_sub1_o1_by_org_2_admin',
                        'args': {'pk': self.frames['mf0_b1_f0_l1_sub1_o1'].id},
                        'user': 'org_2_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # get sub-org frame by id, bad for other
                        # sub-org admin to which this sub-org does not exist
                        'test_name':
                            'get_mf0_b1_f0_l1_sub1_o1_by_sub_1_org_2_admin',
                        'args': {'pk': self.frames['mf0_b1_f0_l1_sub1_o1'].id},
                        'user': 'sub_org_12_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # get sub-org frame by id, okay for staff who is in
                        # this org
                        'test_name': 'get_mf0_b1_f0_l1_sub1_o1_by_employee',
                        'args': {'pk': self.frames['mf0_b1_f0_l1_sub1_o1'].id},
                        'user': 'employee_user',
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                data.get('id', None),
                                str(self.frames[
                                    'mf0_b1_f0_l1_sub1_o1'].id))
                        )
                    },
                    {   # get sub-org by id, forbidden for random user
                        'test_name': 'get_mf0_b1_f0_l1_o2_by_other_user',
                        'args': {'pk': self.frames['mf0_b1_f0_l1_o2'].id},
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
