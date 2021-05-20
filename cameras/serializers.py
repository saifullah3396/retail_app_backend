"""
Defines the serializers used in the Cameras api.
"""

from rest_framework import serializers

from cameras.models import Camera
from measurement_frames.models import MeasurementFrame
from measurement_frames.serializers import \
    MeasurementFrameDetailSerializerDS


# pylint: disable=missing-class-docstring
class CameraDetailSerializerDS(serializers.ModelSerializer):
    class Meta:
        model = Camera
        fields = '__all__'

    measurement_frame = serializers.SerializerMethodField()

    def get_measurement_frame(self, camera):
        """
        Return the frames to which camera is associated.
        """
        try:
            measurement_frame = \
                MeasurementFrame.objects.get(id=camera.measurement_frame.id)
            return MeasurementFrameDetailSerializerDS(
                measurement_frame, context=self.context).data
        except MeasurementFrame.DoesNotExist:
            return None

    def to_representation(self, instance):
        data = super().to_representation(instance)

        repr_data = {}
        repr_data['id'] = data['id']
        repr_data['ip_addr'] = data['ip_addr']
        repr_data['points_frame'] = {
            "p0": [data['p0_coord_in_frame_x'], data['p0_coord_in_frame_y']],
            "p1": [data['p1_coord_in_frame_x'], data['p1_coord_in_frame_y']],
            "p2": [data['p2_coord_in_frame_x'], data['p2_coord_in_frame_y']],
            "p3": [data['p3_coord_in_frame_x'], data['p3_coord_in_frame_y']],
        }

        repr_data['points_image'] = {
            "p0": [data['p0_coord_in_image_x'], data['p0_coord_in_image_y']],
            "p1": [data['p1_coord_in_image_x'], data['p1_coord_in_image_y']],
            "p2": [data['p2_coord_in_image_x'], data['p2_coord_in_image_y']],
            "p3": [data['p3_coord_in_image_x'], data['p3_coord_in_image_y']],
        }

        repr_data['measurement_frame'] = data['measurement_frame']
        return repr_data
