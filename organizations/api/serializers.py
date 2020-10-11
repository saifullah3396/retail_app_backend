from rest_framework import serializers
from ..models import Organization, SubOrganization


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ('id', 'title', 'desc')


class SubOrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubOrganization
        fields = ('id', 'title', 'desc', 'organization')
