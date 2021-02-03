"""
Defines the unit tests for organizations applications.
"""
import copy

from core.tests import TestsBase
from django.urls import include, path, reverse
from rest_framework import status


class OrganizationDeleteMultipleTests(TestsBase):
    """
    Defines unit tests for delete-multiple api for the organizations
    application.
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
        super(OrganizationDeleteMultipleTests, self).setUp()
        self.test = [
            {
                'test_name': 'delete_multiple_organizations',
                'type': 'delete',
                'path_name': 'organizations_list_create_delete',
                'request': [
                    {   # delete orgs by id, forbidden for organization admin
                        'test_name': 'delete_multiple_org_by_id_by_org_1_admin',
                        'data': {
                            "id": [
                                self.orgs['org_4_for_deletion'].id,
                                self.orgs['org_5_for_deletion'].id]
                        },
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # delete sub-orgs by id, okay for organization admin
                        'test_name': 'delete_multiple_sub_orgs_2_by_id_by_org_2_admin',
                        'data': {
                            "id": [
                                self.orgs['sub_4_org_2_for_deletion'].id]
                        },
                        'user': 'org_2_admin_user',
                        'status': status.HTTP_200_OK
                    },
                    {   # delete sub-orgs by id, forbidden for other
                        # organization admin
                        'test_name': 'delete_multiple_sub_orgs_1_by_id_by_org_2_admin',
                        'data': {
                            "id": [
                                self.orgs['sub_3_org_1_for_deletion'].id]
                        },
                        'user': 'org_2_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # delete sub-org by id, okay for staff
                        'test_name': 'delete_multiple_sub_orgs_2_by_id_by_staff',
                        'args': None,
                        'data': {
                            "id": [
                                self.orgs['sub_3_org_1_for_deletion'].id]
                        },
                        'user': 'staff_user',
                        'status': status.HTTP_200_OK
                    },
                    {   # delete org by id, okay for staff
                        'test_name': 'delete_multiple_orgs_by_id_by_staff',
                        'data': {
                            "id": [
                                self.orgs['org_4_for_deletion'].id,
                                self.orgs['org_5_for_deletion'].id]
                        },
                        'user': 'staff_user',
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
