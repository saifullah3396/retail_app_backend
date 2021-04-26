"""
Defines the serializers used in the locations api.
"""

from rest_framework import serializers

from measurement_frames.models import MeasurementFrame


# pylint: disable=missing-class-docstring
class MeasurementFrameListSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeasurementFrame
        fields = ('id', 'name', 'pixel_pose_x',
                  'pixel_pose_y', 'pixel_pose_theta', 'block')
        extra_kwargs = {
            'name': {'required': True},
            'pixel_pose_x': {'required': True},
            'pixel_pose_y': {'required': True},
            'pixel_pose_theta': {'required': True},
            'block': {'required': True},
        }


class MeasurementFrameDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeasurementFrame
        fields = ('id', 'name', 'pixel_pose_x',
                  'pixel_pose_y', 'pixel_pose_theta', 'block')
        extra_kwargs = {
            'block': {'read_only': True},
        }
