from rest_framework import serializers
from ..models import Organization, SubOrganization


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ('id', 'name', 'desc')


class SubOrganizationSerializer(serializers.ModelSerializer):

    class Meta:
        model = SubOrganization
        fields = ('id', 'name', 'desc', 'organization')
