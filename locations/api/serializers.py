from rest_framework import serializers
from ..models import Location, Floor, Block


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
        blocks = Blocks.objects.filter(floor=floor)
        return \
            BlockDetailsSerializer(blocks, many=True).data

    class Meta:
        model = Floor
        fields = ('id', 'number', 'location', 'blocks')


class LocationDetailSerializer(serializers.ModelSerializer):
    floors = serializers.SerializerMethodField()

    def get_floors(self, location):
        # return all floors in this location
        floors = Floor.objects.filter(location__id=location.id)
        return \
            FloorDetailsSerializer(floors, many=True).data

    class Meta:
        model = Location
        fields = ('id', 'name', 'organization', 'floors')

    def to_representation(self, location):
        data = \
            super(
                LocationDetailsSerializer,
                self).to_representation(location)
        return {'location': data}
