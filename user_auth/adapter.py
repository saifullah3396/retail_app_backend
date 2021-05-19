"""
Defines the adapters used in user account creation and rest-auth.
"""

from allauth.account.adapter import DefaultAccountAdapter
from allauth.utils import build_absolute_uri
from rest_framework import serializers

from backend.settings import ACCOUNT_EMAIL_CONFIRMATION_URL
from user_auth.models import DefaultUserGroups, UserGroup


class AppAccountAdapter(DefaultAccountAdapter):
    """
    Custom implements the DefaultAccountAdapter to save our custom AppUser
    according to our requirements.
    """

    def save_user(self, request, user, form, commit=True):
        user = super().save_user(request, user, form, commit)

        # by default the user will be assigned to FREE_USER group
        try:
            free_user_group = UserGroup.objects.get(
                name=DefaultUserGroups.FREE_USER.name)
            user.groups.add(free_user_group)
        except UserGroup.DoesNotExist:
            raise serializers.ValidationError(
                'Error while trying to assign group to user.')

        # commit user
        user.save()
        return user

    def get_email_confirmation_url(self, request, emailconfirmation):
        url = ACCOUNT_EMAIL_CONFIRMATION_URL.format(emailconfirmation.key)
        ret = build_absolute_uri(request, url)
        return ret
