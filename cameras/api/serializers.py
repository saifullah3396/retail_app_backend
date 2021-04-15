"""
Defines the serializers used in the Cameras api.
"""

from rest_framework import serializers

from cameras.models import Camera


# pylint: disable=missing-class-docstring
class CameraSerializer(serializers.ModelSerializer):

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
