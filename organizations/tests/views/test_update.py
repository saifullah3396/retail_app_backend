"""
Defines the unit tests related to 'update' api requests for this application.
"""

from django.urls import include, path
from rest_framework import status

from core.tests import TestsBase


# pylint: disable=line-too-long
class OrganizationUpdateTests(TestsBase):
    """
    Defines unit tests for 'update' api requests for views defined
    at 'organizations/' url.

    Attributes:
        api_urlpatterns: Api url patterns used in this test unit.
        urlpatterns: Complete url pattern used in this test unit.
    """

    api_urlpatterns = [
        path('organizations/', include('organizations.api.urls')),
    ]

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
                        'args': {'pk': self.orgs['o1'].id},
                        'user': 'staff_user',
                        'data': {
                            'name': 'test_1_org_1_updated',
                        },
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                data['id'],
                                str(self.orgs['o1'].id)) and
                            test.assertEqual(
                                data['name'], 'test_1_org_1_updated')
                        )
                    },
                    {   # update org by id, okay for org admin itself
                        'test_name': 'update_org_1_by_id_by_org_1_admin',
                        'args': {'pk': self.orgs['o1'].id},
                        'user': 'org_1_admin_user',
                        'data': {
                            'name': 'test_2_org_1_updated',
                        },
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                data['id'],
                                str(self.orgs['o1'].id)) and
                            test.assertEqual(
                                data['name'], 'test_2_org_1_updated')
                        )
                    },
                    {   # update org by id, sub-org admin has no access to it
                        'test_name': 'update_org_1_by_id_by_sub_1_org_1_admin',
                        'args': {'pk': self.orgs['o1'].id},
                        'user': 'sub_org_11_admin_user',
                        'data': {
                            'name': 'test_3_org_1_updated',
                        },
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # update org by id, should return null for other
                        # org-admin
                        'test_name': 'update_org_1_by_id_by_org_2_admin',
                        'args': {'pk': self.orgs['o1'].id},
                        'user': 'org_2_admin_user',
                        'data': {
                            'name': 'test_4_org_1_updated',
                        },
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # update org by id, forbidden for employee
                        'test_name': 'update_org_1_by_id_by_employee',
                        'args': {'pk': self.orgs['o1'].id},
                        'user': 'employee_user',
                        'data': {
                            'name': 'test_5_org_1_updated',
                        },
                        'status': status.HTTP_403_FORBIDDEN
                    },
                    {   # update org by id, forbidden for random user
                        'test_name': 'update_org_1_by_id_by_other_user',
                        'args': {'pk': self.orgs['o1'].id},
                        'user': 'other_user',
                        'data': {
                            'name': 'test_6_org_1_updated',
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
                        'args': {'pk': self.orgs['sub1_o1'].id},
                        'user': 'staff_user',
                        'data': {
                            'name': 'test_1_sub_1_org_1_updated',
                        },
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                data['id'],
                                str(self.orgs['sub1_o1'].id)) and
                            test.assertEqual(
                                data['name'],
                                'test_1_sub_1_org_1_updated')
                        )
                    },
                    {   # update sub-org by id, okay for org admin itself under
                        # which this sub-org exists
                        'test_name': 'update_sub_1_org_1_by_id_by_org_1_admin',
                        'args': {'pk': self.orgs['sub1_o1'].id},
                        'user': 'org_1_admin_user',
                        'data': {
                            'name': 'test_2_sub_1_org_1_updated',
                        },
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                data['id'],
                                str(self.orgs['sub1_o1'].id)) and
                            test.assertEqual(
                                data['name'],
                                'test_2_sub_1_org_1_updated')
                        )
                    },
                    {   # update sub-org by id, okay for sub-org admin itself
                        'test_name': 'update_sub_1_org_1_by_id_by_sub_1_org_1_admin',
                        'args': {'pk': self.orgs['sub1_o1'].id},
                        'user': 'sub_org_11_admin_user',
                        'data': {
                            'name': 'test_34_sub_1_org_1_updated',
                        },
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                data['id'],
                                str(self.orgs['sub1_o1'].id)) and
                            test.assertEqual(
                                data['name'],
                                'test_34_sub_1_org_1_updated')
                        )
                    },
                    {   # update sub-org by id, okay for sub-org admin itself,
                        # but bad duplicate name
                        'test_name': 'update_sub_2_org_1_by_id_by_sub_1_org_2_admin_dup_name',
                        'args': {'pk': self.orgs['sub2_o1'].id},
                        'user': 'sub_org_21_admin_user',
                        'data': {
                            'name': 'test_34_sub_1_org_1_updated',  # duplicate name here
                        },
                        'status': status.HTTP_400_BAD_REQUEST
                    },
                    {   # update sub-org by id, should return null for other
                        # org-admin under which this sub-org does not exist
                        'test_name': 'update_sub_1_org_1_by_id_by_org_2_admin',
                        'args': {'pk': self.orgs['sub1_o1'].id},
                        'user': 'org_2_admin_user',
                        'data': {
                            'name': 'test_5_sub_1_org_1_updated',
                        },
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # update sub-org by id, should return null for other
                        # sub-org admin to which this sub-org does not exist
                        'test_name': 'update_sub_1_org_1_by_id_by_sub_1_org_2_admin',
                        'args': {'pk': self.orgs['sub1_o1'].id},
                        'user': 'sub_org_12_admin_user',
                        'data': {
                            'name': 'test_6_sub_1_org_1_updated',
                        },
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # update employee's organization by employee, forbidden
                        'test_name': 'update_sub_1_org_1_by_id_by_employee',
                        'args': {'pk': self.orgs['sub1_o1'].id},
                        'user': 'employee_user',
                        'data': {
                            'name': 'test_7_sub_1_org_1_updated',
                        },
                        'status': status.HTTP_403_FORBIDDEN
                    },
                    {   # use employees to update organization info, forbidden
                        'test_name': 'update_sub_1_org_2_by_id_by_employee',
                        'args': {'pk': self.orgs['sub1_o2'].id},
                        'user': 'employee_user',
                        'data': {
                            'name': 'test_8_sub_1_org_1_updated',
                        },
                        'status': status.HTTP_403_FORBIDDEN
                    },
                    {   # update sub-org by id, forbidden for random user
                        'test_name': 'update_sub_1_org_1_by_id_by_other_user',
                        'args': {'pk': self.orgs['sub1_o1'].id},
                        'user': 'other_user',
                        'data': {
                            'name': 'test_9_sub_1_org_1_updated',
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
