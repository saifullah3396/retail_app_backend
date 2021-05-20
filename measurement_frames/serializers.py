"""
Defines the serializers used in the api.
"""

from rest_framework import serializers

from .models import MeasurementFrame


class MeasurementFrameDetailSerializerDS(serializers.ModelSerializer):
    """
    Serializer for measurement frame uesd whiled sending its data to the
    deepstream servers.
    """

    class Meta:
        model = MeasurementFrame
        fields = ('pixel_pose_x', 'pixel_pose_y', 'pixel_pose_theta',)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        repr_data = {
            "x": data['pixel_pose_x'],
            "y": data['pixel_pose_y'],
            "theta": data['pixel_pose_theta'],
        }
        return repr_data
