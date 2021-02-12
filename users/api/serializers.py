from backend import settings
from core.permissions import UserGroups
from core.utils import *
from django.contrib.auth.models import AbstractUser, Group
from locations.api.serializers import (LocationDetailSerializer,
                                       LocationListSerializer)
from locations.models import Location
from locations.utils import *
from organizations.api.serializers import OrganizationSerializer
from organizations.models import Organization
from rest_framework import exceptions, serializers
from user_auth.serializers import RegistrationSerializer

from ..models import AppUser


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['name']


class AppUserListOrganizationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Organization
        fields = ['id', 'name']


class AppUserListSerializer(serializers.ModelSerializer):
    group = serializers.SerializerMethodField()

    def get_group(self, instance):
        if instance.is_staff:
            return "SUPER_USER_GROUP"

        for group in UserGroups:
            group = instance.groups.filter(name=group.name)
            if group.exists():
                return group.first().name

    class Meta:
        model = AppUser
        fields = [
            'id',
            'username',
            'email',
            'is_staff',
            'group',
            'organization']


class AppUserDetailOrganizationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Organization
        fields = ['id', 'name', 'parent']


class AppUserDetailLocationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Location
        fields = ['id', 'organization']


class AppUserDetailRetrieveSerializer(serializers.ModelSerializer):
    group = serializers.SerializerMethodField()
    authorized_locations = serializers.SerializerMethodField()
    organization = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(serializers.ModelSerializer, self).__init__(*args, **kwargs)
        self.group_to_locations_fn = {
            UserGroups.ORGANIZATION_ADMIN_GROUP:
                self._get_organization_admin_locations,
            UserGroups.EMPLOYEE_GROUP:
                self._get_employee_locations
        }

        self.group_to_organizations_fn = {
            UserGroups.ORGANIZATION_ADMIN_GROUP:
                self._get_organization_admin_organizations,
            UserGroups.EMPLOYEE_GROUP:
                self._get_employee_organizations
        }

    def get_group(self, instance):
        if instance.is_staff:
            return "SUPER_USER_GROUP"

        for group in UserGroups:
            group = instance.groups.filter(name=group.name)
            if group.exists():
                return group.first().name

    def get_authorized_locations(self, instance):
        locations = Location.objects.none()
        if instance.is_staff:
            locations = get_locations_for_staff()
        else:
            locations = \
                get_fn_by_group(instance, self.group_to_locations_fn)(instance)
        return AppUserDetailLocationSerializer(locations, many=True).data

    def _get_organization_admin_locations(self, instance):
        return get_locations_for_organization_admin(
            instance, include_self=True)

    def _get_employee_locations(self, instance):
        return get_locations_for_employee(instance)

    def get_organization(self, instance):
        organizations = Organization.objects.none()
        if not instance.is_staff:
            organizations = \
                get_fn_by_group(
                    instance, self.group_to_organizations_fn)(instance)
        return AppUserDetailOrganizationSerializer(
            organizations, many=True).data

    def _get_organization_admin_organizations(self, instance):
        return instance.organization.get_descendants(include_self=True)

    def _get_employee_organizations(self, instance):
        return [instance.organization]

    class Meta:
        model = AppUser
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_staff',
            'group',
            'authorized_locations',
            'organization']




class AppUserSerializerAppUserAccess(serializers.ModelSerializer):
    organization = OrganizationSerializer()
    authorized_locations = LocationDetailSerializer(
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
