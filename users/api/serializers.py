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


class AppUserSerializerAdminAccess(serializers.ModelSerializer):
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
