"""
Defines the unit tests related to 'delete' api requests for this application.
"""

from django.urls import include, path
from rest_framework import status

from core.tests import TestsBase


# pylint: disable=pointless-string-statement, invalid-names, line-too-long
class DSDeleteTests(TestsBase):
    """
    Defines unit tests for 'delete' api requests for views defined
    at 'locations/' url.
    """

    """Define the api url patterns used in this test unit."""
    api_urlpatterns = [
        path('deepstream_servers/', include('deepstream_servers.api.urls')),
    ]

    """Define the the complete url pattern used in this test unit."""
    urlpatterns = [
        path('api/v1/', include(api_urlpatterns)),
    ]

    def setUp(self):
        """
        Sets up the test cases.
        """
        super(DSDeleteTests, self).setUp()
        self.test = [
            {
                'test_name': 'delete_deepstream_server_by_id',
                'type': 'delete',
                'path_name': 'deepstream_servers_retrieve_update_delete',
                'request': [
                    {
                        # delete ds5_del_o1 by staff
                        'test_name': 'delete_ds5_del_o1_staff',
                        'args': {'pk': self.deepstream_servers['ds5_del_o1'].id},
                        'user': 'staff_user',
                        'status': status.HTTP_200_OK
                    },
                    {   # delete ds4_del_o1 by org 1 admin
                        'test_name': 'delete_ds4_del_o1_by_org1_admin',
                        'args': {'pk': self.deepstream_servers['ds4_del_o1'].id},
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_200_OK
                    },
                    {   # delete deepstream_server in higher level organization,
                        'test_name':
                            'delete_ds3_del_o1_by_sub_1_org_1_admin',
                        'args': {'pk': self.deepstream_servers['ds3_del_o1'].id},
                        'user': 'sub_org_11_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # delete deepstream_server of different org, bad (location 1 is in
                        # org 1)
                        'test_name': 'delete_ds3_del_o1_by_org_2_admin',
                        'args': {'pk': self.deepstream_servers['ds3_del_o1'].id},
                        'user': 'org_2_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # delete deepstream_server in org by id, forbidden for employee
                        'test_name':
                            'delete_ds3_del_o1_by_sub_org_1_'
                            'employee',
                        'args': {'pk': self.deepstream_servers['ds3_del_o1'].id},
                        'user': 'employee_user',
                        'status': status.HTTP_403_FORBIDDEN
                    },
                    {   # delete deepstream_server by id, forbidden for random user
                        'test_name':
                            'delete_ds3_del_o1_by_other_user',
                        'args': {'pk': self.deepstream_servers['ds3_del_o1'].id},
                        'user': 'other_user',
                        'status': status.HTTP_403_FORBIDDEN
                    }
                ]
            },
            {
                'test_name': 'delete_sub_deepstream_server_by_id',
                'type': 'delete',
                'path_name': 'deepstream_servers_retrieve_update_delete',
                'request': [
                    {   # delete sub-org deepstream_server by id, okay for staff
                        'test_name':
                            'delete_ds5_del_sub1_o1_by_staff_user',
                        'args': {'pk': self.deepstream_servers['ds5_del_sub1_o1'].id},
                        'user': 'staff_user',
                        'status': status.HTTP_200_OK
                    },
                    {   # delete sub-org deepstream_server by id, okay for org admin itself under
                        # which this sub-org exists
                        'test_name':
                            'delete_ds4_del_sub1_o1_by_org_1_admin',
                        'args': {'pk': self.deepstream_servers['ds4_del_sub1_o1'].id},
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_200_OK
                    },
                    {   # delete sub-org deepstream_server by id, okay for sub-org admin
                        # itself
                        'test_name':
                            'delete_ds3_del_sub1_o1_by_sub_1_org_1_admin',
                        'args': {'pk': self.deepstream_servers['ds3_del_sub1_o1'].id},
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
