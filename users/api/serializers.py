"""
Defines the serializers used in user REST api views.
"""

from django.contrib.auth.models import Group
from rest_framework import serializers

from core.permissions import UserGroups
from core.utils import WritableSerializerMethodField, get_fn_by_group
from locations.models import Location
from locations.utils import (get_locations_for_employee,
                             get_locations_for_organization_admin,
                             get_locations_for_staff)
from organizations.models import Organization
from users.models import AppUser


# pylint: disable=missing-class-docstring
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
        """
        Returns the name of the user group assigned to this user.
        """

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
        fields = ['id', 'name', 'organization']


class AppUserDetailRetrieveSerializer(serializers.ModelSerializer):
    group = serializers.SerializerMethodField()
    authorized_locations = serializers.SerializerMethodField()
    organization = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.group_to_locations_fn = {
            UserGroups.ORGANIZATION_ADMIN_GROUP:
                lambda instance: get_locations_for_organization_admin(
                    instance, include_self=True),
            UserGroups.EMPLOYEE_GROUP: get_locations_for_employee
        }

        self.group_to_organizations_fn = {
            UserGroups.ORGANIZATION_ADMIN_GROUP:
                lambda instance: instance.organization.get_descendants(
                    include_self=True),
            UserGroups.EMPLOYEE_GROUP: lambda instance: [instance.organization]
        }

    def get_group(self, instance):
        """
        Returns the name of the user group assigned to this user.
        """

        if instance.is_staff:
            return "SUPER_USER_GROUP"

        for group in UserGroups:
            group = instance.groups.filter(name=group.name)
            if group.exists():
                return group.first().name

    def get_authorized_locations(self, instance):
        """
        Returns details of all the locations authorized to this user.
        """

        locations = Location.objects.none()
        if instance.is_staff:
            locations = get_locations_for_staff()
        else:
            locations = \
                get_fn_by_group(instance, self.group_to_locations_fn)(instance)
        return AppUserDetailLocationSerializer(locations, many=True).data

    def get_organization(self, instance):
        """
        Returns details of all the organizations authorized to this user.
        """

        organizations = Organization.objects.none()
        if instance.is_staff:
            organizations = Organization.objects.all()
        else:
            organizations = \
                get_fn_by_group(
                    instance, self.group_to_organizations_fn)(instance)
        return AppUserDetailOrganizationSerializer(
            organizations, many=True).data

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


class AppUserDetailUpdateSerializer(serializers.ModelSerializer):
    group = WritableSerializerMethodField(
        deserializer_field=serializers.CharField(required=False))
    organization = WritableSerializerMethodField(
        deserializer_field=serializers.UUIDField(required=False))
    authorized_locations = WritableSerializerMethodField(
        deserializer_field=serializers.ListField(
            child=serializers.UUIDField(), required=False))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.group_to_locations_fn = {
            UserGroups.ORGANIZATION_ADMIN_GROUP:
                lambda instance: get_locations_for_organization_admin(
                    instance, include_self=True),
            UserGroups.EMPLOYEE_GROUP: get_locations_for_employee
        }

        self.group_to_organizations_fn = {
            UserGroups.ORGANIZATION_ADMIN_GROUP:
                lambda instance: instance.organization.get_descendants(
                    include_self=True),
            UserGroups.EMPLOYEE_GROUP:
                lambda instance: instance.organization
        }

    def get_group(self, instance):
        """
        Returns the name of the user group assigned to this user.
        """

        if instance.is_staff:
            return "SUPER_USER_GROUP"

        for group in UserGroups:
            group = instance.groups.filter(name=group.name)
            if group.exists():
                return group.first().name

    def set_group(self, group_name):
        """
        Sets the user group based on the input group_name received.
        """

        try:
            group = Group.objects.get(name=group_name)
            user_groups = [g.name for g in UserGroups]
            if group.name not in user_groups:
                raise serializers.ValidationError(
                    {
                        "group": "Can only be assigned one of the following "
                        "{}".format(user_groups)
                    }
                )
            return {
                'group': group
            }
        except Group.DoesNotExist as exc:
            raise serializers.ValidationError(
                'Group of id={} does not exist. Available groups: {}'.format(
                    group_name, [group.name for group in UserGroups])) from exc

    def get_authorized_locations(self, instance):
        """
        Returns details of all the locations authorized to this user.
        """
        locations = Location.objects.none()
        if instance.is_staff:
            locations = get_locations_for_staff()
        else:
            locations = \
                get_fn_by_group(instance, self.group_to_locations_fn)(instance)
        return AppUserDetailLocationSerializer(locations, many=True).data

    def set_authorized_locations(self, location_ids):
        """
        Adds the received locations to authorized list of user.
        """

        locations = []
        for location_name in location_ids:
            try:
                location = Location.objects.get(id=location_name)
                locations.append(location)
            except Location.DoesNotExist as exc:
                raise serializers.ValidationError(
                    'Location {} does not exist.'.format
                    (location_name)) from exc
        return {
            'authorized_locations': locations
        }

    def get_organization(self, instance):
        """
        Returns details of all the organizations authorized to this user.
        """
        organizations = Organization.objects.none()
        if not instance.is_staff:
            organizations = \
                get_fn_by_group(
                    instance, self.group_to_organizations_fn)(instance)
        return AppUserDetailOrganizationSerializer(
            organizations, many=True).data

    def set_organization(self, organization_id):
        """
        Sets the user organization based on given organization id.
        """
        try:
            return {
                'organization': Organization.objects.get(id=organization_id)
            }
        except Organization.DoesNotExist as exc:
            raise serializers.ValidationError(
                'Organization of id={} does not exist.'.format(
                    organization_id)) from exc

    def update(self, instance, validated_data):
        """
        Validates the incoming data for user registration.
        """

        # # set user permission groups
        group = validated_data.pop('group')
        if group is not None:
            instance.groups.clear()
            instance.groups.add(group)

        # add organization to user
        organization = validated_data.pop('organization')
        if organization is not None:
            instance.organization = organization

        # add all authorized locations to user if its an employee
        if instance.groups.filter(name=UserGroups.EMPLOYEE_GROUP.name).exists():
            locations = validated_data.pop('authorized_locations')
            if locations is not None:
                for location in locations:
                    instance.authorized_locations.add(location)
        return super().update(instance, validated_data)

    class Meta:
        model = AppUser
        fields = [
            'first_name',
            'last_name',
            'avatar',
            'group',
            'authorized_locations',
            'organization']
