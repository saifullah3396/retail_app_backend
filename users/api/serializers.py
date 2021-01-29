from rest_framework import serializers
from ..models import AppUser
from django.contrib.auth.models import AbstractUser
from organizations.api.serializers import \
    OrganizationSerializer, SubOrganizationSerializer
from locations.models import Location
from organizations.models import Organization, SubOrganization
from organizations.api.serializers import \
    OrganizationSerializer, SubOrganizationSerializer
from locations.api.serializers import \
    LocationSerializerAppUserAccess, LocationSerializerAdminAccess
from backend import settings


class AdminUserSerializerAdminAccess(serializers.ModelSerializer):
    organizations = serializers.SerializerMethodField()
    sub_organizations = serializers.SerializerMethodField()
    authorized_locations = serializers.SerializerMethodField()
    group = serializers.SerializerMethodField()

    def get_organizations(self, app_user):
        # return all locations as authorized in super user
        organizations = Organization.objects.all()
        return \
            OrganizationSerializer(organizations, many=True).data

    def get_sub_organizations(self, app_user):
        # return all locations as authorized in super user
        sub_organizations = SubOrganization.objects.all()
        return \
            SubOrganizationSerializer(
                sub_organizations, many=True).data

    def get_authorized_locations(self, app_user):
        # return all locations as authorized in super user
        authorized_locations = Location.objects.all()
        return \
            LocationSerializerAdminAccess(authorized_locations, many=True).data

    def get_group(self, app_user):
        return "Super Admin"

    class Meta:
        model = AppUser
        fields = [
            'uuid',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_staff',
            'group',
            'organizations',
            'sub_organizations',
            'authorized_locations',
            'avatar']


class AppUserSerializerAdminAccess(serializers.ModelSerializer):
    organization = OrganizationSerializer()
    sub_organization = SubOrganizationSerializer()
    authorized_locations = LocationSerializerAppUserAccess(
        many=True, read_only=True)
    group = serializers.SerializerMethodField()

    # get group
    def get_group(self, user):
        for key, value in settings.REGISTRATION_GROUPS_WITH_AUTHORITY.items():
            if user.authority == value:
                return key

    class Meta:
        model = AppUser
        fields = [
            'uuid',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_staff',
            'group',
            'organization',
            'sub_organization',
            'authorized_locations']


class AppUserSerializerAppUserAccess(serializers.ModelSerializer):
    organization = OrganizationSerializer()
    sub_organization = SubOrganizationSerializer()
    authorized_locations = LocationSerializerAppUserAccess(
        many=True, read_only=True)
    group = serializers.SerializerMethodField()

    # get group
    def get_group(self, user):
        for key, value in settings.REGISTRATION_GROUPS_WITH_AUTHORITY.items():
            if user.authority == value:
                return key

    class Meta:
        model = AppUser
        fields = [
            'uuid',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_staff',
            'group',
            'organization',
            'sub_organization',
            'authorized_locations']
