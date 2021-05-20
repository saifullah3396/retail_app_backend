"""
Defines the serializers used in the Cameras api.
"""

from django.db import IntegrityError
from rest_framework import serializers

from cameras.models import Camera


# pylint: disable=missing-class-docstring
class CameraListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Camera
        fields = ('id', 'ip_addr', 'coords')


# pylint: disable=missing-class-docstring
class CameraCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Camera
        fields = ('id', 'ip_addr', 'coords',)
        extra_kwargs = {
            'ip_addr': {'required': True},
            'coords': {'required': True},
        }

    def create(self, validated_data):
        try:
            validated_data['block'] = self.context['view'].validate_kwargs()
            print('validated_data', validated_data)
            return super().create(validated_data)
        except IntegrityError as ex:
            raise serializers.ValidationError({"detail": ex.__cause__})


class CameraRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Camera
        fields = ('id', 'ip_addr', 'coords')


class CameraUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Camera
        fields = ('id', 'ip_addr', 'coords')

    def update(self, instance, validated_data):
        try:
            return super().update(instance, validated_data)
        except IntegrityError as ex:
            raise serializers.ValidationError({"detail": ex.__cause__})
