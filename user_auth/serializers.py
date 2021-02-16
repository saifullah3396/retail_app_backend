from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email
from core.permissions import UserGroups
from core.utils import *
from core.utils import is_in_group
from django.contrib.auth.models import Group
from locations.models import Location
from organizations.models import Organization
from rest_auth.registration.serializers import RegisterSerializer
from rest_framework import exceptions, serializers, status
from users.api.serializers import AppUserDetailRetrieveSerializer
from users.models import AppUser


class RegistrationSerializer(RegisterSerializer):
    """
    Extends the register serializer to add custom fields. This serializer takes
    permission groups as to accept one of the following fields:
        [
            'organization_admin',
            'employee'
        ]
    If the user is organization_admin, it checks whether organization info is
    provided. Finally it checks whether the locations provided as inputs are
    existing and are available to the organization.
    """

    group = serializers.CharField(required=True)
    organization = serializers.UUIDField(required=True)
    authorized_locations = serializers.ListField(
        child=serializers.UUIDField(), required=False)

    def validate_group(self, group_id):
        try:
            group = Group.objects.get(name=group_id)
            user_groups = [g.name for g in UserGroups]
            if group.name not in user_groups:
                raise serializers.ValidationError(
                    {
                        "group": "Can only be assigned one of the following "
                        "{}".format(user_groups)
                    }
                )
            return group
        except Group.DoesNotExist:
            raise serializers.ValidationError(
                'Group of id={} does not exist. Available groups: {}'.format(
                    group_id, [group.name for group in UserGroups]))

    def validate_organization(self, organization_id):

        try:
            return Organization.objects.get(id=organization_id)
        except Organization.DoesNotExist:
            raise serializers.ValidationError(
                'Organization of id={} does not exist.'.format(
                    organization_id))

    def validate_authorized_locations(self, location_ids):
        locations = []
        for location_name in location_ids:
            try:
                location = Location.objects.get(id=location_name)
                locations.append(location)
            except Location.DoesNotExist:
                raise serializers.ValidationError(
                    'Location {} does not exist.'.format(location_name))
        return locations

    def validate_organization_user(self, data, request_user):
        organization = data.get('organization')
        if not request_user.is_staff:
            # check if user is organization admin
            if is_organization_admin(request_user):
                # check if request user is in the same organization as the
                # registered user or if it is in the parent organization
                if request_user.organization != organization:
                    request_user_in_parent = False
                    parent_organization = organization.parent
                    while parent_organization is not None:
                        if request_user.organization == parent_organization:
                            request_user_in_parent = True
                        parent_organization = parent_organization.parent

                    if not request_user_in_parent:
                        raise exceptions.PermissionDenied(
                            "Not autho;ized to register user for another "
                            "organization.")
            else:
                raise exceptions.PermissionDenied(
                    "Not authorized to register a user.")

    def validate_locations_hierarchy(self, data):
        # locations are only updated in case its an employee
        organization = data.get('organization')
        locations = data.get('authorized_locations')

        if locations is not None:
            # get locations available to the organization tree
            organizations = organization.get_descendants(include_self=True)
            available_locations = Location.objects.filter(
                organization__in=organizations)

            # check if requested locations are not associated with the
            # organization
            invalid_locations = []
            for location in locations:
                if location not in available_locations:
                    invalid_locations.append(location.id)

            if len(invalid_locations) != 0:
                raise serializers.ValidationError({
                    "authorized_locations": (
                        "The locations {} are not associated with the "
                        "organization: {}".format(
                            invalid_locations, organization.name))
                })

    def validate(self, data):
        # get validated data
        data = super().validate(data)

        # get the user requesting this registration and raise an exception
        # if none is found
        request_user = get_user_from_serializer(self, raise_exception=True)
        self.validate_organization_user(data=data, request_user=request_user)
        self.validate_locations_hierarchy(data=data)
        return data

    def get_cleaned_data(self):
        cleaned_data = super().get_cleaned_data()
        cleaned_data['group'] = self.validated_data.get('group', None)
        cleaned_data['authorized_locations'] = self.validated_data.get(
            'authorized_locations', None)
        cleaned_data['organization'] = self.validated_data.get(
            'organization', None)
        return cleaned_data


class JWTSerializer(serializers.Serializer):
    """
    Serializer for JWT authentication.
    """
    token = serializers.CharField()
    user = serializers.SerializerMethodField()

    def get_user(self, obj):
        """
        Required to allow using custom USER_DETAILS_SERIALIZER in
        JWTSerializer. Defining it here to avoid circular imports
        """
        user = get_user_from_serializer(self, raise_exception=True)
        JWTUserDetailsSerializer = AppUserDetailRetrieveSerializer
        user_data = JWTUserDetailsSerializer(
            obj['user'], context=self.context).data
        return user_data
