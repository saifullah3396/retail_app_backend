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

    def validate(self, data):
        data = super().validate(data)

        # any groups are assigned to user?
        if data.get('groups') is None:
            raise serializers.ValidationError(
                {
                    "groups": "Group to be assigned to this user required."
                }
            )
        else:
            requested_groups = [g.name for g in data.get('groups')]

            # check if any of the following are to be assigned to user
            # ['organization_admin', 'sub_organization_admin', 'employee']
            available_in_requested = {
                group: group in requested_groups
                for group in settings.REGISTER_AVAILABLE_GROUPS
            }

            # if none of the available group is found in requested groups
            if not any(list(available_in_requested.values())):
                raise serializers.ValidationError(
                    {
                        "groups": "Can only be assigned one of the following "
                        "{}".format(settings.REGISTER_AVAILABLE_GROUPS)
                    }
                )
            else:
                # get user requesting for a new registration
                request_user = None
                request = self.context.get("request")
                if request and hasattr(request, "user"):
                    request_user = request.user

                if request_user is None:
                    # raise unauthorized error if user is not found
                    # most probably this will never get called
                    raise exceptions.PermissionDenied()

                # make sure an organization is available for which the group is
                # for example employee of which organization?
                organization = data.get('organization')
                sub_organization = data.get('sub_organization')
                if organization is None:
                    raise serializers.ValidationError(
                        {
                            "organization": "Please choose the organization "
                            "with which the user associated."
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
                            if request_user.organization != \
                                    sub_organization.organization:
                                raise exceptions.PermissionDenied(
                                    "Requested sub_organization is not a part "
                                    "of the requested organization.")
                        else:
                            if request_user.sub_organization != \
                                    sub_organization:
                                raise exceptions.PermissionDenied(
                                    "Not authorized to register user for "
                                    "another sub_organization.")

                    # check if the request user is authorized to assign
                    # organization admin
                    request_user_in_group = {
                        group: is_in_group(request_user, group)
                        for group in settings.REGISTER_AVAILABLE_GROUPS
                    }

                    if available_in_requested['organization_admin'] and not \
                            request_user_in_group['organization_admin']:
                        raise exceptions.PermissionDenied(
                            "You must be an organization admin to assign "
                            "another organization admin."
                        )

                    if available_in_requested['sub_organization_admin']:
                        if sub_organization is None:
                            raise serializers.ValidationError(
                                {
                                    "sub_organization": "Please choose the "
                                    "sub_organization with which the user "
                                    "associated."
                                }
                            )

                        if not request_user_in_group['organization_admin'] and \
                                not request_user_in_group[
                                    'sub_organization_admin']:
                            raise exceptions.PermissionDenied(
                                "You must either be an organization admin or "
                                "a sub_organization admin to assign "
                                "another sub_organization admin."
                            )

                    if available_in_requested['employee']:
                        if not request_user_in_group['organization_admin'] and \
                                not request_user_in_group[
                                    'sub_organization_admin']:
                            raise exceptions.PermissionDenied(
                                "You must either be an organization admin or "
                                "a sub_organization admin to assign "
                                "another employee."
                            )

                # make sure we are sent locations for which this user is
                # authorized to
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
                            raise serializers.ValidationError(
                                "The locations {} are not associated with the "
                                "sub_organization: {}".format(
                                    invalid_locations, sub_organization.name)
                            )
                        else:
                            raise serializers.ValidationError(
                                "The locations {} are not associated with the "
                                "organization: {}".format(
                                    invalid_locations, organization.name)
                            )
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
