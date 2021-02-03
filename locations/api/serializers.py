"""
Defines the serializers used in the locations api.
"""

from rest_framework import serializers

from ..models import Block, Floor, Location


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'


class FloorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Floor
        fields = '__all__'


class BlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Block
        fields = '__all__'


class BlockDetailSerializer(BlockSerializer):
    class Meta:
        model = Block
        fields = '__all__'


class FloorDetailSerializer(serializers.ModelSerializer):
    blocks = serializers.SerializerMethodField()

    def get_blocks(self, floor):
        # return all blocks in this floor
        blocks = Block.objects.filter(floor=floor)
        return \
            BlockDetailSerializer(blocks, many=True).data

    class Meta:
        model = Floor
        fields = ('id', 'number', 'location', 'blocks')


class BlockInLocationDetailSerializer(BlockSerializer):
    class Meta:
        model = Block
        fields = ('id', 'name', 'floor_map', 'coordinate_frame')


class FloorInLocationDetailSerializer(serializers.ModelSerializer):
    blocks = serializers.SerializerMethodField()

    def get_blocks(self, floor):
        # return all blocks in this floor
        blocks = Block.objects.filter(floor=floor)
        return \
            BlockInLocationDetailSerializer(blocks, many=True).data

    class Meta:
        model = Floor
        fields = ('id', 'number', 'blocks')


class LocationDetailSerializer(serializers.ModelSerializer):
    floors = serializers.SerializerMethodField()

    def get_floors(self, location):
        # return all floors in this location
        floors = Floor.objects.filter(location__id=location.id)
        return \
            FloorInLocationDetailSerializer(floors, many=True).data

    class Meta:
        model = Location
        fields = ('id', 'name', 'organization', 'floors')
