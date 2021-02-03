"""
Defines the unit tests for organizations applications.
"""
import copy

from core.tests import TestsBase
from django.urls import include, path, reverse
from rest_framework import status


class OrganizationUpdateTests(TestsBase):
    """
    Defines unit tests for update api for the organizations application.
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
        super(OrganizationUpdateTests, self).setUp()
        self.test = [
            {
                'test_name': 'update_organization_by_id',
                'type': 'patch',
                'path_name': 'organizations_retrieve_update_delete',
                'request': [
                    {   # update org by id, okay for staff
                        'test_name': 'update_org_1_by_id_by_staff',
                        'args': [self.orgs['org_1'].id],
                        'user': 'staff_user',
                        'data': {
                            'name': 'test_1_org_1_updated',
                            'desc': 'test_1_org_1_desc_updated',
                        },
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                data['id'],
                                str(self.orgs['org_1'].id)) and
                            test.assertEqual(
                                data['name'], 'test_1_org_1_updated')
                        )
                    },
                    {   # update org by id, okay for org admin itself
                        'test_name': 'update_org_1_by_id_by_org_1_admin',
                        'args': [self.orgs['org_1'].id],
                        'user': 'org_1_admin_user',
                        'data': {
                            'name': 'test_2_org_1_updated',
                            'desc': 'test_2_org_1_desc_updated',
                        },
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                data['id'],
                                str(self.orgs['org_1'].id)) and
                            test.assertEqual(
                                data['name'], 'test_2_org_1_updated')
                        )
                    },
                    {   # update org by id, sub-org admin has no access to it
                        'test_name': 'update_org_1_by_id_by_sub_1_org_1_admin',
                        'args': [self.orgs['org_1'].id],
                        'user': 'sub_org_11_admin_user',
                        'data': {
                            'name': 'test_3_org_1_updated',
                            'desc': 'test_3_org_1_desc_updated',
                        },
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # update org by id, should return null for other
                        # org-admin
                        'test_name': 'update_org_1_by_id_by_org_2_admin',
                        'args': [self.orgs['org_1'].id],
                        'user': 'org_2_admin_user',
                        'data': {
                            'name': 'test_4_org_1_updated',
                            'desc': 'test_4_org_1_desc_updated',
                        },
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # update org by id, forbidden for employee
                        'test_name': 'update_org_1_by_id_by_employee',
                        'args': [self.orgs['org_1'].id],
                        'user': 'employee_user',
                        'data': {
                            'name': 'test_5_org_1_updated',
                            'desc': 'test_5_org_1_desc_updated',
                        },
                        'status': status.HTTP_403_FORBIDDEN
                    },
                    {   # update org by id, forbidden for random user
                        'test_name': 'update_org_1_by_id_by_other_user',
                        'args': [self.orgs['org_1'].id],
                        'user': 'other_user',
                        'data': {
                            'name': 'test_6_org_1_updated',
                            'desc': 'test_6_org_1_desc_updated',
                        },
                        'status': status.HTTP_403_FORBIDDEN
                    }
                ]
            },
            {
                'test_name': 'update_sub_organization_by_id',
                'type': 'patch',
                'path_name': 'organizations_retrieve_update_delete',
                'request': [
                    {   # update sub-org by id, okay for staff
                        'test_name': 'update_sub_1_org_1_by_id_by_staff',
                        'args': [self.orgs['sub_1_org_1'].id],
                        'user': 'staff_user',
                        'data': {
                            'name': 'test_1_sub_1_org_1_updated',
                            'desc': 'test_1_sub_1_org_1_desc_updated',
                        },
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                data['id'],
                                str(self.orgs['sub_1_org_1'].id)) and
                            test.assertEqual(
                                data['name'],
                                'test_1_sub_1_org_1_updated')
                        )
                    },
                    {   # update sub-org by id, okay for org admin itself under
                        # which this sub-org exists
                        'test_name': 'update_sub_1_org_1_by_id_by_org_1_admin',
                        'args': [self.orgs['sub_1_org_1'].id],
                        'user': 'org_1_admin_user',
                        'data': {
                            'name': 'test_2_sub_1_org_1_updated',
                            'desc': 'test_2_sub_1_org_1_desc_updated',
                        },
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                data['id'],
                                str(self.orgs['sub_1_org_1'].id)) and
                            test.assertEqual(
                                data['name'],
                                'test_2_sub_1_org_1_updated')
                        )
                    },
                    {   # update sub-org by id, okay for sub-org admin itself
                        'test_name': 'update_sub_1_org_1_by_id_by_sub_1_org_1_admin',
                        'args': [self.orgs['sub_1_org_1'].id],
                        'user': 'sub_org_11_admin_user',
                        'data': {
                            'name': 'test_34_sub_1_org_1_updated',
                            'desc': 'test_34_sub_1_org_1_desc_updated',
                        },
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                data['id'],
                                str(self.orgs['sub_1_org_1'].id)) and
                            test.assertEqual(
                                data['name'],
                                'test_34_sub_1_org_1_updated')
                        )
                    },
                    {   # update sub-org by id, okay for sub-org admin itself,
                        # but bad duplicate name
                        'test_name': 'update_sub_1_org_2_by_id_by_sub_1_org_2_admin_dup_name',
                        'args': [self.orgs['sub_1_org_2'].id],
                        'user': 'sub_org_12_admin_user',
                        'data': {
                            'name': 'test_34_sub_1_org_1_updated',  # duplicate name here
                            'desc': 'test_34_sub_1_org_1_desc_updated',
                        },
                        'status': status.HTTP_400_BAD_REQUEST
                    },
                    {   # update sub-org by id, should return null for other
                        # org-admin under which this sub-org does not exist
                        'test_name': 'update_sub_1_org_1_by_id_by_org_2_admin',
                        'args': [self.orgs['sub_1_org_1'].id],
                        'user': 'org_2_admin_user',
                        'data': {
                            'name': 'test_5_sub_1_org_1_updated',
                            'desc': 'test_5_sub_1_org_1_desc_updated',
                        },
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # update sub-org by id, should return null for other
                        # sub-org admin to which this sub-org does not exist
                        'test_name': 'update_sub_1_org_1_by_id_by_sub_1_org_2_admin',
                        'args': [self.orgs['sub_1_org_1'].id],
                        'user': 'sub_org_12_admin_user',
                        'data': {
                            'name': 'test_6_sub_1_org_1_updated',
                            'desc': 'test_6_sub_1_org_1_desc_updated',
                        },
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # update employee's organization by employee, forbidden
                        'test_name': 'update_sub_1_org_1_by_id_by_employee',
                        'args': [self.orgs['sub_1_org_1'].id],
                        'user': 'employee_user',
                        'data': {
                            'name': 'test_7_sub_1_org_1_updated',
                            'desc': 'test_7_sub_1_org_1_desc_updated',
                        },
                        'status': status.HTTP_403_FORBIDDEN
                    },
                    {   # use employees to update organization info, forbidden
                        'test_name': 'update_sub_1_org_2_by_id_by_employee',
                        'args': [self.orgs['sub_1_org_2'].id],
                        'user': 'employee_user',
                        'data': {
                            'name': 'test_8_sub_1_org_1_updated',
                            'desc': 'test_8_sub_1_org_1_desc_updated',
                        },
                        'status': status.HTTP_403_FORBIDDEN
                    },
                    {   # update sub-org by id, forbidden for random user
                        'test_name': 'update_sub_1_org_1_by_id_by_other_user',
                        'args': [self.orgs['sub_1_org_1'].id],
                        'user': 'other_user',
                        'data': {
                            'name': 'test_9_sub_1_org_1_updated',
                            'desc': 'test_9_sub_1_org_1_desc_updated',
                        },
                        'status': status.HTTP_403_FORBIDDEN
                    },
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
