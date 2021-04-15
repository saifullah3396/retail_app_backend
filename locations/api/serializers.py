"""
Defines the serializers used in the locations api.
"""

from rest_framework import serializers

from locations.models import Block, Floor, Location


# pylint: disable=missing-class-docstring
class LocationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ('id', 'name', 'organization',)
        extra_kwargs = {
            'id': {'read_only': True},
            'name': {'required': True},
            'organization': {'required': True},
        }


class FloorListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Floor
        fields = ('id', 'number', 'location',)
        extra_kwargs = {
            'id': {'read_only': True},
            'number': {'required': True},
            'location': {'required': True},
        }


class BlockListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Block
        fields = ('id', 'name', 'floor_map',
                  'pixels_to_mm_x', 'pixels_to_m_y', 'floor')
        extra_kwargs = {
            'id': {'read_only': True},
            'name': {'required': True},
            'floor_map': {'required': True},
            'pixels_to_mm_x': {'required': True},
            'pixels_to_m_y': {'required': True},
            'floor': {'required': True},
        }


class BlockDetailSerializer(serializers.ModelSerializer):
    floor_map_url = serializers.SerializerMethodField(read_only=True)
    floor_map_resolution = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Block
        fields = ('id', 'name', 'floor_map_url', 'floor_map_resolution')
        extra_kwargs = {
            'id': {'read_only': True},
        }

    def get_floor_map_url(self, block):
        """
        Returns the absolute url of the block floor map.
        """
        return self.context.get('request').\
            build_absolute_uri(block.floor_map.url)

    def get_floor_map_resolution(self, block):
        """
        Generates a floor map resolution method field.
        """
        return {
            "x": block.pixels_to_m_x,
            "y": block.pixels_to_m_y
        }


class FloorDetailSerializer(serializers.ModelSerializer):
    blocks = serializers.SerializerMethodField(read_only=True)

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
        extra_kwargs = {
            'number': {'read_only': True}
        }


class LocationDetailSerializer(serializers.ModelSerializer):
    floors = serializers.SerializerMethodField(read_only=True)

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
        extra_kwargs = {
            'id': {'read_only': True}
        }
