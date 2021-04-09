"""
Defines the serializers used in the Cameras api.
"""

from rest_framework import serializers

from ..models import Camera


class CameraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Camera
        fields = ('id', 'ip_addr', 'coords', 'block')

    def to_representation(self, obj):
        data = super().to_representation(obj)
        print('data', data)

        repr_data = {}
        repr_data['id'] = data['id']
        repr_data['ip_addr'] = data['ip_addr']
        if data['coords']:
            repr_data['coords'] = {
                "x": data['coords'][0],
                "y": data['coords'][1]
            }
        repr_data['block'] = data['block']
        print(repr_data)
        return repr_data
