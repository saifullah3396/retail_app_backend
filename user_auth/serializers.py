"""
Defines the serializers for application user registration/authentication.
"""
from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email
from django.contrib.auth import get_user_model
from rest_auth.registration.serializers import RegisterSerializer
from rest_auth.serializers import PasswordResetSerializer
from rest_framework import serializers

from users.api.app_user.serializers import AppUserRetrieveSerializer


# pylint: disable=abstract-method
class RegistrationSerializer(RegisterSerializer):
    """
    Extends the register serializer to add custom fields.
    """

    # This is not needed now since user has unique email only if deleted
    # condition

    # def save(self, request):
    #     """
    #     Extend the adapter to create user from update_or_create method so it
    #     goes through safe delete
    #     """
    #     adapter = get_adapter()
    #     self.cleaned_data = self.get_cleaned_data()
    #     email = self.cleaned_data.get("email")
    #     user, _ = get_user_model().objects.update_or_create(email=email)
    #     adapter.save_user(request, user, self)
    #     self.custom_signup(request, user)
    #     setup_user_email(request, user, [])
    #     return user

# pylint: disable=abstract-method


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
        user_data = AppUserRetrieveSerializer(
            obj['user'], context=self.context).data
        return user_data


class PasswordResetSerializer(PasswordResetSerializer):
    def get_email_options(self):
        return {
            'email_template_name': 'account/password_reset_message.txt',
        }
