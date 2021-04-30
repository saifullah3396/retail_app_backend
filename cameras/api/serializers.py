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
        fields = ('id', 'ip_addr', 'coords', 'block')

    def to_representation(self, instance):
        data = super().to_representation(instance)

        repr_data = {}
        repr_data['id'] = data['id']
        repr_data['ip_addr'] = data['ip_addr']
        if data['coords']:
            repr_data['coords'] = {
                "x": data['coords'][0],
                "y": data['coords'][1]
            }
        repr_data['block'] = data['block']
        return repr_data


# pylint: disable=missing-class-docstring
class CameraCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Camera
        fields = ('ip_addr', 'coords', 'block')
        extra_kwargs = {
            'ip_addr': {'required': True},
            'coords': {'required': True},
            'block': {'required': True},
        }

    def to_representation(self, instance):
        data = super().to_representation(instance)

        repr_data = {}
        repr_data['id'] = data['id']
        repr_data['ip_addr'] = data['ip_addr']
        if data['coords']:
            repr_data['coords'] = {
                "x": data['coords'][0],
                "y": data['coords'][1]
            }
        repr_data['block'] = data['block']
        return repr_data

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


class CameraUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Camera
        fields = (
            'ip_addr',
            'coords',
            'block',
            'point_coords_in_frame',
            'point_coords_in_image',
            'deepstream_server',
            'measurement_frame')

    def update(self, instance, validated_data):
        try:
            return super().update(instance, validated_data)
        except IntegrityError as ex:
            raise serializers.ValidationError({"detail": ex.__cause__})
