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
    floor = FloorSerializer()
    floor_map_url = serializers.SerializerMethodField()

    class Meta:
        model = Block
        fields = ('id', 'name', 'coordinate_frame', 'floor', 'floor_map_url')

    def get_floor_map_url(self, block):
        request = self.context.get('request')
        if block.floor_map and hasattr(block.floor_map, 'url'):
            floor_map_url = block.floor_map.url
            return request.build_absolute_uri(floor_map_url)
        else:
            None
