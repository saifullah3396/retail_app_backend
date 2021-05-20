"""
Defines the base functionality for unit tests generation for our applications.
"""

import random
import tempfile

from django.conf import settings as django_settings
from django.contrib.auth.models import Group
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.urls import reverse
from django.utils import timezone
from django.utils.http import urlencode
from organizations.models import Organization
from rest_framework.authtoken.models import Token
from rest_framework.test import APITransactionTestCase, URLPatternsTestCase
from rest_framework_jwt.settings import api_settings

from backend.settings import MEDIA_ROOT
from cameras.models import Camera
from ds_servers.models import DSServer
from locations.models import Block, Floor, Location
from measurement_frames.models import MeasurementFrame
from users.models import AppUser

from .permissions import UserGroups

# define payload handler for generating JWT token in tests
JWT_PAYLOAD_HANDLER = api_settings.JWT_PAYLOAD_HANDLER

# define encode handler for generating JWT token in tests
JWT_ENCODE_HANDLER = api_settings.JWT_ENCODE_HANDLER

# use JWT authentication tokens?
JWT_AUTH = True


class TestsBase(APITransactionTestCase, URLPatternsTestCase):
    # pylint: disable=attribute-defined-outside-init
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

    def create_orgs_from_data(self, data, orgs=None):
        """
        Creates new organizations with given data

        :param data: Data of type {
                'o1': { 'name': 'o1' },
                ...
                'o2': { 'name': 'o2' },
                'o3': { 'name': 'o3', parent: 'o1' },
            }
        :parma orgs: List of already created organizations for parent
            assignment
        """
        item_dict = {}
        for (item_name, data) in data.items():
            if orgs:
                item_dict[item_name] = Organization(
                    name=data['name'],
                    parent=orgs.get(data['parent']))
            else:
                item_dict[item_name] = Organization(name=data['name'])
            item_dict[item_name].save()
        return item_dict

    def create_locations_from_data(self, data, orgs):
        """
        Creates new locations with given data

        :param data: Data of type {
                'l1': { 'name': 'l1, organization: 'o1' },
                ...
                'l2': { 'name': 'l2', organization: 'o2' },
                'l3': { 'name': 'l3', organization: 'o1' },
            }
        :parma orgs: List of already created organizations for parent
            assignment
        """
        item_dict = {}
        for (item_name, data) in data.items():
            item_dict[item_name] = \
                Location(
                    name=data['name'],
                    organization=orgs.get(data['organization']))
            item_dict[item_name].save()
        return item_dict

    def create_floors_from_data(self, data, locations):
        """
        Creates new floors with given data

        :param data: Data of type {
                'f0_l1': {
                    'number': 0, 'location': 'l1_o1'},
                ...
                'f1_l1': {
                    'number': 1, 'location': 'l1_o1'},
                'fn_l1': {
                    'number': n, 'location': 'l1_o1'},
            }
        :parma locations: List of already created locations
        """
        item_dict = {}
        for (item_name, data) in data.items():
            item_dict[item_name] = Floor(
                number=data['number'],
                location=locations.get(data['location']))
            item_dict[item_name].save()
        return item_dict

    def create_blocks_from_data(self, data, floors):
        """
        Creates new blocks with given data

        :param data: Data of type {
                'b0_f0_l1': { 'floor': 'f0', **data },
                ...
                'b1_f0_l1': { 'floor': 'f0', **data },
                'b2_f2_l1': { 'floor': 'f2', **data },
            }
        :parma floors: List of already created floors
        """
        item_dict = {}
        for (item_name, data) in data.items():
            item_dict[item_name] = Block(
                name=data['name'],
                pixels_to_m_x=data['pixels_to_m_x'],
                pixels_to_m_y=data['pixels_to_m_y'],
                floor_map=data['floor_map'],
                floor=floors.get(data['floor']))
            item_dict[item_name].save()
        return item_dict

    def create_frames_from_data(self, data, blocks):
        """
        Creates new frames with given data

        :param data: Data of type {
                'f0': { 'block': 'b0_f1_l1', **data },
                ...
                'f1': { 'block': 'b0_f2_l1', **data },
            }
        :parma blocks: List of already created blocks
        """
        item_dict = {}
        for (item_name, data) in data.items():
            item_dict[item_name] = MeasurementFrame(
                name=data['name'],
                pixel_pose_x=data['pixel_pose_x'],
                pixel_pose_y=data['pixel_pose_y'],
                pixel_pose_theta=data['pixel_pose_theta'],
                block=blocks.get(data['block']))
            item_dict[item_name].save()
        return item_dict

    def create_servers_from_data(self, data, orgs):
        """
        Creates new deepstream servers with given data

        :param data: Data of type {
                'd0': { 'block': 'b0_f1_l1', **data },
                ...
                'd1': { 'block': 'b0_f2_l1', **data },
            }
        :parma orgs: List of already created organizations
        """
        item_dict = {}
        for (item_name, data) in data.items():
            item_dict[item_name] = DSServer(
                ip_addr=data['ip_addr'],
                mac_addr=data['mac_addr'],
                connected_at=data['connected_at'],
                last_echo_at=data['last_echo_at'],
                organization=orgs.get(data['organization']))
            item_dict[item_name].save()
        return item_dict

    def create_cameras_from_data(self, data, blocks):
        """
        Creates new cameras with given data

        :param data: Data of type {
                'c0': { 'block': 'b0_f1_l1', **data },
                ...
                'c1': { 'block': 'b0_f2_l1', **data },
            }
        :parma blocks: List of already created blocks
        """
        item_dict = {}
        for (item_name, data) in data.items():
            item_dict[item_name] = Camera(
                ip_addr=data['ip_addr'],
                coords=data['coords'],
                point_coords_in_frame=data['point_coords_in_frame'],
                point_coords_in_image=data['point_coords_in_image'],
                block=blocks.get(data['block']))
            item_dict[item_name].save()
        return item_dict

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

    def get_test_floor_map_image(self):
        """
        Returns an uploaded test image.
        """
        return SimpleUploadedFile(
            "test_image.png",
            content=open(
                "{}/maps/wing_l.png".format(MEDIA_ROOT), 'rb').read(),
            content_type='image/png')

    def generate_test_organizations(self):
        """
        Generates organizations data in test database for testing purposes.
        """
        def generate_organizations_for_parent(org_names, parent_name=None):
            item_dict = {}
            for name in org_names:
                if parent_name:
                    item_dict['{}_{}'.format(name, parent_name)] = {
                        'name': name,
                        'parent': parent_name
                    }
                else:
                    item_dict['{}'.format(name)] = {
                        'name': name
                    }
            return item_dict

        self.os_dict = \
            generate_organizations_for_parent(
                ['o1', 'o1', 'o2', 'o3', 'o4_del', 'o5_del'])

        # generate organizations in database
        self.orgs = self.create_orgs_from_data(self.os_dict)

        # generate sub organizations
        self.subs_o1_dict = \
            generate_organizations_for_parent(
                ['sub1', 'sub2', 'sub3_del', 'sub4_del', 'sub5_del'], 'o1')

        self.subs_o2_dict = \
            generate_organizations_for_parent(
                ['sub1', 'sub2', 'sub3', 'sub4_del', 'sub5_del'], 'o2')

        self.subs_o3_dict = \
            generate_organizations_for_parent(
                ['sub1', 'sub2', 'sub3_del'], 'o3')

        # generate sub organizations dictionary
        self.subs_dict = {
            **self.subs_o1_dict,
            **self.subs_o2_dict,
            **self.subs_o3_dict,
        }

        # update organizations list with sub_organizations in database
        self.orgs.update(
            self.create_orgs_from_data(self.subs_dict, self.orgs))

    def generate_test_locations(self):
        """
        Generates location data in test database for testing purposes.
        """
        def generate_locations_for_organization(
                location_names, organization_name):
            item_dict = {}
            for name in location_names:
                item_dict['{}_{}'.format(name, organization_name)] = {
                    'name': name,
                    'organization': organization_name
                }
            return item_dict

        self.ls_o1_dict = \
            generate_locations_for_organization(
                ['l1', 'l2', 'l3', 'l4', 'l5'], 'o1')

        self.ls_sub1_o1_dict = \
            generate_locations_for_organization(
                ['l1', 'l2', 'l3', 'l4'], 'sub1_o1')

        self.ls_o2_dict = \
            generate_locations_for_organization(['l1', 'l2', 'l3', 'l4'], 'o2')

        self.ls_sub1_o2_dict = \
            generate_locations_for_organization(['l1', 'l2'], 'sub1_o2')

        # generate locations of org_3
        self.ls_o3_dict = \
            generate_locations_for_organization(['l1', 'l2'], 'o3')

        # generate locations dictionary
        self.ls_dict = {
            **self.ls_o1_dict,
            **self.ls_sub1_o1_dict,
            **self.ls_o2_dict,
            **self.ls_sub1_o2_dict,
            **self.ls_o3_dict,
        }

        # generate locations in database
        self.locations = self.create_locations_from_data(
            self.ls_dict, self.orgs)

    def generate_test_floors(self):
        """
        Generates floor data in test database for testing purposes.
        """
        def generate_floors_for_location(floor_names, location_name):
            item_dict = {}
            for name in floor_names:
                number = int(''.join([n for n in name if n.isdigit()]))
                item_dict['{}_{}'.format(name, location_name)] = {
                    'number': number,
                    'location': location_name
                }
            return item_dict

        self.fs_l1_o1_dict = \
            generate_floors_for_location(
                ['f0', 'f1', 'f2', 'f3_del', 'f4_del'],
                'l1_o1')

        self.fs_l1_sub1_o1_dict = \
            generate_floors_for_location(
                ['f0', 'f1', 'f2', 'f3', 'f4'],
                'l1_sub1_o1')

        self.fs_l1_o2_dict = \
            generate_floors_for_location(
                ['f0', 'f1', 'f2'],
                'l1_o2')

        self.fs_l1_sub1_o2_dict = \
            generate_floors_for_location(
                ['f0', 'f1', 'f2'],
                'l1_sub1_o2')

        self.fs_dict = {
            **self.fs_l1_o1_dict,
            **self.fs_l1_sub1_o1_dict,
            **self.fs_l1_o2_dict,
            **self.fs_l1_sub1_o2_dict,
        }

        self.floors = self.create_floors_from_data(
            self.fs_dict, self.locations)

    def generate_test_blocks(self):
        """
        Generates blocks data in test database for testing purposes.
        """
        def generate_blocks_for_floor(block_names, floor_name, data):
            item_dict = {}
            for name in block_names:
                item_dict['{}_{}'.format(name, floor_name)] = {
                    'name': name,
                    'floor': floor_name,
                    **data,
                }
            return item_dict

        block_data = {
            'pixels_to_m_x': 40,
            'pixels_to_m_y': 40,
            'floor_map': self.get_test_floor_map_image(),
        }
        self.bs_f0_l1_o1_dict = \
            generate_blocks_for_floor(
                ['b1', 'b2', 'b3_del', 'b4_del', 'b5_del', 'b6_del'],
                'f0_l1_o1',
                block_data)

        self.bs_f1_l1_o1_dict = \
            generate_blocks_for_floor(
                ['b1', 'b2'],
                'f1_l1_o1',
                block_data)

        self.bs_f0_l1_sub1_o1_dict = \
            generate_blocks_for_floor(
                ['b1', 'b2', 'b3_del', 'b4_del', 'b5_del'],
                'f0_l1_sub1_o1',
                block_data)

        self.bs_f0_l1_o2_dict = \
            generate_blocks_for_floor(
                ['b1', 'b2_del', 'b3_del'],
                'f0_l1_o2',
                block_data)

        self.bs_f0_l1_sub1_o2_dict = \
            generate_blocks_for_floor(
                ['b1', 'b2_del', 'b3_del'],
                'f0_l1_sub1_o2',
                block_data)

        self.bs_dict = {
            **self.bs_f0_l1_o1_dict,
            **self.bs_f1_l1_o1_dict,
            **self.bs_f0_l1_sub1_o1_dict,
            **self.bs_f0_l1_o2_dict,
            **self.bs_f0_l1_sub1_o2_dict
        }

        # generate blocks in database
        self.blocks = self.create_blocks_from_data(self.bs_dict, self.floors)

    def generate_random_mac_addr(self):
        """
        Generates a random mac address for testing purposes.
        """
        return "02:00:00:%02x:%02x:%02x" % (random.randint(0, 255),
                                            random.randint(0, 255),
                                            random.randint(0, 255))

    def generate_test_frames(self):
        """
        Generates frames data in test database for testing purposes.
        """
        def generate_frames_for_block(frame_names, block_name, data):
            item_dict = {}
            for name in frame_names:
                item_dict['{}_{}'.format(name, block_name)] = {
                    'name': name,
                    'block': block_name,
                    **data,
                }
            return item_dict

        frame_data = {
            'pixel_pose_x': 200,
            'pixel_pose_y': 100,
            'pixel_pose_theta': 90,
        }
        self.mfs_b1_f0_l1_o1_dict = \
            generate_frames_for_block(
                ['mf0', 'mf1', 'mf2_del', 'mf3_del', 'mf4_del', 'mf5_del'],
                'b1_f0_l1_o1',
                frame_data)
        self.mfs_b1_f0_l1_o2_dict = \
            generate_frames_for_block(
                ['mf0', 'mf1', 'mf2_del', 'mf3_del'],
                'b1_f0_l1_o2',
                frame_data)
        self.mfs_b1_f0_l1_sub1_o1_dict = \
            generate_frames_for_block(
                ['mf0', 'mf1', 'mf2_del', 'mf3_del', 'mf4_del', 'mf5_del'],
                'b1_f0_l1_sub1_o1',
                frame_data)
        self.mfs_b1_f0_l1_sub1_o2_dict = \
            generate_frames_for_block(
                ['mf0', 'mf1', 'mf2_del', 'mf3_del'],
                'b1_f0_l1_sub1_o2',
                frame_data)

        self.mfs_dict = {
            **self.mfs_b1_f0_l1_o1_dict,
            **self.mfs_b1_f0_l1_o2_dict,
            **self.mfs_b1_f0_l1_sub1_o1_dict,
            **self.mfs_b1_f0_l1_sub1_o2_dict,
        }

        # generate blocks in database
        self.frames = self.create_frames_from_data(self.mfs_dict, self.blocks)

    def generate_test_deepstream_servers(self):
        """
        Generates deepstream servers data in test database for testing
        purposes.
        """
        def generate_servers_for_block(names, organization_name, data):
            item_dict = {}
            for name in names:
                item_dict['{}_{}'.format(name, organization_name)] = {
                    'organization': organization_name,
                    'mac_addr': self.generate_random_mac_addr(),
                    **data,
                }
            return item_dict

        server_data = {
            'ip_addr': 'rtsp://192.168.1.1',
            'connected_at': timezone.now(),
            'last_echo_at': timezone.now()
        }
        self.ds_o1_dict =\
            generate_servers_for_block(
                ['ds0', 'ds1', 'ds2_del', 'ds3_del', 'ds4_del', 'ds5_del'],
                'o1',
                server_data)
        self.ds_o2_dict =\
            generate_servers_for_block(
                ['ds0', 'ds1', 'ds2_del', 'ds3_del', 'ds4_del', 'ds5_del'],
                'o2',
                server_data)
        self.ds_sub1_o1_dict =\
            generate_servers_for_block(
                ['ds0', 'ds1', 'ds2_del', 'ds3_del', 'ds4_del', 'ds5_del'],
                'sub1_o1',
                server_data)
        self.ds_sub1_o2_dict =\
            generate_servers_for_block(
                ['ds0', 'ds1', 'ds2_del', 'ds3_del'],
                'sub1_o2',
                server_data)

        self.ds_dict = {
            **self.ds_o1_dict,
            **self.ds_o2_dict,
            **self.ds_sub1_o1_dict,
            **self.ds_sub1_o2_dict,
        }

        # generate blocks in database
        self.deepstream_servers = \
            self.create_servers_from_data(self.ds_dict, self.orgs)

    def generate_test_cameras(self):
        """
        Generates cameras data in test database for testing
        purposes.
        """
        def generate_cameras_for_block(names, block_name, data):
            item_dict = {}
            for name in names:
                item_dict['{}_{}'.format(name, block_name)] = {
                    'block': block_name,
                    **data,
                }
            return item_dict

        camera_data = {
            'ip_addr': 'rtsp://192.168.1.1',
            'coords': [0, 0],
            'point_coords_in_frame': [0, 1, 2, 3, 4, 5, 6, 7],
            'point_coords_in_image': [0, 1, 2, 3, 4, 5, 6, 7],
        }

        self.cs_b1_f0_l1_o1_dict =\
            generate_cameras_for_block(
                ['c0', 'c1', 'c2_del', 'c3_del', 'c4_del', 'c5_del'],
                'b1_f0_l1_o1',
                camera_data)
        self.cs_b1_f0_l1_o2_dict =\
            generate_cameras_for_block(
                ['c0', 'c1', 'c2_del', 'c3_del', 'c4_del', 'c5_del'],
                'b1_f0_l1_o2',
                camera_data)
        self.cs_b1_f0_l1_sub1_o1_dict =\
            generate_cameras_for_block(
                ['c0', 'c1', 'c2_del', 'c3_del', 'c4_del', 'c5_del'],
                'b1_f0_l1_sub1_o1',
                camera_data)
        self.cs_b1_f0_l1_sub1_o2_dict =\
            generate_cameras_for_block(
                ['c0', 'c1', 'c2_del', 'c3_del'],
                'b1_f0_l1_sub1_o2',
                camera_data)

        self.cs_dict = {
            **self.cs_b1_f0_l1_o1_dict,
            **self.cs_b1_f0_l1_o2_dict,
            **self.cs_b1_f0_l1_sub1_o1_dict,
            **self.cs_b1_f0_l1_sub1_o2_dict,
        }

        # generate blocks in database
        self.cameras = \
            self.create_cameras_from_data(self.cs_dict, self.blocks)

    def setUp(self):
        """
        Sets up the test database with example values for different models
        """
        # set media root to temp file
        django_settings.MEDIA_ROOT = tempfile.mkdtemp()

        # generate test groups
        groups_list = [
            group_enum for group_enum in UserGroups]
        groups_list.append('OTHER_GROUP')
        self.groups = self.create_groups(groups_list)

        # generate test organizations
        self.generate_test_organizations()

        # generate test locations
        self.generate_test_locations()

        # generate test floors
        self.generate_test_floors()

        # generate test blocks
        self.generate_test_blocks()

        # generate measurement frames in database
        self.generate_test_frames()

        # generate deepstream servers data in database
        self.generate_test_deepstream_servers()

        # generate test cameras data in database
        self.generate_test_cameras()

        # make a list of users with respective properties
        self.users_dict = {
            'staff_user': 'staff',
            'org_1_admin_user': {
                'group': UserGroups.ORGANIZATION_ADMIN_GROUP,
                'organization': 'o1',
            },
            'org_2_admin_user': {
                'group': UserGroups.ORGANIZATION_ADMIN_GROUP,
                'organization': 'o2',
            },
            'org_3_admin_user': {
                'group': UserGroups.ORGANIZATION_ADMIN_GROUP,
                'organization': 'o3',
            },
            'org_4_admin_user': {
                'group': UserGroups.ORGANIZATION_ADMIN_GROUP,
                'organization': 'o4_del',
            },
            'sub_org_11_admin_user': {
                'group': UserGroups.ORGANIZATION_ADMIN_GROUP,
                'organization': 'sub1_o1',
            },
            'sub_org_12_admin_user': {
                'group': UserGroups.ORGANIZATION_ADMIN_GROUP,
                'organization': 'sub1_o2',
            },
            'sub_org_21_admin_user': {
                'group': UserGroups.ORGANIZATION_ADMIN_GROUP,
                'organization': 'sub2_o1',
            },
            'sub_org_22_admin_user': {
                'group': UserGroups.ORGANIZATION_ADMIN_GROUP,
                'organization': 'sub2_o2',
            },
            'sub_org_13_admin_user': {
                'group': UserGroups.ORGANIZATION_ADMIN_GROUP,
                'organization': 'sub1_o3',
            },
            'sub_org_23_admin_user': {
                'group': UserGroups.ORGANIZATION_ADMIN_GROUP,
                'organization': 'sub2_o3',
            },
            'employee_user': {
                'group': UserGroups.EMPLOYEE_GROUP,
                'organization': 'sub1_o1',
                'authorized_locations': [
                    'l1_sub1_o1',
                    'l2_sub1_o1'
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
                    url = reverse(path_name, kwargs=request['args'])
                else:
                    url = reverse(path_name)

                query_params = None
                if 'query_params' in request:
                    query_params = urlencode(request['query_params'])
                    url = '{}?{}'.format(url, query_params)

                data = None
                data_format = 'json'
                if 'data' in request:
                    data = request['data']

                if 'data_format' in request:
                    data_format = request['data_format']

                response_check = None
                if 'response_check' in request:
                    response_check = request['response_check']

                self.call_api(
                    url,
                    data,
                    self.tokens[request['user']],
                    request['status'],
                    config['type'],
                    data_format=data_format,
                    response_check=response_check)

    def call_api(
            self,
            url,
            data,
            token,
            status_code,
            api_type,
            data_format='json',
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
                format=data_format,
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
