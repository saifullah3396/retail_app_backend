"""
Defines the serializers used in the organizations api.
"""

from rest_framework import serializers

from organizations.models import Organization


# pylint: disable=missing-class-docstring
class OrganizationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Organization
        fields = '__all__'

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
