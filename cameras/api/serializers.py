"""
Defines the serializers used in the Cameras api.
"""

from rest_framework import serializers

from cameras.models import Camera


# pylint: disable=missing-class-docstring
class CameraListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Camera
        fields = ('id', 'ip_addr', 'coords', 'block')
        extra_kwargs = {
            'id': {'read_only': True},
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


class CameraDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Camera
        fields = ('id', 'ip_addr', 'coords', 'block')
        extra_kwargs = {
            'id': {'read_only': True},
        }
