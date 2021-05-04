"""
Defines the unit tests related to 'list-by-id-list' api requests for this
application.
"""
from django.urls import include, path
from rest_framework import status

from core.tests import TestsBase


# pylint: disable=pointless-string-statement
class FloorListByIdListTests(TestsBase):
    """
    Defines unit tests for 'list-by-id-list' api requests for views defined
    at 'locations/' url.
    """

    """Define the api url patterns used in this test unit."""
    api_urlpatterns = [
        path('locations/floors/', include('locations.api.urls')),
    ]

    """Define the the complete url pattern used in this test unit."""
    urlpatterns = [
        path('api/v1/', include(api_urlpatterns)),
    ]

    def setUp(self):
        """
        Sets up the test cases.
        """
        super(FloorListByIdListTests, self).setUp()
        self.test = [
            {
                'test_name': 'get_floors_list_multiple',
                'type': 'get',
                'path_name': 'floors_list_create_delete',
                'request': [
                    {   # get floors list by staff
                        'test_name': 'test_get_floors_list_by_ids_by_staff',
                        'query_params': [
                            ('id', self.floors['f0_l1_o1'].id),
                            ('id', self.floors['f1_l1_o1'].id),
                            ('id', self.floors['f2_l1_o1'].id),
                        ],
                        'user': 'staff_user',
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(len(data.get('results', None)), 3)
                        )
                    },
                    {   # get floors of different org (1) by org admin (2),
                        # forbidden
                        'test_name':
                            'test_get_org_1_floors_by_id_by_org_2_admin',
                        'query_params': [
                            ('id', self.floors['f0_l1_o1'].id),
                            ('id', self.floors['f1_l1_o1'].id),
                        ],
                        'user': 'org_2_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # get floors of different org (2) by sub-org
                        # admin (1), forbidden
                        'test_name':
                            'test_get_org_2_floors_by_id_by_sub_org_1_admin',
                        'query_params': [
                            ('id', self.floors['f0_l1_o2'].id),
                            ('id', self.floors['f1_l1_o2'].id),
                        ],
                        'user': 'sub_org_11_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # get floors of same org (1) by sub-org
                        # admin (1), forbidden
                        'test_name':
                            'test_get_org_1_floors_by_id_by_sub_org_1_admin',
                        'query_params': [
                            ('id', self.floors['f0_l1_o1'].id),
                            ('id', self.floors['f1_l1_o1'].id),
                        ],
                        'user': 'sub_org_11_admin_user',
                        'status': status.HTTP_404_NOT_FOUND
                    },
                    {   # get floors of same org (1) by sub-org
                        # admin (1), okay
                        'test_name':
                            'test_get_sub_org_1_floors_by_id_by_sub_org_1_'
                            'admin',
                        'query_params': [
                            ('id', self.floors['f0_l1_sub1_o1'].id),
                            ('id', self.floors['f1_l1_sub1_o1'].id),
                        ],
                        'user': 'sub_org_11_admin_user',
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(len(data.get('results', None)), 2)
                        )
                    },
                    {   # get floors of org (1) by org admin (1),
                        # should work
                        'test_name':
                            'test_get_org_1_floors_by_id_by_org_1_admin',
                        'query_params': [
                            ('id', self.floors['f0_l1_o1'].id),
                            ('id', self.floors['f1_l1_o1'].id),
                        ],
                        'user': 'org_1_admin_user',
                        'status': status.HTTP_200_OK,
                        'response_check': lambda test, data: (
                            test.assertEqual(len(data.get('results', None)), 2)
                        )
                    },
                    {   # get list of floors by some random user
                        'test_name': 'test_get_floors_by_other_user',
                        'query_params': [
                            ('id', self.floors['f0_l1_o1'].id),
                            ('id', self.floors['f1_l1_o1'].id),
                        ],
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
