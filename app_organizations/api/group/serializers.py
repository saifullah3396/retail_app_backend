"""
Defines the serializers used in user REST api views.
"""
# pylint: disable=missing-class-docstring

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from rest_framework import exceptions, serializers

from app_organizations.models import (DefaultOrganizationGroups,
                                      OrganizationGroup)
from core.utils import get_organization_user_model

ORGANIZATION_USER_MODEL = get_organization_user_model()


class OrganizationGroupListSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrganizationGroup
        fields = ['name', 'authority']


class OrganizationGroupCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrganizationGroup
        fields = ['name', 'authority']
        extra_kwargs = {
            'name': {'required': True},
            'authority': {'required': True}
        }

    def validate_authority(self, authority):
        # authority of new groups cannot be greater than existing member user
        if authority < DefaultOrganizationGroups.MEMBER.value:
            raise exceptions.ValidationError(
                "Can only be greater than or equal to {}".format(
                    DefaultOrganizationGroups.MEMBER.value))
        return authority

    def create(self, validated_data):
        try:
            organization = self.context['view'].validate_kwargs()
            validated_data['organization'] = organization
            instance, _ = self.Meta.model.objects.update_or_create(
                validated_data)
            return instance
        except IntegrityError as ex:
            raise serializers.ValidationError({"detail": ex.__cause__})


class OrganizationGroupRetrieveUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ORGANIZATION_USER_MODEL
        fields = ['id', 'user']


class OrganizationGroupRetrieveSerializer(serializers.ModelSerializer):
    users = serializers.SerializerMethodField()

    class Meta:
        model = OrganizationGroup
        fields = ['name', 'authority', 'organization', 'users']

    def get_users(self, instance):
        return OrganizationGroupRetrieveUserSerializer(
            instance.organization_user_set.all(),
            many=True,
            context=self.context).data

    def to_representation(self, instance):
        data = super().to_representation(instance)
        users = []
        for user in data['users']:
            users.append(user['id'])
        data['users'] = users
        return data


class OrganizationGroupUpdateSerializer(serializers.ModelSerializer):
    users = serializers.SerializerMethodField()

    class Meta:
        model = OrganizationGroup
        fields = ['name', 'authority', 'organization', 'users']
        extra_kwargs = {
            "name": {"required": False},
            "authority": {"required": False},
            'organization': {'read_only': True},
        }

    def validate_authority(self, authority):
        # authority of new groups cannot be greater than existing member user
        if authority < DefaultOrganizationGroups.MEMBER.value:
            raise exceptions.ValidationError(
                "Can only be greater than or equal to {}".format(
                    DefaultOrganizationGroups.MEMBER.value))
        return authority

    def get_users(self, instance):
        return OrganizationGroupRetrieveUserSerializer(
            instance.organization_user_set.all(),
            many=True,
            context=self.context).data

    def update(self, instance, validated_data):
        try:
            return super().update(instance, validated_data)
        except IntegrityError as ex:
            raise serializers.ValidationError({"detail": ex.__cause__})

    def to_representation(self, instance):
        data = super().to_representation(instance)
        users = []
        for user in data['users']:
            users.append(user['id'])
        data['users'] = users
        return data


class AddRemoveUserSerializerBase(serializers.ModelSerializer):
    users = serializers.SerializerMethodField()
    user = serializers.IntegerField(required=True, write_only=True)

    class Meta:
        model = OrganizationGroup
        fields = ['name', 'authority', 'organization', 'users', 'user']
        extra_kwargs = {
            'name': {'read_only': True},
            'authority': {'read_only': True},
            'organization': {'read_only': True},
        }

    def get_users(self, instance):
        return OrganizationGroupRetrieveUserSerializer(
            instance.organization_user_set.all(),
            many=True,
            context=self.context).data

    def validate_user(self, user):
        try:
            user_to_be_added = ORGANIZATION_USER_MODEL.objects.get(pk=user)

            # make sure the request user has authority to add pk
            # user to the group
            request_user = self.context['request'].user

            # note that authority is highest with lowest value
            if user_to_be_added.highest_group.authority < \
                    request_user.highest_group.authority:
                raise exceptions.ValidationError(
                    "You are unathorized to make changes to this user.")
            return user_to_be_added
        except ORGANIZATION_USER_MODEL.DoesNotExist:
            raise exceptions.ValidationError("User does not exist.")

    def to_representation(self, instance):
        data = super().to_representation(instance)
        users = []
        for user in data['users']:
            users.append(user['id'])
        data['users'] = users
        return data


class AddUserSerializer(AddRemoveUserSerializerBase):

    def update(self, instance, validated_data):
        try:
            instance.organization_user_set.add(validated_data['user'])
            return instance
        except IntegrityError as ex:
            raise serializers.ValidationError({"detail": ex.__cause__})


class RemoveUserSerializer(AddRemoveUserSerializerBase):

    def update(self, instance, validated_data):
        try:
            instance.organization_user_set.remove(validated_data['user'])
            return instance
        except IntegrityError as ex:
            raise serializers.ValidationError({"detail": ex.__cause__})
