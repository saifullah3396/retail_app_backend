"""
Defines the unit tests for organizations applications.
"""
import copy

from core.tests import TestsBase
from django.urls import include, path, reverse
from rest_framework import status


class OrganizationGetTests(TestsBase):
    """
    Defines unit tests for get api for the organizations application.
    """

    """Define the api url patterns used in this test unit."""
    api_urlpatterns = [
        path('organizations/', include('organizations.api.urls')),
    ]

    """Define the the complete url pattern used in this test unit."""
    urlpatterns = [
        path('api/v1/', include(api_urlpatterns)),
    ]

    def setUp(self):
        """
        Sets up the test cases.
        """
        super(OrganizationGetTests, self).setUp()
        self.test = [
            {
                'test_name': 'get_organization_by_id',
                'type': 'get',
                'path_name': 'organizations_retrieve_update_delete',
                'request': [
                    {   # get org by id, okay for staff
                        'test_name': 'get_org_1_by_id_by_staff',
                        'args': [self.orgs['org_1'].id],
                        'user': 'staff_user',
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                data['id'],
                                str(self.orgs['org_1'].id))
                        )
                    },
                    {   # get org by id, okay for org admin itself
                        'test_name': 'get_org_1_by_id_by_org_1_admin',
                        'args': [self.orgs['org_1'].id],
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                data['id'],
                                str(self.orgs['org_1'].id))
                        )
                    },
                    {   # get org by id, forbidden for sub-org
                        'test_name': 'get_org_1_by_id_by_sub_org_1_admin',
                        'args': [self.orgs['org_1'].id],
                        'user': 'sub_org_11_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # get org by id, should return null for other org-admin
                        'test_name': 'get_org_1_by_id_by_org_2_admin',
                        'args': [self.orgs['org_1'].id],
                        'user': 'org_2_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # get org by id, forbidden for employee
                        'test_name': 'get_org_1_by_id_by_employee',
                        'args': [self.orgs['org_1'].id],
                        'user': 'employee_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # get org by id, forbidden for random user
                        'test_name': 'get_org_1_by_id_by_other_user',
                        'args': [self.orgs['org_1'].id],
                        'user': 'other_user',
                        'status': status.HTTP_403_FORBIDDEN
                    }
                ]
            },
            {
                'test_name': 'get_sub_organization_by_id',
                'type': 'get',
                'path_name': 'organizations_retrieve_update_delete',
                'request': [
                    {   # get sub-org by id, okay for staff
                        'test_name': 'get_sub_org_1_by_id_by_staff',
                        'args': [self.orgs['sub_1_org_1'].id],
                        'user': 'staff_user',
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                data['id'],
                                str(self.orgs['sub_1_org_1'].id))
                        )
                    },
                    {   # get sub-org by id, okay for org admin itself under
                        # which this sub-org exists
                        'test_name': 'get_sub_org_1_by_id_by_org_1_admin',
                        'args': [self.orgs['sub_1_org_1'].id],
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                data['id'],
                                str(self.orgs['sub_1_org_1'].id))
                        )
                    },
                    {   # get sub-org by id, okay for sub-org admin itself
                        'test_name': 'get_sub_1_org_1_by_id_by_sub_1_org_1_admin',
                        'args': [self.orgs['sub_1_org_1'].id],
                        'user': 'sub_org_11_admin_user',
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                data['id'],
                                str(self.orgs['sub_1_org_1'].id))
                        )
                    },
                    {   # get sub-org by id, should return null for other
                        # org-admin under which this sub-org does not exist
                        'test_name': 'get_sub_1_org_1_by_id_by_org_2_admin',
                        'args': [self.orgs['sub_1_org_1'].id],
                        'user': 'org_2_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # get sub-org by id, should return null for other
                        # sub-org admin to which this sub-org does not exist
                        'test_name': 'get_sub_1_org_1_by_id_by_sub_1_org_2_admin',
                        'args': [self.orgs['sub_1_org_1'].id],
                        'user': 'sub_org_12_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # get employees own organization info, okay
                        'test_name': 'get_sub_1_org_1_by_id_by_employee',
                        'args': [self.orgs['sub_1_org_1'].id],
                        'user': 'employee_user',
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                data['id'],
                                str(self.orgs['sub_1_org_1'].id))
                        )
                    },
                    {   # use employees to get other organization info, bad
                        'test_name': 'get_sub_1_org_2_by_id_by_employee',
                        'args': [self.orgs['sub_1_org_2'].id],
                        'user': 'employee_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # get sub-org by id, forbidden for random user
                        'test_name': 'get_sub_1_org_1_by_id_by_other_user',
                        'args': [self.orgs['sub_1_org_1'].id],
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
