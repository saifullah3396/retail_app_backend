"""
Defines the serializers used in the organizations api.
"""

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from rest_framework import exceptions, serializers

from app_organizations.models import OrganizationGroup
from core.utils import (field_invalid_error, field_not_found_error,
                        get_organization_user_model, get_user_from_serializer)
from outlets.models import Outlet, OutletUser
from outlets.utils import create_outlet

USER_MODEL = get_user_model()
ORGANIZATION_USER_MODEL = OutletUser


# pylint: disable=missing-class-docstring
class OutletCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Outlet
        fields = ('id', 'name', 'slug',  'avatar')
        extra_kwargs = {
            'name': {'required': True},
            'slug': {'read_only': True}
        }

    def create(self, validated_data):
        try:
            return self._create(validated_data)
        except IntegrityError as ex:
            raise serializers.ValidationError({"detail": ex.__cause__})

    def _create(self, validated_data):
        """
        Create the organization using the organizations create utility.
        """
        organization = self.context['view'].validate_kwargs()
        return create_outlet(
            user=get_user_from_serializer(self),
            name=validated_data["name"],
            organization=organization
        )


class OutletListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Outlet
        fields = ('id', 'name', 'slug', 'avatar')


class OutletRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Outlet
        fields = ('id', 'name', 'slug', 'avatar')


class OutletUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Outlet
        fields = ('id', 'name', 'slug', 'avatar')
        extra_kwargs = {
            'slug': {'read_only': True},
        }

    def update(self, instance, validated_data):
        try:
            return super().update(instance, validated_data)
        except IntegrityError as ex:
            raise serializers.ValidationError({"detail": ex.__cause__})


class OutletUserCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = OutletUser
        fields = ('id', 'user')
        extra_kwargs = {
            'user': {'required': True}
        }

    def validate_user(self, user):
        organization = self.context['view'].get_organization()
        if not organization.users.filter(id=user.id).exists():
            raise exceptions.ValidationError(field_not_found_error())
        return user

    def create(self, validated_data):
        try:
            return self._create(validated_data)
        except IntegrityError as ex:
            raise serializers.ValidationError({"detail": ex.__cause__})

    def _create(self, validated_data):
        """
        Create the outlet user by adding it to outlet
        """
        outlet = self.context['view'].validate_kwargs()
        return outlet.add_user(validated_data['user'])


class OutletUserListSerializer(serializers.ModelSerializer):

    class Meta:
        model = OutletUser
        fields = ('id', 'user', 'outlet')


class OutletUserRetrieveSerializer(serializers.ModelSerializer):

    class Meta:
        model = OutletUser
        fields = ('id', 'user', 'outlet')


class OutletUserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OutletUser
        fields = ('id', 'user', 'organization')
        extra_kwargs = {
            'id': {'read_only': True},
            'user': {'read_only': True},
            'outlet': {'read_only': True}
        }

    def update(self, instance, validated_data):
        try:
            return super().update(instance, validated_data)
        except IntegrityError as ex:
            raise serializers.ValidationError({"detail": ex.__cause__})
