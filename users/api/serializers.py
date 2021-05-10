"""
Defines the serializers used in user REST api views.
"""

from django.contrib.auth.models import Group
from rest_framework import serializers

from core.permissions import UserGroups
from core.utils import (field_invalid_error, field_not_found_error,
                        field_with_id_not_found_error,
                        get_employee_authorized_locations,
                        get_employee_authorized_organizations,
                        get_fn_by_user_group,
                        get_organization_admin_authorized_locations,
                        get_organization_admin_authorized_organizations,
                        get_staff_authorized_locations,
                        get_staff_authorized_organizations)
from locations.models import Location
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
            return 'super_user'

        for group_enum in UserGroups:
            group = instance.groups.filter(name=group_enum.value)
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


class AppUserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppUser
        fields = []


class AppUserRetrieveOrganizationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Organization
        fields = ['id', 'name', 'parent']


class AppUserRetrieveLocationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Location
        fields = ['id', 'name', 'organization']


class AppUserRetrieveSerializer(serializers.ModelSerializer):
    group = serializers.SerializerMethodField(read_only=True)
    authorized_locations = serializers.SerializerMethodField(read_only=True)
    organization = serializers.SerializerMethodField(read_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.group_to_locations_fn = {
            UserGroups.ORGANIZATION_ADMIN_GROUP:
                get_organization_admin_authorized_locations,
            UserGroups.EMPLOYEE_GROUP:
                get_employee_authorized_locations
        }

    def get_group(self, instance):
        """
        Returns the name of the user group assigned to this user.
        """

        if instance.is_staff:
            return 'super_user'

        for group_enum in UserGroups:
            group = instance.groups.filter(name=group_enum.value)
            if group.exists():
                return group.first().name

    def get_authorized_locations(self, instance):
        """
        Returns details of all the locations authorized to this user.
        """

        locations = Location.objects.none()
        if not instance.is_staff:
            locations = \
                get_fn_by_user_group(
                    instance, self.group_to_locations_fn)(instance)
        return AppUserRetrieveLocationSerializer(locations, many=True).data

    def get_organization(self, instance):
        """
        Returns the user organization
        """

        if not instance.is_staff:
            return AppUserRetrieveOrganizationSerializer(
                instance.organization).data
        else:
            return None

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
            'organization',
            'avatar']


class AppUserUpdateSerializer(serializers.ModelSerializer):
    group = serializers.CharField(required=False)
    organization = serializers.UUIDField(required=False)
    authorized_locations = serializers.ListField(
        child=serializers.UUIDField(), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def validate_group(self, group_name):
        """
        Validates the user group based on the input group_name received.
        """

        try:
            group = Group.objects.get(name=group_name)
            user_groups = [g.name for g in UserGroups]
            if group.name not in user_groups:
                raise serializers.ValidationError(
                    {
                        'group': field_invalid_error()
                    }
                )
            return {
                'group': group
            }
        except Group.DoesNotExist as exc:
            raise serializers.ValidationError({
                {
                    'group': field_not_found_error()
                }
            }) from exc

    def validate_authorized_locations(self, location_ids):
        """
        Valdiates the received locations to authorized list of user.
        """

        locations = []
        for location_id in location_ids:
            try:
                location = Location.objects.get(id=location_id)
                locations.append(location)
            except Location.DoesNotExist as exc:
                raise serializers.ValidationError({
                    'authorized_locations':
                        field_with_id_not_found_error(location_id)
                }) from exc
        return {
            'authorized_locations': locations
        }

    def validate_organization(self, organization_id):
        """
        Valdiates the user organization based on given organization id.
        """
        try:
            return {
                'organization': Organization.objects.get(id=organization_id)
            }
        except Organization.DoesNotExist as exc:
            raise serializers.ValidationError({
                'organization': field_with_id_not_found_error(organization_id)
            }) from exc

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
        if instance.groups.filter(name=UserGroups.EMPLOYEE_GROUP).exists():
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
        extra_kwargs = {
            'id': {'read_only': True},
            'username': {'read_only': True},
            'email': {'read_only': True},
            'is_staff': {'read_only': True},
        }


class AppUserOrganizationAdminUpdateSerializer(
        AppUserUpdateSerializer):
    group = serializers.CharField(required=False)
    organization = serializers.UUIDField(required=False)
    authorized_locations = serializers.ListField(
        child=serializers.UUIDField(), required=False)


class AppUserEmployeeUpdateSerializer(AppUserUpdateSerializer):
    group = serializers.CharField(required=False, read_only=True)
    organization = serializers.UUIDField(required=False, read_only=True)
    authorized_locations = serializers.ListField(
        child=serializers.UUIDField(), required=False, read_only=True)
