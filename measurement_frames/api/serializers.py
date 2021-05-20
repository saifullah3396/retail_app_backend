"""
Defines the serializers used in the locations api.
"""

from django.db import IntegrityError
from rest_framework import serializers

from measurement_frames.models import MeasurementFrame


# pylint: disable=missing-class-docstring
class MeasurementFrameListSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeasurementFrame
        fields = ('id', 'name', 'pixel_pose_x',
                  'pixel_pose_y', 'pixel_pose_theta')


class MeasurementFrameCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeasurementFrame
        fields = (
            'id',
            'name',
            'pixel_pose_x',
            'pixel_pose_y',
            'pixel_pose_theta')
        extra_kwargs = {
            'name': {'required': True},
            'pixel_pose_x': {'required': True},
            'pixel_pose_y': {'required': True},
            'pixel_pose_theta': {'required': True}
        }

    def create(self, validated_data):
        try:
            validated_data['block'] = self.context['view'].validate_kwargs()
            return super().create(validated_data)
        except IntegrityError as ex:
            raise serializers.ValidationError({"detail": ex.__cause__})


class MeasurementFrameRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeasurementFrame
        fields = (
            'id',
            'name',
            'pixel_pose_x',
            'pixel_pose_y',
            'pixel_pose_theta')


class MeasurementFrameUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeasurementFrame
        fields = ('id', 'name', 'pixel_pose_x',
                  'pixel_pose_y', 'pixel_pose_theta')

    def update(self, instance, validated_data):
        try:
            return super().update(instance, validated_data)
        except IntegrityError as ex:
            raise serializers.ValidationError({"detail": ex.__cause__})
