"""
Defines the serializers used in the organizations api.
"""

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from rest_framework import serializers

from app_organizations.models import AppOrganization, OrganizationGroup
from app_organizations.utils import create_organization
from core.utils import get_organization_user_model, get_user_from_serializer

USER_MODEL = get_user_model()
ORGANIZATION_USER_MODEL = get_organization_user_model()


# pylint: disable=missing-class-docstring
class AppOrganizationCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = AppOrganization
        fields = ('id', 'name',  'avatar')
        extra_kwargs = {
            'name': {'required': True},
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
        return create_organization(
            user=get_user_from_serializer(self),
            name=validated_data["name"],
            slug=None,
            is_active=True,
            model=self.Meta.model,
            org_user_defaults={
                "is_admin": True
            }
        )


class AppOrganizationListSerializer(serializers.ModelSerializer):

    class Meta:
        model = AppOrganization
        fields = ('id', 'name', 'avatar')


class AppOrganizationRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppOrganization
        fields = ('id', 'name', 'avatar')


class AppOrganizationUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = AppOrganization
        fields = ('id', 'name', 'avatar')
        extra_kwargs = {
            'slug': {'read_only': True},
        }

    def update(self, instance, validated_data):
        try:
            return super().update(instance, validated_data)
        except IntegrityError as ex:
            raise serializers.ValidationError({"detail": ex.__cause__})


class AppOrganizationUserCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = ORGANIZATION_USER_MODEL
        fields = ('id', 'user')
        extra_kwargs = {
            'user': {'required': True}
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
        organization = self.context['view'].get_organization()
        return organization.add_user(validated_data['user'])


class AppOrganizationUserListSerializer(serializers.ModelSerializer):

    class Meta:
        model = ORGANIZATION_USER_MODEL
        fields = ('id', 'user')


class OrganizationGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrganizationGroup
        fields = ['name', 'authority']


class AppOrganizationUserRetrieveSerializer(serializers.ModelSerializer):
    groups = serializers.SerializerMethodField()

    class Meta:
        model = ORGANIZATION_USER_MODEL
        fields = ('id', 'user', 'organization', 'groups')

    def get_groups(self, instance):
        return OrganizationGroupSerializer(
            instance.groups,
            many=True,
            context=self.context).data


class AppOrganizationUserUpdateSerializer(serializers.ModelSerializer):
    groups = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ORGANIZATION_USER_MODEL
        fields = ('id', 'user', 'organization', 'groups')
        # Currently organization has no field that can be updated after
        # creation except the groups which are updated from
        # organization/groups/users url
        extra_kwargs = {
            'id': {'read_only': True},
            'user': {'read_only': True},
            'organization': {'read_only': True}
        }

    def get_groups(self, instance):
        return OrganizationGroupSerializer(
            instance.groups,
            many=True,
            context=self.context).data

    def update(self, instance, validated_data):
        try:
            return super().update(instance, validated_data)
        except IntegrityError as ex:
            raise serializers.ValidationError({"detail": ex.__cause__})
