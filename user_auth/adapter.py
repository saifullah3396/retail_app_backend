from allauth.account.adapter import DefaultAccountAdapter
from allauth.utils import build_absolute_uri
from backend import settings
from core.permissions import UserGroups
from django.urls import reverse


class AppAccountAdapter(DefaultAccountAdapter):

    def save_user(self, request, user, form, commit=True):
        user = super().save_user(request, user, form, commit)
        data = form.cleaned_data

        # set user permission groups
        group = data.get('group')
        if group is not None:
            user.groups.add(group)

        # add organization to user
        organization = data.get('organization')
        if organization is not None:
            user.organization = organization

        # add all authorized locations to user if its an employee
        if group.name == UserGroups.EMPLOYEE_GROUP.name:
            locations = data.get('authorized_locations')
            if locations is not None:
                for location in locations:
                    user.authorized_locations.add(location)

        # commit user
        user.save()
        return user

    def get_email_confirmation_url(self, request, emailconfirmation):
        url = reverse("verify_email", args=[emailconfirmation.key])
        ret = build_absolute_uri(request, url)
        return ret
