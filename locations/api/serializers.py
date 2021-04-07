"""
Defines the serializers used in the locations api.
"""

from rest_framework import serializers

from ..models import Block, Floor, Location


class LocationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'


class FloorListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Floor
        fields = ('id', 'number')


class BlockListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Block
        fields = ('id', 'name')


class BlockDetailSerializer(serializers.ModelSerializer):
    floor_map = serializers.SerializerMethodField()
    floor_map_resolution = serializers.SerializerMethodField()

    class Meta:
        model = Block
        fields = ('id', 'name', 'floor_map', 'floor_map_resolution')

    def get_floor_map(self, block):
        request = self.context.get('request')
        if block.floor_map and hasattr(block.floor_map, 'url'):
            floor_map_url = block.floor_map.url
            return request.build_absolute_uri(floor_map_url)
        else:
            None

    def get_floor_map_resolution(self, block):
        return {
            "x": block.pixels_to_m_x,
            "y": block.pixels_to_m_y
        }


class FloorDetailSerializer(serializers.ModelSerializer):
    blocks = serializers.SerializerMethodField()

    def get_blocks(self, floor):
        # return all blocks in this floor
        blocks = Block.objects.filter(floor=floor)
        return \
            BlockDetailSerializer(blocks, many=True, context=self.context).data

    class Meta:
        model = Floor
        fields = ('id', 'number', 'blocks')


class LocationDetailSerializer(serializers.ModelSerializer):
    floors = serializers.SerializerMethodField()

    def get_floors(self, location):
        # return all floors in this location
        floors = Floor.objects.filter(location__id=location.id)
        return \
            FloorDetailSerializer(floors, many=True, context=self.context).data

    class Meta:
        model = Location
        fields = ('id', 'name', 'organization', 'floors')
