from django.urls import include, path, reverse
from rest_framework.test import APITestCase, URLPatternsTestCase
from rest_framework.authtoken.models import Token
from rest_framework import status
from .models import AppUser
from django.contrib.auth.models import Group
from backend import settings
from organizations.models import Organization, SubOrganization
from locations.models import Location
import copy


class AccountRegistrationTests(APITestCase, URLPatternsTestCase):
    urlpatterns = [
        path('accounts/', include('rest_auth.urls')),
        path('accounts/', include('allauth.urls')),
        path('accounts/registration/', include('rest_auth.registration.urls')),
    ]
    url = 'http://127.0.0.1/accounts/registration/'
    data = {
        "username": "test_user",
        "password1": "abcd1234@",
        "password2": "abcd1234@",
        "email": "test_user@test.com"
    }

    def createGroups(self, groupNames):
        groups = {}
        for groupName in groupNames:
            groups[groupName] = Group(name=groupName)
            groups[groupName].save()
        return groups

    def createOrgs(self, orgNames):
        orgs = {}
        for orgName in orgNames:
            orgs[orgName] = Organization(name=orgName)
            orgs[orgName].save()
        return orgs

    def createSubOrgs(self, subOrgDict, orgs):
        subOrgs = {}
        for (subOrgName, orgName) in subOrgDict.items():
            subOrgs[subOrgName] = SubOrganization(
                name=subOrgName, organization=orgs.get(orgName))
            subOrgs[subOrgName].save()
        return subOrgs

    def createLocations(self, subOrgDict, orgs, subOrgs):
        locations = {}
        for (locationName, orgNames) in subOrgDict.items():
            locations[locationName] = Location(
                name=locationName,
                organization=orgs.get(orgNames['organization']),
                sub_organization=subOrgs.get(orgNames.get('sub_organization')))
            locations[locationName].save()
        return locations

    def createUsers(self, usersDict, groups, orgs, subOrgs):
        users = {}
        tokens = {}
        for (userName, userData) in usersDict.items():
            if userData == "staff":
                users[userName] = AppUser.objects.create_user(
                    username=userName,
                    email='{}@test.com'.format(userName),
                    password='abcd1234@',
                    is_staff=True)
            else:
                users[userName] = AppUser.objects.create_user(
                    username=userName,
                    email='{}@test.com'.format(userName),
                    password='abcd1234@',
                    organization=orgs.get(userData['organization']),
                    sub_organization=subOrgs.get(userData['sub_organization']))
                groups[userData['group']].user_set.add(
                    users[userName])
                groups[userData['group']].save()

            users[userName].save()
            tokens[userName] = Token.objects.create(user=users[userName])
            tokens[userName].save()
        return users, tokens

    def setUp(self):
        # generate test groups
        groups_list = copy.deepcopy(settings.REGISTER_AVAILABLE_GROUPS)
        groups_list.append('other_group')
        self.groups = self.createGroups(groups_list)

        # generate test organizations
        orgs_list = ['org_1', 'org_2']
        self.orgs = self.createOrgs(orgs_list)

        # generate test sub organizations
        sub_orgs_list = {
            'sub_1_org_1': 'org_1',
            'sub_2_org_1': 'org_1',
            'sub_1_org_2': 'org_2',
            'sub_2_org_2': 'org_2',
        }
        self.subOrgs = self.createSubOrgs(sub_orgs_list, self.orgs)

        # generate test locations
        locations_list = {
            'location_1_org_1': {'organization': 'org_1'},
            'location_1_sub_org_1': {
                'organization': 'org_1', 'sub_organization': 'sub_1_org_1'},
            'location_2_org_1': {'organization': 'org_1'},
            'location_1_org_2': {'organization': 'org_2'},
            'location_2_org_2': {'organization': 'org_2'}
        }
        self.locations = self.createLocations(
            locations_list, self.orgs, self.subOrgs)

        user_names_list = {
            'staff_user': 'staff',
            'org_1_admin_user': {
                'group': 'organization_admin',
                'organization': 'org_1',
                'sub_organization': None
            },
            'org_2_admin_user': {
                'group': 'organization_admin',
                'organization': 'org_2',
                'sub_organization': None
            },
            'sub_org_11_admin_user': {
                'group': 'sub_organization_admin',
                'organization': 'org_1',
                'sub_organization': 'sub_1_org_1'
            },
            'sub_org_12_admin_user': {
                'group': 'sub_organization_admin',
                'organization': 'org_1',
                'sub_organization': 'sub_2_org_1'
            },
            'employee_user': {
                'group': 'employee',
                'organization': 'org_1',
                'sub_organization': 'sub_1_org_1'
            },
            'other_user': {
                'group': 'other_group',
                'organization': None,
                'sub_organization': None
            },
        }
        self.users, self.tokens = self.createUsers(
            user_names_list, self.groups, self.orgs, self.subOrgs)

    def send_register_post(self, data, token, status_code, debug=False):
        """
        Sends a post request to url
        """
        response = self.client.post(
            self.url,
            data=data,
            format='json',
            HTTP_AUTHORIZATION='Token {}'.format(token))
        if debug:
            print(response.status_code == status_code, response.data)
        self.assertEqual(response.status_code, status_code)

    def test_user_not_authorized(self):
        """
        Ensure requesting a registration from other_user is not possible
        """
        self.send_register_post(
            "{}", self.tokens['other_user'], status.HTTP_403_FORBIDDEN)

    def test_no_group(self):
        """
        Ensure requesting a registration without a group is not possible
        """
        self.send_register_post(
            self.data, self.tokens['staff_user'], status.HTTP_400_BAD_REQUEST)

    def test_unknown_group(self):
        """
        Ensure requesting an unknown registration group does not work
        """
        data = copy.deepcopy(self.data)
        data['groups'] = ['any_org']
        self.send_register_post(
            data, self.tokens['staff_user'], status.HTTP_400_BAD_REQUEST)

    def test_unavailable_group(self):
        """
        Ensure requesting an unavailable registration group does not work
        """
        data = copy.deepcopy(self.data)
        data['groups'] = ['other_group']
        self.send_register_post(
            data, self.tokens['staff_user'], status.HTTP_400_BAD_REQUEST)

    def test_org_admin_no_org(self):
        """
        Ensure registration of an organization admin with no organization
        provided does not work
        """
        data = copy.deepcopy(self.data)
        data['groups'] = ['organization_admin']
        self.send_register_post(
            data, self.tokens['staff_user'], status.HTTP_400_BAD_REQUEST)

    def test_org_admin_invalid_org(self):
        """
        Ensure registration of an organization admin with invalid organization
        name does not work
        """
        data = copy.deepcopy(self.data)
        data['groups'] = ['organization_admin']
        data['organization'] = 'any_org'
        self.send_register_post(
            data, self.tokens['staff_user'], status.HTTP_400_BAD_REQUEST)

    def test_org_admin_no_locations(self):
        """
        Ensure registration of organization admin with no locations does not
        work
        """
        data = copy.deepcopy(self.data)
        data['groups'] = ['organization_admin']
        data['organization'] = 'org_1'
        self.send_register_post(
            data, self.tokens['staff_user'], status.HTTP_400_BAD_REQUEST)

    def test_org_admin_invalid_locations(self):
        """
        Ensure registration of organization admin with invalid locations does
        not work
        """
        data = copy.deepcopy(self.data)
        data['groups'] = ['organization_admin']
        data['organization'] = 'org_1'
        data['locations'] = ['any_location']
        self.send_register_post(
            data, self.tokens['staff_user'], status.HTTP_400_BAD_REQUEST)

    def test_org_admin_unassociated_locations(self):
        """
        Ensure registration of organization admin with unassociated locations
        does not work
        """
        data = copy.deepcopy(self.data)
        data['groups'] = ['organization_admin']
        data['organization'] = 'org_1'
        data['locations'] = ['location_1_org_2']
        self.send_register_post(
            data, self.tokens['staff_user'], status.HTTP_400_BAD_REQUEST)

    def test_org_admin_by_staff(self):
        """
        Ensure registration of organization admin from staff with valid
        organization name and locations works
        """
        data = copy.deepcopy(self.data)
        data['username'] = 'org_admin_by_staff'
        data['email'] = 'org_admin_by_staff@test.com'
        data['groups'] = ['organization_admin']
        data['organization'] = 'org_1'
        data['locations'] = ['location_1_org_1']
        self.send_register_post(
            data, self.tokens['staff_user'], status.HTTP_201_CREATED)

    def test_org_admin_by_org_admin(self):
        """
        Ensure registration of organization admin from another organization
        with valid data works
        """
        data = copy.deepcopy(self.data)
        data['username'] = 'org_admin_by_org_admin'
        data['email'] = 'org_admin_by_org_admin@test.com'
        data['groups'] = ['organization_admin']
        data['organization'] = 'org_1'
        data['locations'] = ['location_1_org_1']
        self.send_register_post(
            data, self.tokens['org_1_admin_user'], status.HTTP_201_CREATED)

    def test_org_admin_by_org_admin_different_org(self):
        """
        Ensure registration of organization admin from admin of another
        organization does not work
        """
        data = copy.deepcopy(self.data)
        data['groups'] = ['organization_admin']
        data['organization'] = 'org_1'
        data['locations'] = ['location_1_org_1']
        self.send_register_post(
            data, self.tokens['org_2_admin_user'], status.HTTP_403_FORBIDDEN)

    def test_org_admin_by_sub_organization_admin(self):
        """
        Ensure registration of organization admin from sub_organization_admin
        is not possible
        """
        data = copy.deepcopy(self.data)
        data['groups'] = ['organization_admin']
        data['organization'] = 'org_1'
        data['locations'] = ['location_1_org_1']
        self.send_register_post(
            data, self.tokens['sub_org_11_admin_user'],
            status.HTTP_403_FORBIDDEN)

    def test_org_admin_by_employee(self):
        """
        Ensure registration of organization admin from employee
        is not possible
        """
        data = copy.deepcopy(self.data)
        data['groups'] = ['organization_admin']
        data['organization'] = 'org_1'
        data['locations'] = ['location_1_org_1']
        self.send_register_post(
            data, self.tokens['employee_user'], status.HTTP_403_FORBIDDEN)

    def test_sub_org_admin_no_sub_organization(self):
        """
        Ensure registration of sub_organization admin without sub_organization
        is not possible
        """
        data = copy.deepcopy(self.data)
        data['groups'] = ['sub_organization_admin']
        self.send_register_post(
            data, self.tokens['staff_user'], status.HTTP_400_BAD_REQUEST)

    def test_sub_org_admin_invalid_sub_org(self):
        """
        Ensure registration of an sub_organization admin with invalid
        sub_organization name does not work
        """
        data = copy.deepcopy(self.data)
        data['groups'] = ['sub_organization_admin']
        data['organization'] = 'org_1'
        data['sub_organization'] = 'any_sub_organization'
        self.send_register_post(
            data, self.tokens['staff_user'], status.HTTP_400_BAD_REQUEST)

    def test_sub_org_admin_unassociated_sub_org(self):
        """
        Ensure registration of an sub_organization admin with unassociated
        sub_organization name does not work
        """
        data = copy.deepcopy(self.data)
        data['groups'] = ['sub_organization_admin']
        data['organization'] = 'org_1'
        data['sub_organization'] = 'sub_1_org_2'
        self.send_register_post(
            data, self.tokens['staff_user'], status.HTTP_400_BAD_REQUEST)

    def test_sub_org_admin_no_locations(self):
        """
        Ensure registration of sub_organization admin by organization admin
        with no locations does not work
        """
        data = copy.deepcopy(self.data)
        data['groups'] = ['sub_organization_admin']
        data['organization'] = 'org_1'
        data['sub_organization'] = 'sub_1_org_1'
        self.send_register_post(
            data, self.tokens['org_1_admin_user'], status.HTTP_400_BAD_REQUEST)

    def test_sub_org_admin_invalid_locations(self):
        """
        Ensure registration of sub_organization admin by organization admin
        with invalid locations does not work
        """
        data = copy.deepcopy(self.data)
        data['groups'] = ['sub_organization_admin']
        data['organization'] = 'org_1'
        data['sub_organization'] = 'sub_1_org_1'
        data['locations'] = ['any_location']
        self.send_register_post(
            data, self.tokens['org_1_admin_user'], status.HTTP_400_BAD_REQUEST)

    def test_sub_org_admin_unassociated_locations(self):
        """
        Ensure registration of sub_organization admin by organization admin
        with unassociated locations does not work
        """
        data = copy.deepcopy(self.data)
        data['groups'] = ['sub_organization_admin']
        data['organization'] = 'org_1'
        data['sub_organization'] = 'sub_1_org_1'
        # this location is under org_1 not sub_org_1
        data['locations'] = ['location_1_org_1']
        self.send_register_post(
            data, self.tokens['org_1_admin_user'], status.HTTP_400_BAD_REQUEST)

    def test_sub_org_admin_org_admin(self):
        """
        Ensure registration of sub_organization admin by organization admin
        works with valid data
        """
        data = copy.deepcopy(self.data)
        data['username'] = 'sub_org_admin_org_admin'
        data['email'] = 'sub_org_admin_org_admin@test.com'
        data['groups'] = ['sub_organization_admin']
        data['organization'] = 'org_1'
        data['sub_organization'] = 'sub_1_org_1'
        data['locations'] = ['location_1_sub_org_1']
        self.send_register_post(
            data, self.tokens['org_1_admin_user'], status.HTTP_201_CREATED)

    def test_sub_org_admin_sub_org_admin(self):
        """
        Ensure registration of sub_organization admin by another
        sub_organization admin works with valid data
        """
        data = copy.deepcopy(self.data)
        data['username'] = 'sub_org_admin_sub_org_admin'
        data['email'] = 'sub_org_admin_sub_org_admin@test.com'
        data['groups'] = ['sub_organization_admin']
        data['organization'] = 'org_1'
        data['sub_organization'] = 'sub_1_org_1'
        data['locations'] = ['location_1_sub_org_1']
        self.send_register_post(
            data, self.tokens['sub_org_11_admin_user'], status.HTTP_201_CREATED)

    def test_sub_org_admin_different_sub_org_admin(self):
        """
        Ensure registration of sub_organization admin by another
        sub_organization admin works
        """
        data = copy.deepcopy(self.data)
        data['groups'] = ['sub_organization_admin']
        data['organization'] = 'org_1'
        data['sub_organization'] = 'sub_1_org_1'
        data['locations'] = ['location_1_sub_org_1']
        self.send_register_post(
            data, self.tokens['sub_org_12_admin_user'], status.HTTP_403_FORBIDDEN)

    def test_sub_org_admin_employee(self):
        """
        Ensure registration of sub_organization admin by another
        sub_organization admin works
        """
        data = copy.deepcopy(self.data)
        data['groups'] = ['sub_organization_admin']
        data['organization'] = 'org_1'
        data['sub_organization'] = 'sub_1_org_1'
        data['locations'] = ['location_1_sub_org_1']
        self.send_register_post(
            data, self.tokens['employee_user'], status.HTTP_403_FORBIDDEN)
