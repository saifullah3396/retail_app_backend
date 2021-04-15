"""
Defines the unit tests related to 'list-by-id-list' api requests for this
application.
"""

from django.urls import include, path
from rest_framework import status

from core.tests import TestsBase


# pylint: disable=line-too-long
class OrganizationListByIdListTests(TestsBase):
    """
    Defines unit tests for 'list-by-id-list' api requests for views defined
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
        super(OrganizationListByIdListTests, self).setUp()
        self.test = [
            {
                'test_name': 'get_organizations_list_multiple',
                'type': 'get',
                'path_name': 'organizations_list_create_delete',
                'request': [
                    {   # get org list by staff
                        'test_name': 'get_multiple_org_by_id_by_staff',
                        'args': None,
                        'data': {
                            "id": [
                                self.orgs['sub_1_org_2'].id,
                                self.orgs['sub_2_org_2'].id]
                        },
                        'user': 'staff_user',
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(len(data['results']), 2)
                        )
                    },
                    {   # get sub-orgs of different org (2) by org admin (1),
                        # forbidden
                        'test_name': 'get_multiple_sub_org_2_by_id_by_org_1_admin',
                        'args': None,
                        'data': {
                            "id": [
                                self.orgs['sub_1_org_2'].id,
                                self.orgs['sub_2_org_2'].id]
                        },
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # get sub-orgs of different org (2) by sub-org
                        # admin (1), forbidden
                        'test_name': 'get_multiple_sub_org_2_by_id_by_sub_org_1_admin',
                        'args': None,
                        'data': {
                            "id": [
                                self.orgs['sub_1_org_2'].id,
                                self.orgs['sub_2_org_2'].id]
                        },
                        'user': 'sub_org_11_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # get sub-orgs of org (2) by org admin (2), should work
                        'test_name': 'get_multiple_sub_org_2_by_id_by_org_2_admin',
                        'args': None,
                        'data': {
                            "id": [
                                self.orgs['sub_1_org_2'].id,
                                self.orgs['sub_2_org_2'].id]
                        },
                        'user': 'org_2_admin_user',
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(len(data['results']), 2)
                        )
                    },
                    {   # get org list of orgs by employee
                        'test_name': 'get_multiple_sub_org_2_by_id_by_employee',
                        'args': None,
                        'data': {
                            "id": [
                                self.orgs['sub_1_org_2'].id,
                                self.orgs['sub_2_org_2'].id]
                        },
                        'user': 'employee_user',
                        'status': status.HTTP_403_FORBIDDEN
                    },
                    {   # get org list of orgs by some random user
                        'test_name': 'get_multiple_sub_org_2_by_id_by_other_user',
                        'args': None,
                        'data': {
                            "id": [
                                self.orgs['sub_1_org_2'].id,
                                self.orgs['sub_2_org_2'].id]
                        },
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
