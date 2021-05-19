"""
Defines the serializers used in the locations api.
"""

from django.db import IntegrityError
from rest_framework import exceptions, serializers, status

from locations.api.serializers import FloorDetailSerializer
from locations.models import Block, Floor, OrganizationLocation


# pylint: disable=missing-class-docstring
class LocationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationLocation
        fields = ('id', 'name')


class LocationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationLocation
        fields = ('id', 'name')
        extra_kwargs = {
            'name': {'required': True},
        }

    def create(self, validated_data):
        try:
            validated_data['organization'] = \
                self.context['view'].get_organization()
            return super().create(validated_data)
        except IntegrityError as ex:
            raise serializers.ValidationError({"detail": ex.__cause__})


class LocationRetrieveSerializer(serializers.ModelSerializer):
    floors = serializers.SerializerMethodField(read_only=True)

    def get_floors(self, location):
        """
        Return the details of all the floors in the location
        """
        floors = Floor.objects.filter(location__id=location.id)
        return \
            FloorDetailSerializer(floors, many=True, context=self.context).data

    class Meta:
        model = OrganizationLocation
        fields = ('id', 'name', 'floors')


class LocationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationLocation
        fields = ('id', 'name')
        extra_kwargs = {
            'id': {'read_only': True}
        }

    def update(self, instance, validated_data):
        try:
            return super().update(instance, validated_data)
        except IntegrityError as ex:
            raise serializers.ValidationError({"detail": ex.__cause__})
