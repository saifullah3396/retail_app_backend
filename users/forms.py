# pylint: disable=missing-module-docstring
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.core.exceptions import ValidationError

from .models import AppUser

# from locations.models import Location


class AppUserCreationForm(UserCreationForm):
    """
    Provides a custom user creation form view for admin site
    """

    class Meta(UserCreationForm):
        model = AppUser
        fields = (
            'organization',
            # 'authorized_locations'
        )

    def clean(self):
        cleaned_data = super().clean()
        group_list = [g.name for g in cleaned_data.get('groups')]
        in_groups = {
            group: group in group_list for group in [
                'organization_admin',
                'employee']
        }

        organization = cleaned_data.get('organization')
        if any(list(in_groups.values())) and organization is None:
            raise ValidationError(
                "Please choose the organization with which the user "
                "associated."
            )

        # authorized_locations = cleaned_data.get('authorized_locations')
        # if sub_organization is not None:
        #     available_locations = Location.objects.filter(
        #         organization=organization,
        #         sub_organization=sub_organization)
        # else:
        #     available_locations = Location.objects.filter(
        #         organization=organization)

        # invalid_locations = []
        # for location in authorized_locations:
        #     if location not in available_locations:
        #         invalid_locations.append(location.title)

        # if len(invalid_locations) != 0:
        #     if sub_organization is not None:
        #         raise ValidationError(
        #             "The locations {} are not associated with the "
        #             "sub_organization: {}".format(
        #                 invalid_locations, sub_organization.title)
        #         )
        #     else:
        #         raise ValidationError(
        #             "The locations {} are not associated with the "
        #             "organization: {}".format(
        #                 invalid_locations, organization.title)
        #         )


class AppUserChangeForm(UserChangeForm):
    """
    Provides a custom user update form view for admin site
    """

    class Meta:
        model = AppUser
        fields = (
            'organization',
            # 'authorized_locations'
        )
