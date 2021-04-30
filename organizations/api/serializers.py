"""
Defines the serializers used in the organizations api.
"""

from django.db import IntegrityError
from rest_framework import serializers

from organizations.models import Organization


# pylint: disable=missing-class-docstring
class OrganizationCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Organization
        fields = ('name', 'parent',)
        extra_kwargs = {
            'name': {'required': True},
        }

    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except IntegrityError as ex:
            raise serializers.ValidationError({"detail": ex.__cause__})


class OrganizationListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Organization
        fields = ('id', 'name', 'parent',)
        extra_kwargs = {
            'name': {'required': True},
        }

    def to_representation(self, instance):
        data = super().to_representation(instance)
        repr_data = {}
        repr_data['id'] = data['id']
        repr_data['name'] = data['name']
        if data['parent']:
            try:
                parent_organization = \
                    Organization.objects.get(id=data['parent'])
                repr_data['parent'] = {
                    'id': parent_organization.id,
                    'name': parent_organization.name
                }
            except Organization.DoesNotExist:
                return None
        return repr_data


class OrganizationDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Organization
        fields = ('id', 'name', 'parent',)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        repr_data = {}
        repr_data['id'] = data['id']
        repr_data['name'] = data['name']
        if data['parent']:
            try:
                parent_organization = \
                    Organization.objects.get(id=data['parent'])
                repr_data['parent'] = {
                    'id': parent_organization.id,
                    'name': parent_organization.name
                }
            except Organization.DoesNotExist:
                return None
        return repr_data


class OrganizationUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Organization
        fields = ('name', 'parent',)
        extra_kwargs = {
            'name': {'required': True},
            'parent': {'read_only': True},
        }

    def update(self, instance, validated_data):
        try:
            return super().update(instance, validated_data)
        except IntegrityError as ex:
            raise serializers.ValidationError({"detail": ex.__cause__})
