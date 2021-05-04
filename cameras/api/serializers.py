"""
Defines the serializers used in the Cameras api.
"""

from django.db import IntegrityError
from rest_framework import serializers

from cameras.api.utils import camera_to_representation
from cameras.models import Camera


# pylint: disable=missing-class-docstring
class CameraListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Camera
        fields = ('id', 'ip_addr', 'coords', 'block')

    def to_representation(self, instance):
        return camera_to_representation(super().to_representation(instance))


# pylint: disable=missing-class-docstring
class CameraCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Camera
        fields = (
            'id',
            'ip_addr',
            'coords',
            'point_coords_in_frame',
            'point_coords_in_image',
            'block',
            'deepstream_server',
            'measurement_frame')
        extra_kwargs = {
            'ip_addr': {'required': True},
            'coords': {'required': True},
            'block': {'required': True},
        }

    def to_representation(self, instance):
        return camera_to_representation(super().to_representation(instance))

    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except IntegrityError as ex:
            raise serializers.ValidationError({"detail": ex.__cause__})


class CameraDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Camera
        fields = (
            'id',
            'ip_addr',
            'coords',
            'block',
            'point_coords_in_frame',
            'point_coords_in_image',
            'deepstream_server',
            'measurement_frame')

    def to_representation(self, instance):
        return camera_to_representation(super().to_representation(instance))


class CameraUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Camera
        fields = (
            'id',
            'ip_addr',
            'coords',
            'block',
            'point_coords_in_frame',
            'point_coords_in_image',
            'deepstream_server',
            'measurement_frame')
        extra_kwargs = {
            'block': {'read_only': True},
        }

    def to_representation(self, instance):
        return camera_to_representation(super().to_representation(instance))

    def update(self, instance, validated_data):
        try:
            return super().update(instance, validated_data)
        except IntegrityError as ex:
            raise serializers.ValidationError({"detail": ex.__cause__})
