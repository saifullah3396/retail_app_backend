"""
Defines the serializers used in the locations api.
"""

from rest_framework import serializers

from ..models import Block, Floor, Location, MeasurementFrame


# pylint: disable=missing-class-docstring
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

class MeasurementFrameSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeasurementFrame
        fields = '__all__'

class BlockDetailSerializer(serializers.ModelSerializer):
    floor_map = serializers.SerializerMethodField()
    floor_map_resolution = serializers.SerializerMethodField()

    class Meta:
        model = Block
        fields = ('id', 'name', 'floor_map', 'floor_map_resolution')

    def get_floor_map(self, block):
        """
        Returns the absolute url of the block floor map.
        """
        request = self.context.get('request')
        floor_map_url = block.floor_map.url
        return request.build_absolute_uri(floor_map_url)

    def get_floor_map_resolution(self, block):
        """
        Generates a floor map resolution method field.
        """
        return {
            "x": block.pixels_to_m_x,
            "y": block.pixels_to_m_y
        }

class FloorDetailSerializer(serializers.ModelSerializer):
    blocks = serializers.SerializerMethodField()

    def get_blocks(self, floor):
        """
        Return the details of all the blocks in the floor
        """
        blocks = Block.objects.filter(floor=floor)
        return \
            BlockDetailSerializer(blocks, many=True, context=self.context).data

    class Meta:
        model = Floor
        fields = ('id', 'number', 'blocks')

class LocationDetailSerializer(serializers.ModelSerializer):
    floors = serializers.SerializerMethodField()

    def get_floors(self, location):
        """
        Return the details of all the floors in the location
        """
        floors = Floor.objects.filter(location__id=location.id)
        return \
            FloorDetailSerializer(floors, many=True, context=self.context).data

    class Meta:
        model = Location
        fields = ('id', 'name', 'organization', 'floors')
