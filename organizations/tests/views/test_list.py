"""
Defines the unit tests related to 'list' api requests for this application.
"""

from django.urls import include, path
from rest_framework import status

from core.tests import TestsBase


# pylint: disable=line-too-long
class OrganizationListTests(TestsBase):
    """
    Defines unit tests for 'list' api requests for views defined
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
        super(OrganizationListTests, self).setUp()
        self.test = [
            {
                'test_name': 'get_organizations_list',
                'type': 'get',
                'path_name': 'organizations_list_create_delete',
                'request': [
                    {   # get org list by staff
                        'test_name': 'get_org_1_list_by_staff',
                        'args': None,
                        'user': 'staff_user',
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                len(data['results']),
                                len(self.orgs_list)+len(self.sub_orgs_dict))
                        )
                    },
                    {   # get org list by org admin
                        'test_name': 'get_org_list_by_org_1_admin',
                        'args': None,
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                len(data['results']),
                                1+len(self.org_1_sub_orgs))
                        )
                    },
                    {   # get org list by sub-org admin
                        'test_name': 'get_org_list_by_sub_org_1_admin',
                        'args': None,
                        'user': 'sub_org_11_admin_user',
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(len(data['results']), 1)
                        )
                    },
                    {   # get org list by another org admin
                        'test_name': 'get_org_list_by_sub_org_2_admin',
                        'args': None,
                        'user': 'org_2_admin_user',
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                len(data['results']),
                                1+len(self.org_2_sub_orgs))
                        )
                    },
                    {   # get org list by org employee
                        'test_name': 'get_org_list_by_employee',
                        'args': None,
                        'user': 'employee_user',
                        'status': status.HTTP_403_FORBIDDEN,
                    },
                    {   # get org list by org other user
                        'test_name': 'get_org_list_by_employee',
                        'args': None,
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
