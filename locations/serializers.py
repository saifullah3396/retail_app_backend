"""
Defines the serializers used in the Locations api.
"""

from rest_framework import serializers

from .models import MeasurementFrame


class MeasurementFrameDetailSerializerDeepstream(serializers.ModelSerializer):
    class Meta:
        model = MeasurementFrame
        fields = ('pixel_pose_x', 'pixel_pose_y', 'pixel_pose_theta',)

    def to_representation(self, obj):
        data = super().to_representation(obj)
        repr_data = {
            "x": data['pixel_pose_x'],
            "y": data['pixel_pose_y'],
            "theta": data['pixel_pose_theta'],
        }
        return repr_data
