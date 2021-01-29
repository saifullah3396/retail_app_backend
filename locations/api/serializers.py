from rest_framework import serializers
from ..models import Location, Floor, Block


class LocationSerializerAdminAccess(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ('id', 'name', 'organization', 'sub_organization')


class FloorSerializerAdminAccess(serializers.ModelSerializer):
    class Meta:
        model = Floor
        fields = ('id', 'number', 'location')


class BlockSerializerAdminAccess(serializers.ModelSerializer):
    floor = FloorSerializerAdminAccess()
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


class LocationSerializerAppUserAccess(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ('id', 'name', 'organization', 'sub_organization')


class BlockDetailsSerializerAppUserAccess(serializers.ModelSerializer):
    class Meta:
        model = Block
        fields = ('id', 'name', 'floor_map', 'coordinate_frame', 'floor')


class FloorDetailsSerializerAppUserAccess(serializers.ModelSerializer):
    blocks = serializers.SerializerMethodField()

    def get_blocks(self, floor):
        # return all blocks in this floor
        blocks = Blocks.objects.filter(floor=floor)
        return \
            BlockDetailsSerializerAppUserAccess(blocks, many=True).data

    class Meta:
        model = Floor
        fields = ('id', 'number', 'location', 'blocks')


class LocationDetailsSerializerAppUserAccess(serializers.ModelSerializer):
    floors = serializers.SerializerMethodField()

    def get_floors(self, location):
        # return all floors in this location
        print("GeTTING FLOORS", location.id)
        floors = Floor.objects.filter(location__id=location.id)
        return \
            FloorDetailsSerializerAppUserAccess(floors, many=True).data

    class Meta:
        model = Location
        fields = ('id', 'name', 'organization', 'sub_organization', 'floors')

    def to_representation(self, location):
        data = \
            super(
                LocationDetailsSerializerAppUserAccess,
                self).to_representation(location)
        return {'location': data}
