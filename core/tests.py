"""
Defines the base functionality for unit tests generation for our applications.
"""

from django.contrib.auth.models import Group
from django.core.management import call_command
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase, URLPatternsTestCase
from rest_framework_jwt.settings import api_settings

from locations.models import Block, Floor, Location
from organizations.models import Organization
from users.models import AppUser

from .permissions import UserGroups

# define payload handler for generating JWT token in tests
JWT_PAYLOAD_HANDLER = api_settings.JWT_PAYLOAD_HANDLER

# define encode handler for generating JWT token in tests
JWT_ENCODE_HANDLER = api_settings.JWT_ENCODE_HANDLER

# use JWT authentication tokens?
JWT_AUTH = True


class TestsBase(APITestCase, URLPatternsTestCase):
    """
    Generates a test database with example values for different models for
    performing tests
    """

    def create_groups(self, group_names):
        """
        Creates new groups with given name list in the test database

        :param group_names: List of group names ['group_1',...'group_n']
        """
        groups = {}
        for group_name in group_names:
            groups[group_name] = Group(name=group_name)
            groups[group_name].save()
        return groups

    def create_orgs(self, org_names):
        """
        Creates new organizations with given name list in the test database

        :param org_names: List of organization names ['o1',...'org_n']
        """
        orgs = {}
        for org_name in org_names:
            orgs[org_name] = Organization(name=org_name)
            orgs[org_name].save()
        return orgs

    def create_sub_orgs(self, sub_org_dict, orgs):
        """
        Creates new sub-organizations with input sub-organization dictionary
        mapping sub-organizations to organizations in the test database
        :param sub_org_dict: Dict of sub_organization, for example
            {
                'sub_org_1: 'o1',
                ...
                'sub_org_n': 'org_n'
            }
        """
        sub_orgs = {}
        for (sub_org_name, org_name) in sub_org_dict.items():
            sub_orgs[sub_org_name] = Organization(
                name=sub_org_name, parent=orgs.get(org_name))
            sub_orgs[sub_org_name].save()
        return sub_orgs

    def create_locations(self, locations_dict, orgs):
        """
        Creates new locations in the test database according to input
        locations dictionary mapping locations to organizations

        :param locations_dict: Dict of locations, for example
            {
                'location_1': 'o1',
                ...
                'location_2': 'o2',
                'location_n': 'sub_org_n',
            }
        """
        locations = {}
        for (location_name, org_name) in locations_dict.items():
            locations[location_name] = Location(
                name=location_name,
                organization=orgs.get(org_name))
            locations[location_name].save()
        return locations

    def create_floors(self, fs_names, locations):
        """
        Creates new floors in the test database according to input
        floors dictionary mapping floors to locations

        :param fs_names: Dict of floors, for example
            {
                'floor_0_location_1': {
                    'number': 0, 'location': 'l1_o1'},
                ...
                'floor_1_location_1': {
                    'number': 1, 'location': 'l1_o1'},
                'floor_n_location_1': {
                    'number': n, 'location': 'l1_o1'},
            }
        """
        floors = {}
        for (floor_name, mapping) in fs_names.items():
            floors[floor_name] = Floor(
                number=mapping['number'],
                location=locations.get(mapping['location']))
            floors[floor_name].save()
        return floors

    def create_blocks(self, blocks_dict, floors):
        """
        Creates new blocks in the test database according to input
        blocks dictionary mapping blocks to floors

        :param blocks_dict: Dict of blocks, for example
            {
                'block_0_floor_0_location_1': {
                    'floor': 'floor_0_location_1'},
                ...
                'block_1_floor_0_location_1': {
                    'floor': 'floor_0_location_1'},
                'block_n_floor_0_location_1': {
                    'floor': 'floor_0_location_1'},
            }
        """
        blocks = {}
        for (block_name, mapping) in blocks_dict.items():
            blocks[block_name] = Block(
                name=mapping['name'],
                pixels_to_m_x=mapping['pixels_to_m_x'],
                pixels_to_m_y=mapping['pixels_to_m_y'],
                floor_map=mapping['floor_map'],
                floor=floors.get(mapping['floor']))
            blocks[block_name].save()
        return blocks

    def create_users(self, users_dict, groups, orgs, locations):
        """
        Creates new users in the test database according to input
        users dictionary mapping users to groups, sub-organizations and
        organizations

        :param users_dict: Dict of users, for example
            {
                'user_1': {
                    'group': 'group_1',
                    'organization': 'o1',
                    'sub_organization': 'sub_org_1',
                },
                ...
                'user_2': {
                    'group': 'group_2',
                    'organization': None,
                    'sub_organization': None
                },
                'user_n': {
                    'group': 'group_n',
                    'organization': 'org_n',
                    'sub_organization': 'sub_org_n'
                },
            }

        For employees, authorized_locations must be provided like this:
        'employee_user': {
                    'group': 'employee',
                    'organization': 'o1',
                    'sub_organization': 'sub_org_1',
                    'authorized_locations': [
                        'l1_sub1_o1',
                        'l2_sub1_o1'
                    ]
                },
        """
        users = {}
        tokens = {}
        for (user_name, user_data) in users_dict.items():
            if user_data == "staff":
                users[user_name] = AppUser.objects.create_superuser(
                    username=user_name,
                    email='{}@test.com'.format(user_name),
                    password='abcd1234@')
            else:
                users[user_name] = AppUser.objects.create_user(
                    username=user_name,
                    email='{}@test.com'.format(user_name),
                    password='abcd1234@',
                    organization=orgs.get(user_data.get('organization')))
                if 'authorized_locations' in user_data:
                    for location_name in user_data.get('authorized_locations'):
                        location = locations.get(location_name)
                        users[user_name].authorized_locations.add(location)
                groups[user_data['group']].user_set.add(
                    users[user_name])
                groups[user_data['group']].save()

            users[user_name].save()
            if JWT_AUTH:
                payload = JWT_PAYLOAD_HANDLER(users[user_name])
                tokens[user_name] = JWT_ENCODE_HANDLER(payload)
            else:
                tokens[user_name] = Token.objects.create(user=users[user_name])
                tokens[user_name].save()
        return users, tokens

    def setUp(self):
        """
        Sets up the test database with example values for different models
        """
        # generate test groups
        groups_list = [
            e.name for e in UserGroups]
        groups_list.append('OTHER_GROUP')
        self.groups = self.create_groups(groups_list)

        # generate test organizations
        self.os_names = [
            'o1',
            'o2',
            'o3',
            'o4_for_deletion',
            'o5_for_deletion']

        # generate organizations in database
        self.orgs = self.create_orgs(self.os_names)

        # generate sub organizations of org_1
        self.subs_o1_names = {
            'sub1_o1': 'o1',
            'sub2_o1': 'o1',
            'sub3_o1_for_deletion': 'o1',
            'sub4_o1_for_deletion': 'o1',
            'sub5_o1_for_deletion': 'o1',
        }

        # generate sub organizations of org_2
        self.subs_o2_names = {
            'sub1_o2': 'o2',
            'sub2_o2': 'o2',
            'sub3_o2': 'o2',
            'sub4_o2_for_deletion': 'o2',
            'sub5_o2_for_deletion': 'o2',
        }

        # generate sub organizations of org_3
        self.subs_o3_names = {
            'sub1_o3': 'o3',
            'sub2_o3': 'o3',
            'sub3_o3_for_deletion': 'o3',
        }

        # generate sub organizations of org_4
        self.subs_o4_names = {
            'sub1_o4': 'o4_for_deletion'
        }

        # generate sub organizations dictionary
        self.subs_names = {
            **self.subs_o1_names,
            **self.subs_o2_names,
            **self.subs_o3_names,
            **self.subs_o4_names,
        }

        # update organizations list with sub_organizations in database
        self.orgs.update(self.create_sub_orgs(self.subs_names, self.orgs))

        # generate locations of org_1
        self.ls_o1_names = {
            'l1_o1': 'o1',
            'l2_o1': 'o1',
            'l3_o1': 'o1',
            'l4_o1': 'o1',
            'l5_o1': 'o1',
        }

        # generate locations of sub_1_org_1
        self.ls_sub1_o1_names = {
            'l1_sub1_o1': 'sub1_o1',
            'l2_sub1_o1': 'sub1_o1',
            'l3_sub1_o1': 'sub1_o1',
            'l4_sub1_o1': 'sub1_o1',
        }

        # generate locations of org_2
        self.ls_o2_names = {
            'l1_o2': 'o2',
            'l2_o2': 'o2',
            'l3_o2': 'o2',
            'l4_o2': 'o2',
        }

        # generate locations of sub_1_org_2
        self.ls_sub1_o2_names = {
            'l1_sub1_o2': 'sub1_o2',
            'l2_sub1_o2': 'sub1_o2',
        }

        # generate locations of org_3
        self.ls_o3_names = {
            'l1_o3': 'o3',
            'l2_o3': 'o3',
        }

        # generate locations dictionary
        self.ls_names = {
            **self.ls_o1_names,
            **self.ls_sub1_o1_names,
            **self.ls_o2_names,
            **self.ls_sub1_o2_names,
            **self.ls_o3_names,
        }

        # generate locations in database
        self.locations = self.create_locations(self.ls_names, self.orgs)

        # generate test floors
        self.fs_l1_o1_names = {
            'f0_l1_o1': {
                'number': 0, 'location': 'l1_o1'},
            'f1_l1_o1': {
                'number': 1, 'location': 'l1_o1'},
            'f2_l1_o1': {
                'number': 2, 'location': 'l1_o1'},
            'f3_l1_o1_for_deletion': {
                'number': 3, 'location': 'l1_o1'},
            'f4_l1_o1_for_deletion': {
                'number': 4, 'location': 'l1_o1'},
        }

        self.fs_l1_sub1_o1_names = {
            'f0_l1_sub1_o1': {
                'number': 0, 'location': 'l1_sub1_o1'},
            'f1_l1_sub1_o1': {
                'number': 1, 'location': 'l1_sub1_o1'},
            'f2_l1_sub1_o1': {
                'number': 2, 'location': 'l1_sub1_o1'},
            'f3_l1_sub1_o1': {
                'number': 3, 'location': 'l1_sub1_o1'},
            'f4_l1_sub1_o1': {
                'number': 4, 'location': 'l1_sub1_o1'},
        }

        self.fs_l1_o2_names = {
            'f0_l1_o2': {
                'number': 0, 'location': 'l1_o2'},
            'f1_l1_o2': {
                'number': 1, 'location': 'l1_o2'},
            'f2_l1_o2': {
                'number': 2, 'location': 'l1_o2'},
        }

        self.fs_l1_sub1_o2_names = {
            'f0_l1_sub1_o2': {
                'number': 0, 'location': 'l1_sub1_o2'},
        }

        self.fs_names = {
            **self.fs_l1_o1_names,
            **self.fs_l1_sub1_o1_names,
            **self.fs_l1_o2_names,
            **self.fs_l1_sub1_o2_names,
        }

        self.floors = self.create_floors(
            self.fs_names, self.locations)

        # generate test blocks
        self.bs_f0_l1_o1_names = {
            'b1_f0_l1_o1': {
                'name': 'b1',
                'pixels_to_m_x': 40,
                'pixels_to_m_y': 40,
                'floor_map': self.get_test_floor_map_image(),
                'floor': 'f0_l1_o1'},
            'b2_f0_l1_o1': {
                'name': 'b2',
                'pixels_to_m_x': 40,
                'pixels_to_m_y': 40,
                'floor_map': self.get_test_floor_map_image(),
                'floor': 'f0_l1_o1'},
            'b3_f0_l1_o1_for_deletion': {
                'name': 'b3',
                'pixels_to_m_x': 40,
                'pixels_to_m_y': 40,
                'floor_map': self.get_test_floor_map_image(),
                'floor': 'f0_l1_o1'},
            'b4_f0_l1_o1_for_deletion': {
                'name': 'b4',
                'pixels_to_m_x': 40,
                'pixels_to_m_y': 40,
                'floor_map': self.get_test_floor_map_image(),
                'floor': 'f0_l1_o1'},
            'b5_f0_l1_o1_for_deletion': {
                'name': 'b5',
                'pixels_to_m_x': 40,
                'pixels_to_m_y': 40,
                'floor_map': self.get_test_floor_map_image(),
                'floor': 'f0_l1_o1'},
            'b6_f0_l1_o1_for_deletion': {
                'name': 'b6',
                'pixels_to_m_x': 40,
                'pixels_to_m_y': 40,
                'floor_map': self.get_test_floor_map_image(),
                'floor': 'f0_l1_o1'},
        }

        self.bs_f1_l1_o1_names = {
            'b1_f1_l1_o1': {
                'name': 'b1',
                'pixels_to_m_x': 40,
                'pixels_to_m_y': 40,
                'floor_map': self.get_test_floor_map_image(),
                'floor': 'f1_l1_o1'},
            'b2_f1_l1_o1': {
                'name': 'b2',
                'pixels_to_m_x': 40,
                'pixels_to_m_y': 40,
                'floor_map': self.get_test_floor_map_image(),
                'floor': 'f1_l1_o1'},
        }

        self.bs_f0_l1_sub1_o1_names = {
            'b1_f0_l1_sub1_o1': {
                'name': 'b1',
                'pixels_to_m_x': 40,
                'pixels_to_m_y': 40,
                'floor_map': self.get_test_floor_map_image(),
                'floor': 'f0_l1_sub1_o1'},
            'b2_f0_l1_sub1_o1': {
                'name': 'b2',
                'pixels_to_m_x': 40,
                'pixels_to_m_y': 40,
                'floor_map': self.get_test_floor_map_image(),
                'floor': 'f0_l1_sub1_o1'},
            'b3_f0_l1_sub1_o1_for_deletion': {
                'name': 'b3',
                'pixels_to_m_x': 40,
                'pixels_to_m_y': 40,
                'floor_map': self.get_test_floor_map_image(),
                'floor': 'f0_l1_sub1_o1'},
            'b4_f0_l1_sub1_o1_for_deletion': {
                'name': 'b4',
                'pixels_to_m_x': 40,
                'pixels_to_m_y': 40,
                'floor_map': self.get_test_floor_map_image(),
                'floor': 'f0_l1_sub1_o1'},
            'b5_f0_l1_sub1_o1_for_deletion': {
                'name': 'b5',
                'pixels_to_m_x': 40,
                'pixels_to_m_y': 40,
                'floor_map': self.get_test_floor_map_image(),
                'floor': 'f0_l1_sub1_o1'},
        }

        self.bs_f0_l1_o2_names = {
            'b1_f0_l1_o2': {
                'name': 'b1',
                'pixels_to_m_x': 40,
                'pixels_to_m_y': 40,
                'floor_map': self.get_test_floor_map_image(),
                'floor': 'f0_l1_o2'},
            'b2_f0_l1_o2_for_deletion': {
                'name': 'b2',
                'pixels_to_m_x': 40,
                'pixels_to_m_y': 40,
                'floor_map': self.get_test_floor_map_image(),
                'floor': 'f0_l1_o2'},
            'b3_f0_l1_o2_for_deletion': {
                'name': 'b3',
                'pixels_to_m_x': 40,
                'pixels_to_m_y': 40,
                'floor_map': self.get_test_floor_map_image(),
                'floor': 'f0_l1_o2'},
        }

        self.bs_f0_l1_sub1_o2_names = {
            'b1_f0_l1_sub1_o2': {
                'name': 'b1',
                'pixels_to_m_x': 40,
                'pixels_to_m_y': 40,
                'floor_map': self.get_test_floor_map_image(),
                'floor': 'f0_l1_sub1_o2'},
            'b2_f0_l1_sub1_o2_for_deletion': {
                'name': 'b2',
                'pixels_to_m_x': 40,
                'pixels_to_m_y': 40,
                'floor_map': self.get_test_floor_map_image(),
                'floor': 'f0_l1_sub1_o2'},
            'b3_f0_l1_sub1_o2_for_deletion': {
                'name': 'b3',
                'pixels_to_m_x': 40,
                'pixels_to_m_y': 40,
                'floor_map': self.get_test_floor_map_image(),
                'floor': 'f0_l1_sub1_o2'},
        }

        self.bs_names = {
            **self.bs_f0_l1_o1_names,
            **self.bs_f1_l1_o1_names,
            **self.bs_f0_l1_sub1_o1_names,
            **self.bs_f0_l1_o2_names,
            **self.bs_f0_l1_sub1_o2_names
        }

        # generate blocks in database
        self.blocks = self.create_blocks(self.bs_names, self.floors)

        # make a list of users with respective properties
        self.users_dict = {
            'staff_user': 'staff',
            'org_1_admin_user': {
                'group': UserGroups.ORGANIZATION_ADMIN_GROUP.name,
                'organization': 'org_1',
            },
            'org_2_admin_user': {
                'group': UserGroups.ORGANIZATION_ADMIN_GROUP.name,
                'organization': 'org_2',
            },
            'org_3_admin_user': {
                'group': UserGroups.ORGANIZATION_ADMIN_GROUP.name,
                'organization': 'org_3',
            },
            'org_4_admin_user': {
                'group': UserGroups.ORGANIZATION_ADMIN_GROUP.name,
                'organization': 'org_4_for_deletion',
            },
            'sub_org_11_admin_user': {
                'group': UserGroups.ORGANIZATION_ADMIN_GROUP.name,
                'organization': 'sub_1_org_1',
            },
            'sub_org_12_admin_user': {
                'group': UserGroups.ORGANIZATION_ADMIN_GROUP.name,
                'organization': 'sub_1_org_2',
            },
            'sub_org_21_admin_user': {
                'group': UserGroups.ORGANIZATION_ADMIN_GROUP.name,
                'organization': 'sub_2_org_1',
            },
            'sub_org_22_admin_user': {
                'group': UserGroups.ORGANIZATION_ADMIN_GROUP.name,
                'organization': 'sub_2_org_2',
            },
            'sub_org_13_admin_user': {
                'group': UserGroups.ORGANIZATION_ADMIN_GROUP.name,
                'organization': 'sub_1_org_3',
            },
            'sub_org_23_admin_user': {
                'group': UserGroups.ORGANIZATION_ADMIN_GROUP.name,
                'organization': 'sub_2_org_3',
            },
            'sub_org_14_admin_user': {
                'group': UserGroups.ORGANIZATION_ADMIN_GROUP.name,
                'organization': 'sub_1_org_4',
            },
            'employee_user': {
                'group': UserGroups.EMPLOYEE_GROUP.name,
                'organization': 'sub_1_org_1',
                'authorized_locations': [
                    'location_1_sub_1_org_1',
                    'location_2_sub_1_org_1'
                ]
            },
            'other_user': {
                'group': 'OTHER_GROUP',
                'organization': None,
                'sub_organization': None
            },
        }

        # generate users and their tokens in database
        self.users, self.tokens = self.create_users(
            self.users_dict, self.groups, self.orgs, self.locations)

        # call the setup_apps command to generate any common functionality
        # added separately in the applications.
        call_command('setup_apps')

    def run_single_test(self, config):
        """
        Runs a single test as defined in the config. Each test contains
        multiple sub-tests that are called separately.

        :param config: The test configuration. An example configuration is
            shown below:

        config = {
                # name of the test
                'test_name': 'test_name',

                # (get, patch, delete, post, etc)
                'type': 'get',

                # view url name as defined in urls.py
                'path_name': 'url_name',

                # A list of requests. Each request is a sub-test hitting the
                # specified url with specified type
                'request': [
                    {
                        # sub test name
                        'test_name': 'sub_test_1',

                        # query parameters to send
                        'args': [query_param_1, query_param_2],

                        # user that is calling the request
                        'user': 'staff_user',

                        # data to be sent, for example, for post requests
                        'data': {
                            'data1': 'data1',
                            'data2': 'data2',
                        },

                        # return status code that should be matched for a
                        # successful run. Test fails if the returned status
                        # code is different from this one
                        'status': status.HTTP_200_OK,

                        # a lambda function that asserts the returned response.
                        # the lambda takes the returned response data and
                        # performs any necessary assertions for the test.
                        'response_check': lambda test, data: (
                            test.assertEqual(
                                data['name'],
                                'data1')
                        )
                    },
                    {...},
                    ...
                    {...},
        """
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

                self.call_api(
                    url,
                    data,
                    self.tokens[request['user']],
                    request['status'],
                    config['type'],
                    response_check=response_check)

    def call_api(
            self,
            url,
            data,
            token,
            status_code,
            api_type,
            response_check=None,
            debug=True):
        """
        Calls the rest api for tests cases as defined by the input parameters.
        """

        if JWT_AUTH:
            auth_string = 'JWT {}'.format(token)
        else:
            auth_string = 'Token {}'.format(token)

        rest_fn = None
        if api_type == 'get':
            rest_fn = self.client.get
        elif api_type == 'post':
            rest_fn = self.client.post
        elif api_type == 'put':
            rest_fn = self.client.put
        elif api_type == 'patch':
            rest_fn = self.client.patch
        elif api_type == 'delete':
            rest_fn = self.client.delete
        else:
            print(
                "Invalid API function type provided. Allowed types are: "
                "[get, post, put, patch, delete]")

        if data:
            response = rest_fn(
                url,
                data=data,
                format='json',
                HTTP_AUTHORIZATION=auth_string)
        else:
            response = rest_fn(
                url,
                HTTP_AUTHORIZATION=auth_string)
        if debug:
            if response.status_code != status_code:
                print('response:', response.data)
        if response_check:
            response_check(self, response.data)
        self.assertEqual(response.status_code, status_code)
        return response
