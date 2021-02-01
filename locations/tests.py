import copy
from django.urls import include, path, reverse
from rest_framework import status
from core.tests import TestsBase


class LocationTests(TestsBase):
    api_urlpatterns = [
        path('locations/', include('locations.api.urls')),
    ]

    urlpatterns = [
        path('api/v1/', include(api_urlpatterns)),
    ]

    def setUp(self):
        super(LocationTests, self).setUp()
        test_get = [
            {
                'test_name': 'get_locations_list',
                'type': 'get',
                'path_name': 'locations_list_create_delete',
                'request': [
                    {   # get locations list by staff
                        'args': None,
                        'user': 'staff_user',
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                len(data['results']), len(self.locations_dict))
                        )
                    },
                    {    # get locations list by org admin
                        'args': None,
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                len(data['results']),
                                len(self.org_1_locations) +
                                len(self.sub_1_org_1_locations))
                        )
                    },
                    {   # get locations list by sub-org admin
                        'args': None,
                        'user': 'sub_org_11_admin_user',
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                len(data['results']),
                                len(self.sub_1_org_1_locations))
                        )
                    },
                    {   # get locations list by another org admin
                        'args': None,
                        'user': 'org_2_admin_user',
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                len(data['results']),
                                len(self.org_2_locations) +
                                len(self.sub_1_org_2_locations))
                        )
                    },
                    {   # get locations list by employee, okay
                        'args': None,
                        'user': 'employee_user',
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                len(data['results']),
                                len(self.users_dict['employee_user']
                                    ['authorized_locations']))
                        )
                    },
                    {   # get locations list by random user, forbidden
                        'args': None,
                        'user': 'other_user',
                        'status': status.HTTP_403_FORBIDDEN
                    }
                ]
            }
        ]

        test_get_multiple = [
            {
                'test_name': 'get_locations_list_multiple',
                'type': 'get',
                'path_name': 'locations_list_create_delete',
                'request': [
                    {   # get locations list by staff
                        'test_name': 'test_get_locations_list_by_ids_by_staff',
                        'args': None,
                        'data': {
                            'id': [
                                self.locations['location_1_org_1'].id,
                                self.locations['location_2_org_1'].id,
                                self.locations['location_1_org_2'].id]
                        },
                        'user': 'staff_user',
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(len(data['results']), 3)
                        )
                    },
                    {   # get locations of different org (1) by org admin (2),
                        # forbidden
                        'test_name':
                            'test_get_org_1_locations_by_id_by_org_2_admin',
                        'args': None,
                        'data': {
                            'id': [
                                self.locations['location_1_org_1'].id,
                                self.locations['location_2_org_1'].id]
                        },
                        'user': 'org_2_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # get locations of different org (2) by sub-org
                        # admin (1), forbidden
                        'test_name':
                            'test_get_org_2_locations_by_id_by_sub_org_1_admin',
                        'args': None,
                        'data': {
                            'id': [
                                self.locations['location_1_org_2'].id,
                                self.locations['location_2_org_2'].id]
                        },
                        'user': 'sub_org_11_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # get locations of same org (1) by sub-org
                        # admin (1), forbidden
                        'test_name':
                            'test_get_org_1_locations_by_id_by_sub_org_1_admin',
                        'args': None,
                        'data': {
                            'id': [
                                self.locations['location_1_org_1'].id,
                                self.locations['location_1_org_2'].id]
                        },
                        'user': 'sub_org_11_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # get locations of same org (1) by sub-org
                        # admin (1), okay
                        'test_name':
                            'test_get_sub_org_1_locations_by_id_by_sub_org_1_admin',
                        'args': None,
                        'data': {
                            'id': [
                                self.locations['location_1_sub_1_org_1'].id,
                                self.locations['location_2_sub_1_org_1'].id]
                        },
                        'user': 'sub_org_11_admin_user',
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(len(data['results']), 2)
                        )
                    },
                    {   # get locations of org (1) by org admin (1),
                        # should work
                        'test_name':
                            'test_get_org_1_locations_by_id_by_org_1_admin',
                        'args': None,
                        'data': {
                            'id': [
                                self.locations['location_1_org_1'].id,
                                self.locations['location_2_org_1'].id]
                        },
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(len(data['results']), 2)
                        )
                    },
                    {   # get authorized locations list of locations by
                        # employee
                        'test_name':
                            'test_get_auth_locations_by_sub_org_1_employee',
                        'args': None,
                        'data': {
                            'id': [
                                self.locations['location_1_sub_1_org_1'].id,
                                self.locations['location_2_sub_1_org_1'].id]
                        },
                        'user': 'employee_user',
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(len(data['results']), 2)
                        )
                    },
                    {   # get unauthorized locations list of locations by
                        # employee
                        'test_name':
                            'test_get_unauth_locations_by_sub_org_1_employee',
                        'args': None,
                        'data': {
                            'id': [
                                self.locations['location_1_org_1'].id,
                                self.locations['location_2_org_1'].id]
                        },
                        'user': 'employee_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # get locations list of locations by some random user
                        'test_name': 'test_get_locations_by_other_user',
                        'args': None,
                        'data': {
                            'id': [
                                self.locations['location_1_org_1'].id,
                                self.locations['location_2_org_1'].id]
                        },
                        'user': 'other_user',
                        'status': status.HTTP_403_FORBIDDEN
                    }
                ]
            }
        ]

        test_create = [
            {
                'test_name': 'create_locations',
                'type': 'post',
                'path_name': 'locations_list_create_delete',
                'request': [
                    {   # create location, okay for staff
                        'test_name': 'create_location_by_staff',
                        'data': {
                            'name': 'My location',
                            'organization': self.orgs['org_1'].id
                        },
                        'user': 'staff_user',
                        'status': status.HTTP_201_CREATED,
                        'response_check': lambda test, data: (
                            test.assertEqual(data['name'], 'My location')
                        )
                    },
                    {   # duplicate create by staff, bad
                        'test_name': 'create_dup_location_by_staff',
                        'data': {
                            'name': 'My location',
                            'organization': self.orgs['org_1'].id
                        },
                        'user': 'staff_user',
                        'status': status.HTTP_400_BAD_REQUEST
                    },
                    {   # create location by org-admin, okay
                        'test_name': 'create_location_org_admin_1_in_org_1',
                        'data': {
                            'name': 'My location 1',
                            'organization': self.orgs['org_1'].id
                        },
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_201_CREATED,
                        'response_check': lambda test, data: (
                            test.assertEqual(data['name'], 'My location 1')
                        )
                    },
                    {   # create location by org-admin in lower tree, okay
                        'test_name': 'create_location_org_admin_1_in_sub_1_org_1',
                        'data': {
                            'name': 'My location 2',
                            'organization': self.orgs['sub_1_org_1'].id
                        },
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_201_CREATED,
                        'response_check': lambda test, data: (
                            test.assertEqual(data['name'], 'My location 2')
                        )
                    },
                    {   # create location by org-admin in other organization,
                        # bad
                        'test_name': 'create_location_org_admin_1_in_org_2',
                        'data': {
                            'name': 'My location 3',
                            'organization': self.orgs['org_2'].id
                        },
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_400_BAD_REQUEST
                    },
                    {   # create location by org-admin in other organization
                        # lower tree, bad
                        'test_name': 'create_location_org_admin_1_in_sub_1_org_2',
                        'data': {
                            'name': 'My location 4',
                            'organization': self.orgs['sub_1_org_2'].id
                        },
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_400_BAD_REQUEST
                    },
                    {   # create location by sub-org-admin in upper tree, bad
                        'test_name': 'create_location_sub_org_admin_1_in_org_1',
                        'data': {
                            'name': 'My location 5',
                            'organization': self.orgs['org_1'].id
                        },
                        'user': 'sub_org_11_admin_user',
                        'status': status.HTTP_400_BAD_REQUEST
                    },
                    {   # create location by sub-org-admin in own tree, bad
                        'test_name': 'create_location_sub_org_admin_1_in_sub_1_org_1',
                        'data': {
                            'name': 'My location 6',
                            'organization': self.orgs['sub_1_org_1'].id
                        },
                        'user': 'sub_org_11_admin_user',
                        'status': status.HTTP_201_CREATED,
                        'response_check': lambda test, data: (
                            test.assertEqual(data['name'], 'My location 6')
                        )
                    },
                    {   # create location by random user, forbidden
                        'test_name': 'create_location_other_user',
                        'data': {
                            'name': 'My location 7',
                            'desc': 'No description',
                        },
                        'user': 'other_user',
                        'status': status.HTTP_403_FORBIDDEN
                    },
                ]
            }
        ]

        test_delete_multiple = [
            {
                'test_name': 'delete_multiple_locations',
                'type': 'delete',
                'path_name': 'locations_list_create_delete',
                'request': [
                    {   # delete location, okay for staff
                        'test_name': 'delete_location_by_staff',
                        'data': {
                            'id': [
                                self.locations['location_1_org_1'].id,
                                self.locations['location_2_org_1'].id]
                        },
                        'user': 'staff_user',
                        'status': status.HTTP_200_OK
                    },
                    {   # duplicate delete by staff, bad
                        'test_name': 'delete_dup_location_by_staff',
                        'data': {
                            'id': [
                                self.locations['location_1_org_1'].id,
                                self.locations['location_2_org_1'].id]
                        },
                        'user': 'staff_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # delete location by org-admin, okay
                        'test_name': 'delete_location_org_admin_2_in_org_2',
                        'data': {
                            'id': [
                                self.locations['location_1_org_2'].id,
                                self.locations['location_2_org_2'].id]
                        },
                        'user': 'org_2_admin_user',
                        'status': status.HTTP_200_OK
                    },
                    {   # delete location by org-admin in lower tree, okay
                        'test_name': 'delete_location_org_admin_1_in_sub_1_org_1',
                        'data': {
                            'id': [
                                self.locations['location_1_sub_1_org_1'].id]
                        },
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_200_OK
                    },
                    {   # delete location by org-admin in other organization,
                        # bad
                        'test_name': 'delete_location_org_admin_1_in_org_2',
                        'data': {
                            'id': [
                                self.locations['location_3_org_2'].id]
                        },
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # delete location by org-admin in other organization
                        # lower tree, bad
                        'test_name': 'delete_location_org_admin_1_in_sub_1_org_2',
                        'data': {
                            'id': [
                                self.locations['location_1_sub_1_org_2'].id]
                        },
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # delete location by sub-org-admin in upper tree, bad
                        'test_name': 'delete_location_sub_org_admin_1_in_org_1',
                        'data': {
                            'id': [
                                self.locations['location_4_org_1'].id,
                                self.locations['location_5_org_1'].id
                            ]
                        },
                        'user': 'sub_org_11_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # delete location by sub-org-admin in own tree, okay
                        'test_name': 'delete_location_sub_org_admin_1_in_sub_1_org_1',
                        'data': {
                            'id': [
                                self.locations['location_3_sub_1_org_1'].id,
                                self.locations['location_4_sub_1_org_1'].id
                            ]
                        },
                        'user': 'sub_org_11_admin_user',
                        'status': status.HTTP_200_OK
                    },
                    {   # delete location by employee user, forbidden
                        'test_name': 'delete_location_other_user',
                        'data': {
                            'id': [
                                self.locations['location_3_sub_1_org_1'].id,
                                self.locations['location_4_sub_1_org_1'].id
                            ]
                        },
                        'user': 'employee_user',
                        'status': status.HTTP_403_FORBIDDEN
                    },
                    {   # delete location by random user, forbidden
                        'test_name': 'delete_location_other_user',
                        'data': {
                            'id': [
                                self.locations['location_1_org_1'].id,
                                self.locations['location_2_org_2'].id
                            ]
                        },
                        'user': 'other_user',
                        'status': status.HTTP_403_FORBIDDEN
                    },
                ]
            }
        ]

        test_retrieve = [
            {
                'test_name': 'get_location_by_id',
                'type': 'get',
                'path_name': 'locations_rud',
                'request': [
                    {   # get location by id, okay for staff
                        'test_name': 'get_location_1_org_1_by_staff',
                        'args': [self.locations['location_1_org_1'].id],
                        'user': 'staff_user',
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                data['location']['id'],
                                str(self.locations['location_1_org_1'].id))
                        )
                    },
                    {   # get location by id, okay for org admin itself
                        'test_name': 'get_location_1_org_1_by_org_1_admin',
                        'args': [self.locations['location_1_org_1'].id],
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                data['location']['id'],
                                str(self.locations['location_1_org_1'].id))
                        )
                    },
                    {   # get location of org, forbidden for sub-org admin
                        'test_name': 'get_location_1_org_1_by_sub_org_1_admin',
                        'args': [self.locations['location_1_org_1'].id],
                        'user': 'sub_org_11_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # get location, bad for other org-admin
                        'test_name': 'get_location_1_org_1_by_org_2_admin',
                        'args': [self.locations['location_1_org_1'].id],
                        'user': 'org_2_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # get location by id, forbidden for random user
                        'test_name': 'get_location_1_org_1_by_other_user',
                        'args': [self.locations['location_1_org_1'].id],
                        'user': 'other_user',
                        'status': status.HTTP_403_FORBIDDEN
                    },
                ]
            },
            {
                'test_name': 'get_sub_location_by_id',
                'type': 'get',
                'path_name': 'locations_rud',
                'request': [
                    {   # get sub-org location by id, okay for staff
                        'test_name': 'get_location_1_sub_1_org_1_by_staff',
                        'args': [self.locations['location_1_sub_1_org_1'].id],
                        'user': 'staff_user',
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                data['location']['id'],
                                str(
                                    self.locations['location_1_sub_1_org_1'].id))
                        )
                    },
                    {   # get sub-org location by id, okay for org admin itself
                        # under which this sub-org exists
                        'test_name': 'get_location_1_sub_1_org_1_by_org_1_admin',
                        'args': [self.locations['location_1_sub_1_org_1'].id],
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                data['location']['id'],
                                str(
                                    self.locations['location_1_sub_1_org_1'].id))
                        )
                    },
                    {   # get sub-org location by id, okay for sub-org admin itself
                        'test_name': 'get_location_1_sub_1_org_1_by_sub_1_org_1_admin',
                        'args': [self.locations['location_1_sub_1_org_1'].id],
                        'user': 'sub_org_11_admin_user',
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                data['location']['id'],
                                str(
                                    self.locations['location_1_sub_1_org_1'].id))
                        )
                    },
                    {   # get sub-org location by id, bad for other
                        # org-admin under which this sub-org does not exist
                        'test_name': 'get_location_1_sub_1_org_1_by_org_2_admin',
                        'args': [self.locations['location_1_sub_1_org_1'].id],
                        'user': 'org_2_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # get sub-org location by id, bad for other
                        # sub-org admin to which this sub-org does not exist
                        'test_name': 'get_location_1_sub_1_org_1_by_sub_1_org_2_admin',
                        'args': [self.locations['location_1_sub_1_org_1'].id],
                        'user': 'sub_org_12_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # get employees auth location info, okay
                        'test_name': 'get_location_1_sub_1_org_1_by_employee',
                        'args': [self.locations['location_1_sub_1_org_1'].id],
                        'user': 'employee_user',
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                data['location']['id'],
                                str(self.locations['location_1_sub_1_org_1'].id))
                        )
                    },
                    {   # get employees unauth location info, bad
                        'test_name': 'get_location_1_sub_1_org_1_by_employee',
                        'args': [self.locations['location_1_sub_1_org_2'].id],
                        'user': 'employee_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # get sub-org by id, forbidden for random user
                        'test_name': 'get_location_1_sub_1_org_1_by_other_user',
                        'args': [self.locations['location_1_sub_1_org_1'].id],
                        'user': 'other_user',
                        'status': status.HTTP_403_FORBIDDEN
                    }
                ]
            }
        ]

        test_update = [
            {
                'test_name': 'update_location_by_id',
                'type': 'patch',
                'path_name': 'locations_rud',
                'request': [
                    {
                        # update location 1 org 1 by staff, okay
                        'test_name': 'update_location_1_org_1_by_staff',
                        'args': [self.locations['location_1_org_1'].id],
                        'user': 'staff_user',
                        'data': {
                            'name': 'location_1_org_1_updated',
                        },
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                data['location']['name'],
                                'location_1_org_1_updated')
                        )
                    },
                    {   # update location_1_org_1 by id by org_1 admin, okay
                        'test_name': 'update_location_1_org_1_by_org_1_admin',
                        'args': [self.locations['location_1_org_1'].id],
                        'user': 'org_1_admin_user',
                        'data': {
                            'name': 'location_1_org_1_updated',
                        },
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                data['location']['name'],
                                'location_1_org_1_updated')
                        )
                    },
                    {   # update location in higher level organization,
                        # no access
                        'test_name': 'update_location_1_org_1_by_sub_1_org_1_admin',
                        'args': [self.locations['location_1_org_1'].id],
                        'user': 'sub_org_11_admin_user',
                        'data': {
                            'name': 'location_1_org_1_updated',
                        },
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # update location of different org, bad
                        'test_name': 'update_location_1_org_1_by_org_2_admin',
                        'args': [self.locations['location_1_org_1'].id],
                        'user': 'org_2_admin_user',
                        'data': {
                            'name': 'location_1_org_1_updated',
                        },
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # update location in org by id, forbidden for employee
                        'test_name': 'update_location_1_sub_1_org_1_by_sub_org_1_employee',
                        'args': [self.locations['location_1_sub_1_org_1'].id],
                        'user': 'employee_user',
                        'data': {
                            'name': 'location_1_sub_1_org_1_updated',
                        },
                        'status': status.HTTP_403_FORBIDDEN
                    },
                    {   # update location by id, forbidden for random user
                        'test_name': 'update_location_1_sub_1_org_1_by_other_user',
                        'args': [self.locations['location_1_sub_1_org_1'].id],
                        'user': 'other_user',
                        'data': {
                            'name': 'location_1_sub_1_org_1_updated',
                        },
                        'status': status.HTTP_403_FORBIDDEN
                    }
                ]
            },
            {
                'test_name': 'update_sub_location_by_id',
                'type': 'patch',
                'path_name': 'locations_rud',
                'request': [
                    {   # update sub-org location by id, okay for staff
                        'test_name': 'update_location_1_sub_1_org_1_by_staff_user',
                        'args': [self.locations['location_1_sub_1_org_1'].id],
                        'user': 'staff_user',
                        'data': {
                            'name': 'location_1_sub_1_org_1_updated',
                        },
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                data['location']['name'],
                                'location_1_sub_1_org_1_updated')
                        )
                    },
                    {   # update sub-org by id, okay for org admin itself under
                        # which this sub-org exists
                        'test_name': 'update_location_1_sub_1_org_1_by_org_1_admin',
                        'args': [self.locations['location_1_sub_1_org_1'].id],
                        'user': 'org_1_admin_user',
                        'data': {
                            'name': 'location_1_sub_1_org_1_updated',
                        },
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                data['location']['name'],
                                'location_1_sub_1_org_1_updated')
                        )
                    },
                    {   # update sub-org location by id, okay for sub-org admin itself
                        'test_name': 'update_location_1_sub_1_org_1_by_sub_1_org_1_admin',
                        'args': [self.locations['location_1_sub_1_org_1'].id],
                        'user': 'sub_org_11_admin_user',
                        'data': {
                            'name': 'location_1_sub_1_org_1_updated',
                        },
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                data['location']['name'],
                                'location_1_sub_1_org_1_updated')
                        )
                    },
                    {   # test for bad duplicate name
                        'test_name': 'update_location_1_sub_1_org_2_by_sub_1_org_2_admin',
                        'args': [self.locations['location_1_sub_1_org_2'].id],
                        'user': 'sub_org_12_admin_user',
                        'data': {
                            'name': 'location_1_sub_1_org_1_updated',
                        },
                        'status': status.HTTP_400_BAD_REQUEST
                    }
                ]
            }
        ]

        test_delete = [
            {
                'test_name': 'delete_location_by_id',
                'type': 'patch',
                'path_name': 'locations_rud',
                'request': [
                    {
                        # delete location 1 org 1 by staff, okay
                        'test_name': 'delete_location_1_org_1_by_staff',
                        'args': [self.locations['location_1_org_1'].id],
                        'user': 'staff_user',
                        'status': status.HTTP_200_OK
                    },
                    {   # delete location_2_org_1 by id by org_1 admin, okay
                        'test_name': 'delete_location_2_org_1_by_org_1_admin',
                        'args': [self.locations['location_2_org_1'].id],
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_200_OK
                    },
                    {   # delete location in higher level organization,
                        # no access
                        'test_name': 'delete_location_1_org_2_by_sub_1_org_2_admin',
                        'args': [self.locations['location_1_org_2'].id],
                        'user': 'sub_org_12_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # delete location of different org, bad
                        'test_name': 'delete_location_1_org_1_by_org_2_admin',
                        'args': [self.locations['location_3_org_1'].id],
                        'user': 'org_2_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # delete location in org by id, forbidden for employee
                        'test_name': 'delete_location_1_sub_1_org_1_by_sub_org_1_employee',
                        'args': [self.locations['location_1_sub_1_org_1'].id],
                        'user': 'employee_user',
                        'status': status.HTTP_403_FORBIDDEN
                    },
                    {   # delete location by id, forbidden for random user
                        'test_name': 'delete_location_1_sub_1_org_1_by_other_user',
                        'args': [self.locations['location_1_sub_1_org_1'].id],
                        'user': 'other_user',
                        'status': status.HTTP_403_FORBIDDEN
                    }
                ]
            },
            {
                'test_name': 'delete_sub_location_by_id',
                'type': 'patch',
                'path_name': 'locations_rud',
                'request': [
                    {   # delete sub-org location by id, okay for staff
                        'test_name': 'delete_location_1_sub_1_org_1_by_staff_user',
                        'args': [self.locations['location_1_sub_1_org_1'].id],
                        'user': 'staff_user',
                        'status': status.HTTP_200_OK
                    },
                    {   # delete sub-org by id, okay for org admin itself under
                        # which this sub-org exists
                        'test_name': 'delete_location_2_sub_1_org_1_by_org_1_admin',
                        'args': [self.locations['location_2_sub_1_org_1'].id],
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_200_OK
                    },
                    {   # delete sub-org location by id, okay for sub-org admin itself
                        'test_name': 'delete_location_3_sub_1_org_1_by_sub_1_org_1_admin',
                        'args': [self.locations['location_3_sub_1_org_1'].id],
                        'user': 'sub_org_11_admin_user',
                        'status': status.HTTP_200_OK
                    },
                ]
            }
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

                response_check = None
                if 'response_check' in request:
                    response_check = request['response_check']

                response = self.call_api(
                    url,
                    data,
                    self.tokens[request['user']],
                    request['status'],
                    config['type'],
                    response_check=response_check)

    def test_all_sets(self):
        for test_set in self.test_sets:
            for test_config in test_set:
                self.run_single_test(test_config)
