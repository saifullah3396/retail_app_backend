import copy
from django.urls import include, path, reverse
from rest_framework.authtoken.models import Token
from rest_framework import status
from common.tests import TestsBase


class AccountRegistrationTests(TestsBase):
    urlpatterns = [
        path('accounts/', include('rest_auth.urls')),
        path('accounts/', include('allauth.urls')),
        path('accounts/registration/', include('rest_auth.registration.urls')),
    ]

    register_url = 'http://127.0.0.1/accounts/registration/'

    data = {
        "username": "test_user",
        "password1": "abcd1234@",
        "password2": "abcd1234@",
        "email": "test_user@test.com"
    }

    def post(self, data, token, status_code, debug=True):
        super().post(self.register_url, data, token, status_code, debug)

    def test_user_not_authorized(self):
        """
        Ensure requesting a registration from other_user is not possible
        """
        self.post(
            "{}", self.tokens['other_user'], status.HTTP_403_FORBIDDEN)

    def test_no_group(self):
        """
        Ensure requesting a registration without a group is not possible
        """
        self.post(
            self.data, self.tokens['staff_user'], status.HTTP_400_BAD_REQUEST)

    def test_unknown_group(self):
        """
        Ensure requesting an unknown registration group does not work
        """
        data = copy.deepcopy(self.data)
        data['groups'] = ['any_org']
        self.post(
            data, self.tokens['staff_user'], status.HTTP_400_BAD_REQUEST)

    def test_unavailable_group(self):
        """
        Ensure requesting an unavailable registration group does not work
        """
        data = copy.deepcopy(self.data)
        data['groups'] = ['other_group']
        self.post(
            data, self.tokens['staff_user'], status.HTTP_400_BAD_REQUEST)

    def test_org_admin_no_org(self):
        """
        Ensure registration of an organization admin with no organization
        provided does not work
        """
        data = copy.deepcopy(self.data)
        data['groups'] = ['organization_admin']
        self.post(
            data, self.tokens['staff_user'], status.HTTP_400_BAD_REQUEST)

    def test_org_admin_invalid_org(self):
        """
        Ensure registration of an organization admin with invalid organization
        name does not work
        """
        data = copy.deepcopy(self.data)
        data['groups'] = ['organization_admin']
        data['organization'] = 'any_org'
        self.post(
            data, self.tokens['staff_user'], status.HTTP_400_BAD_REQUEST)

    def test_org_admin_no_locations(self):
        """
        Ensure registration of organization admin with no locations does not
        work
        """
        data = copy.deepcopy(self.data)
        data['groups'] = ['organization_admin']
        data['organization'] = 'org_1'
        self.post(
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
        self.post(
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
        self.post(
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
        self.post(
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
        self.post(
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
        self.post(
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
        self.post(
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
        self.post(
            data, self.tokens['employee_user'], status.HTTP_403_FORBIDDEN)

    def test_sub_org_admin_no_sub_organization(self):
        """
        Ensure registration of sub_organization admin without sub_organization
        is not possible
        """
        data = copy.deepcopy(self.data)
        data['groups'] = ['sub_organization_admin']
        self.post(
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
        self.post(
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
        self.post(
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
        self.post(
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
        self.post(
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
        self.post(
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
        self.post(
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
        self.post(
            data, self.tokens['sub_org_11_admin_user'], status.HTTP_201_CREATED)

    def test_sub_org_admin_different_sub_org_admin(self):
        """
        Ensure registration of sub_organization admin by another
        sub_organization admin from different sub_organization does not work
        """
        data = copy.deepcopy(self.data)
        data['groups'] = ['sub_organization_admin']
        data['organization'] = 'org_1'
        data['sub_organization'] = 'sub_1_org_1'
        data['locations'] = ['location_1_sub_org_1']
        self.post(
            data, self.tokens['sub_org_12_admin_user'], status.HTTP_403_FORBIDDEN)

    def test_sub_org_admin_employee(self):
        """
        Ensure registration of sub_organization admin by an employee does
        not work
        """
        data = copy.deepcopy(self.data)
        data['groups'] = ['sub_organization_admin']
        data['organization'] = 'org_1'
        data['sub_organization'] = 'sub_1_org_1'
        data['locations'] = ['location_1_sub_org_1']
        self.post(
            data, self.tokens['employee_user'], status.HTTP_403_FORBIDDEN)

    def test_employee_sub_org_admin(self):
        """
        Ensure registration of employee by sub_organization admin works
        """
        data = copy.deepcopy(self.data)
        data['groups'] = ['employee']
        data['organization'] = 'org_1'
        data['sub_organization'] = 'sub_1_org_1'
        data['locations'] = ['location_1_sub_org_1']
        self.post(
            data, self.tokens['sub_org_11_admin_user'], status.HTTP_201_CREATED)

    def test_employee_employee(self):
        """
        Ensure registration of employee by another employee does not work
        """
        data = copy.deepcopy(self.data)
        data['groups'] = ['employee']
        data['organization'] = 'org_1'
        data['sub_organization'] = 'sub_1_org_1'
        data['locations'] = ['location_1_sub_org_1']
        self.post(
            data, self.tokens['employee_user'], status.HTTP_403_FORBIDDEN)
