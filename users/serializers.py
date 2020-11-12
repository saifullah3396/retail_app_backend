from rest_framework import serializers
from rest_framework import status, exceptions
from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email
from rest_auth.registration.serializers import RegisterSerializer
from django.contrib.auth.models import Group
from organizations.models import Organization, SubOrganization
from locations.models import Location
from .permissions import is_in_group
from backend import settings


class AppRegisterSerializer(RegisterSerializer):
    """
    Extends the register serializer to add custom fields. This serializer takes
    permission groups as to accept one of the following fields:
        [
            'organization_admin',
            'sub_organization_admin',
            'employee'
        ]
    If the user is organization_admin, it checks whether organization info is
    provided. Same is done for sub_organization_admin and sub_organization.
    Finally it checks whether the locations provided as inputs are existing and
    are available to the organization (or suborganization).
    """

    organization = serializers.CharField(max_length=150, required=False)
    sub_organization = serializers.CharField(
        max_length=150, required=False)
    locations = serializers.ListField(
        child=serializers.CharField(max_length=150), required=False)
    groups = serializers.ListField(
        child=serializers.CharField(max_length=150), required=False)

    def validate_organization(self, organization_name):
        organization = Organization.objects.filter(name=organization_name)
        if not organization:
            raise serializers.ValidationError(
                'Organization {} does not exist.'.format(organization_name))
        return organization[0]

    def validate_sub_organization(self, sub_organization_name):
        sub_organization = SubOrganization.objects.filter(
            name=sub_organization_name)
        if not sub_organization:
            raise serializers.ValidationError(
                'SubOrganization {} does not exist.'.format(
                    sub_organization_name))
        return sub_organization[0]

    def validate_locations(self, location_names):
        locations = []
        for location_name in location_names:
            try:
                location = Location.objects.get(name=location_name)
                locations.append(location)
            except Location.DoesNotExist:
                raise serializers.ValidationError(
                    'Location {} does not exist.'.format(location_name))
        return locations

    def validate_groups(self, group_names):
        groups = []
        for group_name in group_names:
            try:
                group = Group.objects.get(name=group_name)
                groups.append(group)
            except Group.DoesNotExist:
                raise serializers.ValidationError(
                    'Group {} does not exist.'.format(group_name))
        return groups

    def get_request_user(self, raise_exception=False):
        # get user requesting for a new registration
        request_user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            request_user = request.user
        else:
            if raise_exception:
                # raise unauthorized error if user is not found
                # most probably this will never get called
                raise exceptions.PermissionDenied()
        return request_user

    def validate_organization_user(self, data, request_user):
        # get data in groups
        groups = [g.name for g in data.get('groups')]

        # check if any of the possible groups are found in groups
        # this finds the overlap of two lists
        requested_groups = {
            group: authority
            for group, authority in
            settings.REGISTRATION_GROUPS_WITH_AUTHORITY.items()
            if group in groups
        }

        # if none of the available groups are found in requested groups
        if len(requested_groups) == 0:
            raise serializers.ValidationError(
                {
                    "groups": "Can only be assigned one of the following "
                    "{}".format(
                        settings.REGISTRATION_GROUPS_WITH_AUTHORITY.keys())
                }
            )
        else:
            # make sure an organization is available for which the group is
            # for example employee of which organization?
            organization = data.get('organization')
            if organization is None:
                raise serializers.ValidationError(
                    {
                        "organization": "Please choose the organization "
                        "with which the user is associated."
                    }
                )

            # if sub_organization group is assigned then sub_organization must
            # exist
            sub_organization = data.get('sub_organization')
            if 'sub_organization_admin' in requested_groups:
                if sub_organization is None:
                    raise serializers.ValidationError(
                        {
                            "sub_organization": "Please choose the "
                            "sub_organization with which the user "
                            "is associated."
                        }
                    )

            if not request_user.is_staff:
                # check if request user is in the same organization as the
                # registered user
                if request_user.organization != organization:
                    raise exceptions.PermissionDenied(
                        "Not authorized to register user for another "
                        "organization.")

                # check if request user is the same sub organization as
                # registered user
                if sub_organization is not None:
                    if request_user.sub_organization is None:
                        # if request user has no sub organization then the
                        # parent of this organization must match with request
                        # user organization
                        if request_user.organization != \
                                sub_organization.organization:
                            raise exceptions.PermissionDenied(
                                "Requested sub_organization is not a part "
                                "of the requested organization.")
                    else:
                        # see if the sub organizations match
                        if request_user.sub_organization != \
                                sub_organization:
                            raise exceptions.PermissionDenied(
                                "Not authorized to register user for "
                                "another sub_organization.")

                # check if the request user is authorized to assign user group
                # first find request user authority
                request_user_authority = -1
                request_groups_with_required_authority = {}
                for (group, authority) in \
                        settings.REGISTRATION_GROUPS_WITH_AUTHORITY.items():
                    if is_in_group(request_user, group):
                        if authority >= request_user_authority:
                            request_user_authority = authority

                # for each assigned group check if the user has the authority
                # to assign it
                for (group, authority) in requested_groups.items():
                    if request_user_authority < authority:
                        raise exceptions.PermissionDenied(
                            "You do not have the permission to perform this "
                            "operation.")

    def validate_locations_hierarchy(self, data):
        # make sure we are sent locations for which this user is
        # authorized to
        organization = data.get('organization')
        sub_organization = data.get('sub_organization')
        locations = data.get('locations')
        if locations is None:
            raise serializers.ValidationError(
                "Please choose locations which are to be authorized to "
                "the user."
            )
        else:
            # get locations available to the organization or
            # sub_organization
            if sub_organization is not None:
                available_locations = Location.objects.filter(
                    organization=organization,
                    sub_organization=sub_organization)
            else:
                available_locations = Location.objects.filter(
                    organization=organization)

            # check if requested locations are not associated with the
            # organization
            invalid_locations = []
            for location in locations:
                if location not in available_locations:
                    invalid_locations.append(location.name)

            if len(invalid_locations) != 0:
                if sub_organization is not None:
                    raise serializers.ValidationError({
                        "locations": (
                            "The locations {} are not associated with the "
                            "sub_organization: {}".format(
                                invalid_locations, sub_organization.name))
                    })
                else:
                    raise serializers.ValidationError({
                        "locations": (
                            "The locations {} are not associated with the "
                            "organization: {}".format(
                                invalid_locations, organization.name))
                    })

    def validate(self, data):
        # get validated data
        data = super().validate(data)

        # get the user requesting this registration and raise an exception
        # if none is found
        request_user = self.get_request_user(True)
        if data.get('groups') is not None:
            self.validate_organization_user(
                data=data, request_user=request_user)
        else:
            if not request_user.is_staff:
                raise serializers.ValidationError(
                    {
                        "groups": "Group to be assigned to this user required."
                    }
                )
        self.validate_locations_hierarchy(data=data)
        return data

    def get_cleaned_data(self):
        cleaned_data = super().get_cleaned_data()
        cleaned_data['groups'] = self.validated_data.get('groups', None)
        cleaned_data['locations'] = self.validated_data.get(
            'locations', None)
        cleaned_data['organization'] = self.validated_data.get(
            'organization', None)
        cleaned_data['sub_organization'] = self.validated_data.get(
            'sub_organization', None)
        return cleaned_data


class JWTSerializer(serializers.Serializer):
    """
    Serializer for JWT authentication.
    """
    token = serializers.CharField()
    user = serializers.SerializerMethodField()

    def get_request_user(self, raise_exception=False):
        # get user requesting for a new registration
        request_user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            request_user = request.user
        else:
            if raise_exception:
                # raise unauthorized error if user is not found
                # most probably this will never get called
                raise exceptions.PermissionDenied()
        return request_user

    def get_user(self, obj):
        """
        Required to allow using custom USER_DETAILS_SERIALIZER in
        JWTSerializer. Defining it here to avoid circular imports
        """
        user = self.get_request_user(raise_exception=True)
        if user.is_staff:
            JWTUserDetailsSerializer = AdminUserSerializerAdminAccess
        else:
            JWTUserDetailsSerializer = AppUserSerializerAppUserAccess
        user_data = JWTUserDetailsSerializer(
            obj['user'], context=self.context).data
        return user_data
