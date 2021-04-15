"""
Defines the unit tests related to 'create' api requests for this application.
"""

from django.urls import include, path
from rest_framework import status

from core.tests import TestsBase


# pylint: disable=line-too-long
class OrganizationCreateTests(TestsBase):
    """
    Defines unit tests for 'create' api requests for views defined at
    'organizations/' url.

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
        super(OrganizationCreateTests, self).setUp()
        self.test = [
            {
                'test_name': 'create_top_level_organizations',
                'type': 'post',
                'path_name': 'organizations_list_create_delete',
                'request': [
                    {   # create org, okay for staff
                        'test_name': 'create_org_by_staff',
                        'data': {
                            'name': 'test_12_organization',
                        },
                        'user': 'staff_user',
                        'status': status.HTTP_201_CREATED,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                data['name'], 'test_12_organization')
                        )
                    },
                    {   # duplicate create by staff, bad
                        'test_name': 'create_org_duplicate_by_staff',
                        'data': {
                            'name': 'test_12_organization',
                        },
                        'user': 'staff_user',
                        'status': status.HTTP_400_BAD_REQUEST
                    },
                    {   # create org by org-admin, forbidden
                        'test_name': 'create_org_by_org_admin',
                        'data': {
                            'name': 'test_3_organization',
                            'parent': None
                        },
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_400_BAD_REQUEST
                    },
                    {   # create org by sub-org-admin, forbidden
                        'test_name': 'create_org_by_sub_org_admin',
                        'data': {
                            'name': 'test_4_organization',
                            'parent': None
                        },
                        'user': 'sub_org_11_admin_user',
                        'status': status.HTTP_400_BAD_REQUEST
                    },
                    {   # create org by employee, forbidden
                        'test_name': 'create_org_by_employee',
                        'data': {
                            'name': 'test_5_organization',
                        },
                        'user': 'employee_user',
                        'status': status.HTTP_403_FORBIDDEN
                    },
                    {   # create org by random user, forbidden
                        'test_name': 'create_org_by_other_user',
                        'data': {
                            'name': 'test_6_organization',
                        },
                        'user': 'other_user',
                        'status': status.HTTP_403_FORBIDDEN
                    },
                ]
            },
            {
                'test_name': 'create_lower_level_organizations',
                'type': 'post',
                'path_name': 'organizations_list_create_delete',
                'request': [
                    {   # create sub-org under org_1, okay for staff
                        'test_name': 'create_sub_org_in_org_1_by_staff',
                        'data': {
                            'name': 'test_12_sub_org_in_org_1',
                            'parent': self.orgs['org_1'].id
                        },
                        'user': 'staff_user',
                        'status': status.HTTP_201_CREATED,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                data['name'], 'test_12_sub_org_in_org_1')
                        )
                    },
                    {   # duplicate create by staff, bad
                        'test_name': 'create_dup_sub_org_in_org_1_by_staff',
                        'data': {
                            'name': 'test_12_sub_org_in_org_1',
                            'parent': self.orgs['org_1'].id
                        },
                        'user': 'staff_user',
                        'status': status.HTTP_400_BAD_REQUEST
                    },
                    {   # create sub-org under org_1, okay for org admin if
                        # org is within descendents of admin organization
                        'test_name': 'create_sub_org_in_org_1_by_org_1_admin',
                        'data': {
                            'name': 'test_34_sub_org_in_org_1',
                            'parent': self.orgs['org_1'].id
                        },
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_201_CREATED,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                data['name'], 'test_34_sub_org_in_org_1')
                        )
                    },
                    {   # duplicate create by org-admin, bad
                        'test_name': 'create_dup_sub_org_in_org_1_by_org_1_admin',
                        'data': {
                            'name': 'test_34_sub_org_in_org_1',
                            'parent': self.orgs['org_1'].id
                        },
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_400_BAD_REQUEST
                    },
                    {   # create sub-org by sub-org admin with a higher level
                        # organization, forbidden
                        'test_name': 'create_sub_org_in_org_1_by_sub_1_org_1_admin',
                        'data': {
                            'name': 'test_5_sub_org_in_org_1',
                            'parent': self.orgs['org_1'].id
                        },
                        'user': 'sub_org_11_admin_user',
                        'status': status.HTTP_400_BAD_REQUEST
                    },
                    {   # create sub-org by another admin,
                        # forbidden if org doesn't match
                        'test_name': 'create_sub_org_in_org_1_by_org_2_admin',
                        'data': {
                            'name': 'test_6_sub_org_in_org_1',
                            'parent': self.orgs['org_1'].id
                        },
                        'user': 'org_2_admin_user',
                        'status': status.HTTP_400_BAD_REQUEST
                    },
                    {   # create sub-org by another admin, org matches, okay
                        'test_name': 'create_sub_org_in_org_2_by_org_2_admin',
                        'data': {
                            'name': 'test_7_sub_org_in_org_2',
                            'parent': self.orgs['org_2'].id
                        },
                        'user': 'org_2_admin_user',
                        'status': status.HTTP_201_CREATED,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                data['name'], 'test_7_sub_org_in_org_2')
                        )
                    },
                    {   # create sub-org by employee, forbidden
                        'test_name': 'create_sub_org_in_org_1_by_employee',
                        'data': {
                            'name': 'test_8_sub_org_in_org_1',
                            'parent': self.orgs['org_1'].id
                        },
                        'user': 'employee_user',
                        'status': status.HTTP_403_FORBIDDEN
                    },
                    {   # create sub-org by random user, forbidden
                        'test_name': 'create_sub_org_in_org_1_by_other_user',
                        'data': {
                            'name': 'test_9_sub_org_in_org_1',
                            'parent': self.orgs['org_1'].id
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
