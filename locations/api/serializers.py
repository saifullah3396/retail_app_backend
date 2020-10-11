from rest_framework import serializers
from ..models import Location, Floor, Block


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ('id', 'title', 'desc', 'organization', 'sub_organization')


class FloorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Floor
        fields = ('id', 'number', 'location')


class BlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Floor
        fields = ('id', 'number', 'floor')
