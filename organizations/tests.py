import copy
from django.urls import include, path, reverse
from rest_framework import status
from core.tests import TestsBase


class OrganizationTests(TestsBase):
    api_urlpatterns = [
        path('organizations/', include('organizations.api.urls')),
    ]

    urlpatterns = [
        path('api/v1/', include(api_urlpatterns)),
    ]

    def setUp(self):
        super(OrganizationTests, self).setUp()
        test_get = [
            {
                'test_name': 'get_organizations_list',
                'type': 'get',
                'path_name': 'organizations_list_create',
                'request': [
                    {   # get org list by staff
                        'args': None,
                        'user': 'staff_user',
                        'status': status.HTTP_200_OK
                    },
                    {    # get org list by org admin
                        'args': None,
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_200_OK
                    },
                    {   # get org list by sub-org admin
                        'args': None,
                        'user': 'sub_org_11_admin_user',
                        'status': status.HTTP_200_OK
                    },
                    {   # get org list by another org admin
                        'args': None,
                        'user': 'org_2_admin_user',
                        'status': status.HTTP_200_OK
                    },
                    {   # get org list by org admin
                        'args': None,
                        'user': 'employee_user',
                        'status': status.HTTP_403_FORBIDDEN
                    },
                    {   # get org list by org admin
                        'args': None,
                        'user': 'other_user',
                        'status': status.HTTP_403_FORBIDDEN
                    }
                ]
            }
        ]

        test_get_multiple = [
            {
                'test_name': 'get_organizations_list_multiple',
                'type': 'get',
                'path_name': 'organizations_list_create',
                'request': [
                    {   # get org list by staff
                        'args': None,
                        'data': {
                            "id": [
                                self.orgs['sub_1_org_2'].id,
                                self.orgs['sub_2_org_2'].id]
                        },
                        'user': 'staff_user',
                        'status': status.HTTP_200_OK
                    },
                    {   # get sub-orgs of different org (2) by org admin (1),
                        # forbidden
                        'args': None,
                        'data': {
                            "id": [
                                self.orgs['sub_1_org_2'].id,
                                self.orgs['sub_2_org_2'].id]
                        },
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_403_FORBIDDEN
                    },
                    {   # get sub-orgs of different org (2) by sub-org
                        # admin (1), forbidden
                        'args': None,
                        'data': {
                            "id": [
                                self.orgs['sub_1_org_2'].id,
                                self.orgs['sub_2_org_2'].id]
                        },
                        'user': 'sub_org_11_admin_user',
                        'status': status.HTTP_403_FORBIDDEN
                    },
                    {   # get sub-orgs of org (2) by org admin (2), should work
                        'args': None,
                        'data': {
                            "id": [
                                self.orgs['sub_1_org_2'].id,
                                self.orgs['sub_2_org_2'].id]
                        },
                        'user': 'org_2_admin_user',
                        'status': status.HTTP_200_OK
                    },
                    {   # get org list of orgs by some random user
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

        test_create = [
            {
                'test_name': 'create_top_level_organizations',
                'type': 'post',
                'path_name': 'organizations_list_create',
                'request': [
                    {   # create org, okay for staff
                        'data': {
                            'name': 'My Organization',
                            'desc': 'No description',
                        },
                        'user': 'staff_user',
                        'status': status.HTTP_201_CREATED
                    },
                    {   # duplicate create by staff, bad
                        'data': {
                            'name': 'My Organization',
                            'desc': 'No description',
                        },
                        'user': 'staff_user',
                        'status': status.HTTP_400_BAD_REQUEST
                    },
                    {   # create org by org-admin, forbidden
                        'data': {
                            'name': 'My Organization1',
                            'desc': 'No description',
                            'parent': None
                        },
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_403_FORBIDDEN
                    },
                    {   # create org by sub-org-admin, forbidden
                        'data': {
                            'name': 'My Organization2',
                            'desc': 'No description',
                            'parent': None
                        },
                        'user': 'sub_org_11_admin_user',
                        'status': status.HTTP_403_FORBIDDEN
                    },
                    {   # create org by another org-admin, forbidden
                        'data': {
                            'name': 'My Organization3',
                            'desc': 'No description',
                            'parent': None
                        },
                        'user': 'org_2_admin_user',
                        'status': status.HTTP_403_FORBIDDEN
                    },
                    {   # create org by random user, forbidden
                        'data': {
                            'name': 'My Organization4',
                            'desc': 'No description',
                        },
                        'user': 'other_user',
                        'status': status.HTTP_403_FORBIDDEN
                    },
                ]
            },
            {
                'test_name': 'create_lower_level_organizations',
                'type': 'post',
                'path_name': 'organizations_list_create',
                'request': [
                    {   # create sub-org under org_1, okay for staff
                        'data': {
                            'name': 'sub_org_10_in_org_1',
                            'desc': 'No description',
                            'parent': self.orgs['org_1'].id
                        },
                        'user': 'staff_user',
                        'status': status.HTTP_201_CREATED
                    },
                    {   # duplicate create by staff, bad
                        'data': {
                            'name': 'sub_org_10_in_org_1',
                            'desc': 'No description',
                            'parent': self.orgs['org_1'].id
                        },
                        'user': 'staff_user',
                        'status': status.HTTP_400_BAD_REQUEST
                    },
                    {   # create sub-org under org_1, okay for org admin if
                        # org is within descendents of admin organization
                        'data': {
                            'name': 'sub_org_11_in_org_1',
                            'desc': 'No description',
                            'parent': self.orgs['org_1'].id
                        },
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_201_CREATED
                    },
                    {   # duplicate create by org-admin, bad
                        'data': {
                            'name': 'sub_org_11_in_org_1',
                            'desc': 'No description',
                            'parent': self.orgs['org_1'].id
                        },
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_400_BAD_REQUEST
                    },
                    {   # create sub-org by sub-org admin with a higher level
                        # organization, forbidden
                        'data': {
                            'name': 'sub_org_12_in_org_1',
                            'desc': 'No description',
                            'parent': self.orgs['org_1'].id
                        },
                        'user': 'sub_org_11_admin_user',
                        'status': status.HTTP_403_FORBIDDEN
                    },
                    {   # create sub-org by another admin,
                        # forbidden if org doesn't match
                        'data': {
                            'name': 'sub_org_13_in_org_1',
                            'desc': 'No description',
                            'parent': self.orgs['org_1'].id
                        },
                        'user': 'org_2_admin_user',
                        'status': status.HTTP_403_FORBIDDEN
                    },
                    {   # create sub-org by another admin, org matches, okay
                        'data': {
                            'name': 'sub_org_14_in_org_2',
                            'desc': 'No description',
                            'parent': self.orgs['org_2'].id
                        },
                        'user': 'org_2_admin_user',
                        'status': status.HTTP_201_CREATED
                    },
                    {   # create sub-org by random user, forbidden
                        'data': {
                            'name': 'sub_org_15_in_org_1',
                            'desc': 'No description',
                            'parent': self.orgs['org_1'].id
                        },
                        'user': 'other_user',
                        'status': status.HTTP_403_FORBIDDEN
                    },
                ]
            }
        ]

        test_delete_multiple = [
            {
                'test_name': 'delete_multiple_organizations',
                'type': 'delete',
                'path_name': 'organizations_list_create',
                'request': [
                    {   # delete orgs by id, forbidden for organization admin
                        'data': {
                            "id": [
                                self.orgs['org_1'].id,
                                self.orgs['org_2'].id,
                                self.orgs['org_3'].id]
                        },
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_403_FORBIDDEN
                    },
                    {   # delete sub-orgs by id, okay for organization admin
                        'data': {
                            "id": [
                                self.orgs['sub_3_org_2'].id]
                        },
                        'user': 'org_2_admin_user',
                        'status': status.HTTP_200_OK
                    },
                    {   # delete sub-orgs by id, forbidden for other
                        # organization admin
                        'data': {
                            "id": [
                                self.orgs['sub_2_org_1'].id]
                        },
                        'user': 'org_2_admin_user',
                        'status': status.HTTP_403_FORBIDDEN
                    },
                    {   # delete sub-org by id, okay for staff
                        'args': None,
                        'data': {
                            "id": [
                                self.orgs['sub_1_org_2'].id]
                        },
                        'user': 'staff_user',
                        'status': status.HTTP_200_OK
                    },
                    {   # delete org by id, okay for staff
                        'data': {
                            "id": [
                                self.orgs['org_1'].id,
                                self.orgs['org_2'].id,
                                self.orgs['org_3'].id]
                        },
                        'user': 'staff_user',
                        'status': status.HTTP_200_OK
                    },
                ]
            }
        ]

        test_retrieve = [
            {
                'test_name': 'get_organization_by_id',
                'type': 'get',
                'path_name': 'organizations_rud',
                'request': [
                    {   # get org by id, okay for staff
                        'args': [self.orgs['org_1'].id],
                        'user': 'staff_user',
                        'status': status.HTTP_200_OK
                    },
                    {   # get org by id, okay for org admin itself
                        'args': [self.orgs['org_1'].id],
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_200_OK
                    },
                    {   # get org by id, forbidden for sub-org
                        'args': [self.orgs['org_1'].id],
                        'user': 'sub_org_11_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # get org by id, should return null for other org-admin
                        'args': [self.orgs['org_1'].id],
                        'user': 'org_2_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # get org by id, forbidden for random user
                        'args': [self.orgs['org_1'].id],
                        'user': 'other_user',
                        'status': status.HTTP_403_FORBIDDEN
                    },
                    {   # get org by id, forbidden for random user
                        'args': [self.orgs['org_1'].id],
                        'user': 'other_user',
                        'status': status.HTTP_403_FORBIDDEN
                    }
                ]
            },
            {
                'test_name': 'get_sub_organization_by_id',
                'type': 'get',
                'path_name': 'organizations_rud',
                'request': [
                    {   # get sub-org by id, okay for staff
                        'args': [self.orgs['sub_1_org_1'].id],
                        'user': 'staff_user',
                        'status': status.HTTP_200_OK
                    },
                    {   # get sub-org by id, okay for org admin itself under
                        # which this sub-org exists
                        'args': [self.orgs['sub_1_org_1'].id],
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_200_OK
                    },
                    {   # get sub-org by id, okay for sub-org admin itself
                        'args': [self.orgs['sub_1_org_1'].id],
                        'user': 'sub_org_11_admin_user',
                        'status': status.HTTP_200_OK
                    },
                    {   # get sub-org by id, okay for sub-org admin itself
                        'args': [self.orgs['sub_1_org_2'].id],
                        'user': 'sub_org_12_admin_user',
                        'status': status.HTTP_200_OK
                    },
                    {   # get sub-org by id, okay for sub-org admin itself
                        'args': [self.orgs['sub_2_org_1'].id],
                        'user': 'sub_org_21_admin_user',
                        'status': status.HTTP_200_OK
                    },
                    {   # get sub-org by id, okay for sub-org admin itself
                        'args': [self.orgs['sub_2_org_2'].id],
                        'user': 'sub_org_22_admin_user',
                        'status': status.HTTP_200_OK
                    },
                    {   # get sub-org by id, should return null for other
                        # org-admin under which this sub-org does not exist
                        'args': [self.orgs['sub_1_org_1'].id],
                        'user': 'org_2_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # get sub-org by id, should return null for other
                        # sub-org admin to which this sub-org does not exist
                        'args': [self.orgs['sub_1_org_1'].id],
                        'user': 'sub_org_12_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # get sub-org by id, should return null for other
                        # sub-org admin to which this sub-org does not exist
                        'args': [self.orgs['sub_1_org_1'].id],
                        'user': 'sub_org_21_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # get employees own organization info, okay
                        'args': [self.orgs['sub_1_org_1'].id],
                        'user': 'employee_user',
                        'status': status.HTTP_200_OK
                    },
                    {   # use employees to get other organization info, bad
                        'args': [self.orgs['sub_1_org_2'].id],
                        'user': 'employee_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # get sub-org by id, forbidden for random user
                        'args': [self.orgs['sub_1_org_1'].id],
                        'user': 'other_user',
                        'status': status.HTTP_403_FORBIDDEN
                    }
                ]
            }
        ]

        test_update = [
            {
                'test_name': 'update_organization_by_id',
                'type': 'patch',
                'path_name': 'organizations_rud',
                'request': [
                    {   # update org by id, okay for staff
                        'args': [self.orgs['org_1'].id],
                        'user': 'staff_user',
                        'data': {
                            'name': 'org_1_updated',
                            'desc': 'org_1_desc_updated',
                        },
                        'status': status.HTTP_200_OK
                    },
                    {   # update org by id, okay for org admin itself
                        'args': [self.orgs['org_1'].id],
                        'user': 'org_1_admin_user',
                        'data': {
                            'name': 'org_1_updated',
                            'desc': 'org_1_desc_updated',
                        },
                        'status': status.HTTP_200_OK
                    },
                    {   # update org by id, sub-org admin has no access to it
                        'args': [self.orgs['org_1'].id],
                        'user': 'sub_org_11_admin_user',
                        'data': {
                            'name': 'org_1_updated',
                            'desc': 'org_1_desc_updated',
                        },
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # update org by id, should return null for other
                        # org-admin
                        'args': [self.orgs['org_1'].id],
                        'user': 'org_2_admin_user',
                        'data': {
                            'name': 'org_1_updated',
                            'desc': 'org_1_desc_updated',
                        },
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # update org by id, forbidden for random user
                        'args': [self.orgs['org_1'].id],
                        'user': 'other_user',
                        'data': {
                            'name': 'org_1_updated',
                            'desc': 'org_1_desc_updated',
                        },
                        'status': status.HTTP_403_FORBIDDEN
                    }
                ]
            },
            {
                'test_name': 'update_sub_organization_by_id',
                'type': 'patch',
                'path_name': 'organizations_rud',
                'request': [
                    {   # update sub-org by id, okay for staff
                        'args': [self.orgs['sub_1_org_1'].id],
                        'user': 'staff_user',
                        'data': {
                            'name': 'sub_1_org_1_updated',
                            'desc': 'sub_1_org_1_desc_updated',
                        },
                        'status': status.HTTP_200_OK
                    },
                    {   # update sub-org by id, okay for org admin itself under
                        # which this sub-org exists
                        'args': [self.orgs['sub_1_org_1'].id],
                        'user': 'org_1_admin_user',
                        'data': {
                            'name': 'sub_1_org_1_updated',
                            'desc': 'sub_1_org_1_desc_updated',
                        },
                        'status': status.HTTP_200_OK
                    },
                    {   # update sub-org by id, okay for sub-org admin itself
                        'args': [self.orgs['sub_1_org_1'].id],
                        'user': 'sub_org_11_admin_user',
                        'data': {
                            'name': 'sub_1_org_1_updated',
                            'desc': 'sub_1_org_1_desc_updated',
                        },
                        'status': status.HTTP_200_OK
                    },
                    {   # update sub-org by id, okay for sub-org admin itself,
                        # but bad duplicate name
                        'args': [self.orgs['sub_1_org_2'].id],
                        'user': 'sub_org_12_admin_user',
                        'data': {
                            'name': 'sub_1_org_1_updated',  # duplicate name here
                            'desc': 'sub_1_org_1_desc_updated',
                        },
                        'status': status.HTTP_400_BAD_REQUEST
                    },
                    {   # update sub-org by id, okay for sub-org admin itself
                        'args': [self.orgs['sub_1_org_2'].id],
                        'user': 'sub_org_12_admin_user',
                        'data': {
                            'name': 'sub_1_org_2_updated',
                            'desc': 'sub_1_org_2_desc_updated',
                        },
                        'status': status.HTTP_200_OK
                    },
                    {   # update sub-org by id, okay for sub-org admin itself
                        'args': [self.orgs['sub_2_org_1'].id],
                        'user': 'sub_org_21_admin_user',
                        'data': {
                            'name': 'sub_2_org_1_updated',
                            'desc': 'sub_2_org_1_desc_updated',
                        },
                        'status': status.HTTP_200_OK
                    },
                    {   # update sub-org by id, okay for sub-org admin itself
                        'args': [self.orgs['sub_2_org_2'].id],
                        'user': 'sub_org_22_admin_user',
                        'data': {
                            'name': 'sub_2_org_2_updated',
                            'desc': 'sub_2_org_2_desc_updated',
                        },
                        'status': status.HTTP_200_OK
                    },
                    {   # update sub-org by id, should return null for other
                        # org-admin under which this sub-org does not exist
                        'args': [self.orgs['sub_1_org_1'].id],
                        'user': 'org_2_admin_user',
                        'data': {
                            'name': 'sub_1_org_1_updated',
                            'desc': 'sub_1_org_1_desc_updated',
                        },
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # update sub-org by id, should return null for other
                        # sub-org admin to which this sub-org does not exist
                        'args': [self.orgs['sub_1_org_1'].id],
                        'user': 'sub_org_12_admin_user',
                        'data': {
                            'name': 'sub_1_org_1_updated',
                            'desc': 'sub_1_org_1_desc_updated',
                        },
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # update sub-org by id, should return null for other
                        # sub-org admin to which this sub-org does not exist
                        'args': [self.orgs['sub_1_org_1'].id],
                        'user': 'sub_org_21_admin_user',
                        'data': {
                            'name': 'sub_1_org_1_updated',
                            'desc': 'sub_1_org_1_desc_updated',
                        },
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # update sub-org by id, forbidden for random user
                        'args': [self.orgs['sub_1_org_1'].id],
                        'user': 'other_user',
                        'data': {
                            'name': 'sub_1_org_1_updated',
                            'desc': 'sub_1_org_1_desc_updated',
                        },
                        'status': status.HTTP_403_FORBIDDEN
                    },
                    {   # update employee's organization by employee, forbidden
                        'args': [self.orgs['sub_1_org_1'].id],
                        'user': 'employee_user',
                        'data': {
                            'name': 'sub_1_org_1_updated',
                            'desc': 'sub_1_org_1_desc_updated',
                        },
                        'status': status.HTTP_403_FORBIDDEN
                    },
                    {   # use employees to update organization info, forbidden
                        'args': [self.orgs['sub_1_org_2'].id],
                        'user': 'employee_user',
                        'data': {
                            'name': 'sub_1_org_1_updated',
                            'desc': 'sub_1_org_1_desc_updated',
                        },
                        'status': status.HTTP_403_FORBIDDEN
                    },
                ]
            }
        ]

        test_delete = [
            {
                'test_name': 'delete_organization_by_id',
                'type': 'delete',
                'path_name': 'organizations_rud',
                'request': [
                    {   # delete org by id, forbidden for org admin itself
                        'args': [self.orgs['org_3'].id],
                        'user': 'org_3_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # delete org by id, forbidden for sub-org
                        'args': [self.orgs['org_3'].id],
                        'user': 'sub_org_13_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # delete org by id by other org admin, forbidden
                        'args': [self.orgs['org_3'].id],
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # delete org by id, forbidden for random user
                        'args': [self.orgs['org_3'].id],
                        'user': 'other_user',
                        'status': status.HTTP_403_FORBIDDEN
                    },
                    {   # delete org by id, okay for staff -> at the end so org
                        # remains for other test cases
                        'args': [self.orgs['org_3'].id],
                        'user': 'staff_user',
                        'status': status.HTTP_200_OK
                    },
                ]
            },
            {
                'test_name': 'delete_sub_organization_by_id',
                'type': 'delete',
                'path_name': 'organizations_rud',
                'request': [
                    {   # delete sub-org by id, should not be found for
                        # sub-org admin
                        'args': [self.orgs['sub_1_org_1'].id],
                        'user': 'sub_org_11_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # delete sub-org by id, should return null for other
                        # org-admin under which this sub-org does not exist
                        'args': [self.orgs['sub_1_org_1'].id],
                        'user': 'org_2_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # delete sub-org by id by sub-org admin,
                        # should be not found
                        'args': [self.orgs['sub_1_org_1'].id],
                        'user': 'sub_org_21_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # delete sub-org by id, forbidden for random user
                        'args': [self.orgs['sub_1_org_1'].id],
                        'user': 'other_user',
                        'status': status.HTTP_403_FORBIDDEN
                    },
                    {   # delete sub-org by id, okay for staff
                        'args': [self.orgs['sub_2_org_2'].id],
                        'user': 'staff_user',
                        'status': status.HTTP_200_OK
                    },
                    {   # duplicate delete sub-org by id, bad request
                        'args': [self.orgs['sub_2_org_2'].id],
                        'user': 'staff_user',
                        'status': status.HTTP_404_NOT_FOUND  # already deleted
                    },
                    {   # delete sub-org by id, okay for org admin itself under
                        # which this sub-org exists
                        'args': [self.orgs['sub_1_org_2'].id],
                        'user': 'org_2_admin_user',
                        'status': status.HTTP_200_OK
                    },
                ]
            },
        ]

        self.test_sets = [
            test_get,
            test_get_multiple,
            test_create,
            test_retrieve,
            test_update,
            test_delete,
            test_delete_multiple,
        ]

    def run_single_test(self, config):
        path_name = config['path_name']
        for request in config['request']:
            with self.subTest(request=request, test_name=config['test_name']):
                if 'args' in request:
                    url = reverse(path_name, args=request['args'])
                else:
                    url = reverse(path_name)

                data = None
                if 'data' in request:
                    data = request['data']

                response = self.call_api(
                    url,
                    data,
                    self.tokens[request['user']],
                    request['status'],
                    config['type'])

    def test_all_sets(self):
        for test_set in self.test_sets:
            for test_config in test_set:
                self.run_single_test(test_config)
