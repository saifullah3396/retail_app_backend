"""
Defines the serializers used in the Cameras api.
"""

from rest_framework import serializers

from ..models import Camera


class CameraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Camera
        fields = ('id', 'place_name', 'ip_addr', 'coords', 'block')
