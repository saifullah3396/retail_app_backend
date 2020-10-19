from rest_framework import serializers
from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email
from rest_auth.registration.serializers import RegisterSerializer
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from organizations.models import Organization, SubOrganization
from locations.models import Location


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

    @todo: Validate the following:
        1. If the user requesting registration is making a new organization
            admin, then he must be the admin of that organization himself.
        2. If the user requesting registration is making a new sub_organization
            admin, then he must be the admin of that sub_organization himself.
        3. Make sure this call can only be made by admins, organization admins,
            sub-organization admins
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
            raise ValidationError(
                'Organization {} does not exist.'.format(organization))
        return organization[0]

    def validate_sub_organization(self, sub_organization_name):
        sub_organization = SubOrganization.objects.filter(
            name=sub_organization_name)
        if not sub_organization:
            raise ValidationError(
                'SubOrganization {} does not exist.'.format(sub_organization))
        return sub_organization[0]

    def validate_locations(self, location_names):
        locations = []
        for location_name in location_names:
            try:
                location = Location.objects.get(name=location_name)
                locations.append(location)
            except Location.DoesNotExist:
                raise ValidationError(
                    'Location {} does not exist.'.format(location_name))
        return locations

    def validate_groups(self, group_names):
        groups = []
        for group_name in group_names:
            try:
                group = Group.objects.get(name=group_name)
                groups.append(group)
            except Group.DoesNotExist:
                raise ValidationError(
                    'Group {} does not exist.'.format(group_name))
        return groups

    def validate(self, data):
        data = super().validate(data)

        # any groups are assigned to user?
        if data.get('groups') is None:
            raise ValidationError(
                "Please choose the group for this user."
            )
        else:
            group_list = [g.name for g in data.get('groups')]

            # check if any of the following are assigned to user
            # ['organization_admin', 'sub_organization_admin', 'employee']
            in_groups = {
                group: group in group_list for group in [
                    'organization_admin',
                    'sub_organization_admin',
                    'employee']
            }

            if any(list(in_groups.values())):
                # make sure an organization is available for which the role is
                # for example employee of which organization?
                organization = data.get('organization')
                if organization is None:
                    raise ValidationError(
                        "Please choose the organization with which the user "
                        "associated."
                    )

                # get user requesting for a new registration
                user = None
                request = self.context.get("request")
                if request and hasattr(request, "user"):
                    user = request.user

                raise ValidationError(
                    "Please choose the group for this user."
                )

                # if sub_organization_admin role exists, check for that as well
                sub_organization = data.get('sub_organization')
                if in_groups['sub_organization_admin'] \
                        and sub_organization is None:
                    raise ValidationError(
                        "Please choose the sub_organization with which the "
                        "user associated."
                    )

                # make sure we are sent locations for which this user is
                # authorized to
                locations = data.get('locations')
                if locations is None:
                    raise ValidationError(
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
                            raise ValidationError(
                                "The locations {} are not associated with the "
                                "sub_organization: {}".format(
                                    invalid_locations, sub_organization.name)
                            )
                        else:
                            raise ValidationError(
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
