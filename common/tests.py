import copy
from rest_framework.test import APITestCase, URLPatternsTestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import Group
from backend import settings
from users.models import AppUser
from organizations.models import Organization
from locations.models import Location, Floor, Block
from rest_framework_jwt.settings import api_settings

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
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

        :param org_names: List of organization names ['org_1',...'org_n']
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
                'sub_org_1: 'org_1',
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
                'location_1': 'org_1',
                ...
                'location_2': 'org_2',
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

    def create_floors(self, floors_dict, locations):
        """
        Creates new floors in the test database according to input
        floors dictionary mapping floors to locations

        :param floors_dict: Dict of floors, for example
            {
                'floor_0_location_1': {
                    'number': 0, 'location': 'location_1_org_1'},
                ...
                'floor_1_location_1': {
                    'number': 1, 'location': 'location_1_org_1'},
                'floor_n_location_1': {
                    'number': n, 'location': 'location_1_org_1'},
            }
        """
        floors = {}
        for (floor_name, mapping) in floors_dict.items():
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
                name=block_name,
                floor=floors.get(mapping['floor']))
            blocks[block_name].save()
        return blocks

    def create_users(self, users_dict, groups, orgs):
        """
        Creates new users in the test database according to input
        users dictionary mapping users to groups, sub-organizations and
        organizations

        :param users_dict: Dict of users, for example
            {
                'user_1': {
                    'group': 'group_1',
                    'organization': 'org_1',
                    'sub_organization': 'sub_org_1'
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
                groups[user_data['group']].user_set.add(
                    users[user_name])
                groups[user_data['group']].save()

            users[user_name].save()
            if JWT_AUTH:
                payload = jwt_payload_handler(users[user_name])
                tokens[user_name] = jwt_encode_handler(payload)
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
            e.name for e in settings.UserGroups]
        groups_list.append('OTHER_GROUP')
        self.groups = self.create_groups(groups_list)

        # generate test organizations
        orgs_list = ['org_1', 'org_2', 'org_3']
        self.orgs = self.create_orgs(orgs_list)

        # generate test sub organizations
        sub_orgs_dict = {
            'sub_1_org_1': 'org_1',
            'sub_2_org_1': 'org_1',
            'sub_1_org_2': 'org_2',
            'sub_2_org_2': 'org_2',
            'sub_3_org_2': 'org_2',
            'sub_1_org_3': 'org_3',
            'sub_2_org_3': 'org_3',
        }
        self.orgs.update(self.create_sub_orgs(sub_orgs_dict, self.orgs))

        # generate test locations
        locations_dict = {
            'location_1_org_1': 'org_1',
            'location_1_sub_org_1': 'sub_1_org_1',
            'location_2_org_1': 'org_1',
            'location_1_org_2': 'org_2',
            'location_2_org_2': 'org_2'
        }
        self.locations = self.create_locations(locations_dict, self.orgs)

        # generate test floors
        floors_dict = {
            'floor_0_location_1': {
                'number': 0, 'location': 'location_1_org_1'},
            'floor_1_location_1': {
                'number': 1, 'location': 'location_1_org_1'},
            'floor_2_location_1': {
                'number': 2, 'location': 'location_1_org_1'},
        }
        self.floors = self.create_floors(
            floors_dict, self.locations)

        # generate test blocks
        blocks_dict = {
            'block_0_floor_0_location_1': {
                'floor': 'floor_0_location_1'},
            'block_1_floor_0_location_1': {
                'floor': 'floor_0_location_1'},
            'block_2_floor_0_location_1': {
                'floor': 'floor_0_location_1'},
        }

        self.blocks = self.create_blocks(blocks_dict, self.floors)

        users_dict = {
            'staff_user': 'staff',
            'org_1_admin_user': {
                'group': settings.UserGroups.ORGANIZATION_ADMIN_GROUP.name,
                'organization': 'org_1',
            },
            'org_2_admin_user': {
                'group': settings.UserGroups.ORGANIZATION_ADMIN_GROUP.name,
                'organization': 'org_2',
            },
            'org_3_admin_user': {
                'group': settings.UserGroups.ORGANIZATION_ADMIN_GROUP.name,
                'organization': 'org_3',
            },
            'sub_org_11_admin_user': {
                'group': settings.UserGroups.ORGANIZATION_ADMIN_GROUP.name,
                'organization': 'sub_1_org_1',
            },
            'sub_org_12_admin_user': {
                'group': settings.UserGroups.ORGANIZATION_ADMIN_GROUP.name,
                'organization': 'sub_1_org_2',
            },
            'sub_org_21_admin_user': {
                'group': settings.UserGroups.ORGANIZATION_ADMIN_GROUP.name,
                'organization': 'sub_2_org_1',
            },
            'sub_org_22_admin_user': {
                'group': settings.UserGroups.ORGANIZATION_ADMIN_GROUP.name,
                'organization': 'sub_2_org_2',
            },
            'sub_org_13_admin_user': {
                'group': settings.UserGroups.ORGANIZATION_ADMIN_GROUP.name,
                'organization': 'sub_1_org_3',
            },
            'sub_org_23_admin_user': {
                'group': settings.UserGroups.ORGANIZATION_ADMIN_GROUP.name,
                'organization': 'sub_2_org_2',
            },
            'employee_user': {
                'group': settings.UserGroups.EMPLOYEE_GROUP.name,
                'organization': 'sub_1_org_1',
            },
            'other_user': {
                'group': 'OTHER_GROUP',
                'organization': None,
                'sub_organization': None
            },
        }
        self.users, self.tokens = self.create_users(
            users_dict, self.groups, self.orgs)

    def call_api(
            self,
            url,
            data,
            token,
            status_code,
            api_type,
            debug=True,
            make_assert=True):

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
        self.assertEqual(response.status_code, status_code)
        return response
