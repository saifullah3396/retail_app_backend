"""
Defines the serializers used in the organizations api.
"""

from rest_framework import serializers

from organizations.models import Organization


# pylint: disable=missing-class-docstring
class OrganizationListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Organization
        fields = ('id', 'name', 'parent',)
        extra_kwargs = {
            'id': {'read_only': True},
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
        extra_kwargs = {
            'id': {'read_only': True},
            'name': {'required': True},
            'parent': {'read_only': True},
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
