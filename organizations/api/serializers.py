from rest_framework import serializers
from ..models import Organization, SubOrganization


class AdminOnlyOrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ('id', 'name', 'desc')


class AdminOnlySubOrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubOrganization
        fields = ('id', 'name', 'desc', 'organization')
