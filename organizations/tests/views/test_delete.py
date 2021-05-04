"""
Defines the unit tests related to 'delete' api requests for this application.
"""

from django.urls import include, path
from rest_framework import status

from core.tests import TestsBase


# pylint: disable=line-too-long
class OrganizationDeleteTests(TestsBase):
    """
    Defines unit tests for 'delete' api requests for views defined
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
        super(OrganizationDeleteTests, self).setUp()
        self.test = [
            {
                'test_name': 'delete_organization_by_id',
                'type': 'delete',
                'path_name': 'organizations_retrieve_update_delete',
                'request': [
                    {   # delete org by id, forbidden for org admin itself
                        'test_name': 'delete_org_4_by_id_by_org_4_admin',
                        'args': {'pk': self.orgs['o4_del'].id},
                        'user': 'org_4_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # delete org by id, forbidden for sub-org
                        'test_name': 'delete_org_1_by_id_by_sub_1_org_1_admin',
                        'args': {'pk': self.orgs['o1'].id},
                        'user': 'sub_org_11_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # delete org by id by other org admin, forbidden
                        'test_name': 'delete_org_4_by_id_by_org_1_admin',
                        'args': {'pk': self.orgs['o4_del'].id},
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # delete org by id, forbidden for random user
                        'test_name': 'delete_org_4_by_id_by_other_user',
                        'args': {'pk': self.orgs['o4_del'].id},
                        'user': 'other_user',
                        'status': status.HTTP_403_FORBIDDEN
                    },
                    {   # delete org by id, okay for staff -> at the end so org
                        # remains for other test cases, but this organization
                        # will be protected and will return a bad request.
                        'test_name': 'delete_org_4_by_id_by_staff',
                        'args': {'pk': self.orgs['o4_del'].id},
                        'user': 'staff_user',
                        'status': status.HTTP_400_BAD_REQUEST
                    },
                ]
            },
            {
                'test_name': 'delete_sub_organization_by_id',
                'type': 'delete',
                'path_name': 'organizations_retrieve_update_delete',
                'request': [
                    {   # delete sub-org by id, should not be found for
                        # sub-org admin
                        'test_name': 'delete_sub_5_org_1_by_id_by_sub_1_org_1_admin',
                        'args': {'pk': self.orgs['sub5_del_o1'].id},
                        'user': 'sub_org_11_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # delete sub-org by id, should return null for other
                        # org-admin under which this sub-org does not exist
                        'test_name': 'delete_sub_5_org_1_by_id_by_org_2_admin',
                        'args': {'pk': self.orgs['sub5_del_o1'].id},
                        'user': 'org_2_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # delete sub-org by id by sub-org admin,
                        # should be not found
                        'test_name': 'delete_sub_5_org_1_by_id_by_sub_2_org_1_admin',
                        'args': {'pk': self.orgs['sub5_del_o1'].id},
                        'user': 'sub_org_21_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # delete sub-org by id, forbidden for random user
                        'test_name': 'delete_sub_5_org_1_by_id_by_other_user',
                        'args': {'pk': self.orgs['sub5_del_o1'].id},
                        'user': 'other_user',
                        'status': status.HTTP_403_FORBIDDEN
                    },
                    {   # delete sub-org by id, okay for staff
                        'test_name': 'delete_sub_5_org_1_by_staff',
                        'args': {'pk': self.orgs['sub5_del_o1'].id},
                        'user': 'staff_user',
                        'status': status.HTTP_200_OK
                    },
                    {   # duplicate delete sub-org by id, bad request
                        'test_name': 'delete_sub_5_org_1_by_staff',
                        'args': {'pk': self.orgs['sub5_del_o1'].id},
                        'user': 'staff_user',
                        'status': status.HTTP_404_NOT_FOUND  # already deleted
                    },
                    {   # delete sub-org by id, okay for org admin itself under
                        # which this sub-org exists
                        'test_name': 'delete_sub_5_org_2_by_org_2_admin',
                        'args': {'pk': self.orgs['sub5_del_o2'].id},
                        'user': 'org_2_admin_user',
                        'status': status.HTTP_200_OK
                    },
                ]
            },
        ]

    def test_(self):
        """
        The single test function that runs all the test cases defined in
        the self.test.
        """
        for test_config in self.test:
            self.run_single_test(test_config)
