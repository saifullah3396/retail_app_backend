"""
Defines the serializers used in the locations api.
"""

from django.db import IntegrityError
from rest_framework import exceptions, serializers, status

from locations.models import Block, Floor, Location


# pylint: disable=missing-class-docstring
class LocationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ('id', 'name', 'organization',)


class LocationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ('id', 'name', 'organization',)
        extra_kwargs = {
            'name': {'required': True},
            'organization': {'required': True},
        }

    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except IntegrityError as ex:
            raise serializers.ValidationError({"detail": ex.__cause__})


class FloorListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Floor
        fields = ('id', 'number', 'location',)


class FloorCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Floor
        fields = ('id', 'number', 'location',)
        extra_kwargs = {
            'number': {'required': True},
            'location': {'required': True},
        }

    def create(self, validated_data):
        try:
            location = validated_data.get('location')
            number = validated_data.get('number')

            # get all floors in location
            floors = Floor.objects.filter(location=location).order_by('number')
            if floors and number != floors.last().number + 1:
                raise exceptions.ValidationError(detail={
                    "number": "Please add an intermediate floor value."
                }, code=status.HTTP_400_BAD_REQUEST)

            return super().create(validated_data)
        except IntegrityError as ex:
            raise serializers.ValidationError({"detail": ex.__cause__})


class BlockListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Block
        fields = ('id', 'name', 'floor')


class BlockCreateSerializer(serializers.ModelSerializer):
    floor_map_url = serializers.SerializerMethodField(read_only=True)

    def get_floor_map_url(self, block):
        """
        Returns the absolute url of the block floor map.
        """
        if block.floor_map and hasattr(block.floor_map, 'url'):
            return self.context.get('request').\
                build_absolute_uri(block.floor_map.url)

    class Meta:
        model = Block
        fields = ('id', 'name', 'floor_map', 'floor_map_url',
                  'pixels_to_m_x', 'pixels_to_m_y', 'floor')
        extra_kwargs = {
            'name': {'required': True},
            'floor_map': {'required': True, 'write_only': True},
            'floor_map_url': {'required': True, 'read_only': True},
            'pixels_to_m_x': {'required': True},
            'pixels_to_m_y': {'required': True},
            'floor': {'required': True},
        }

    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except IntegrityError as ex:
            raise serializers.ValidationError({"detail": ex.__cause__})


class BlockDetailSerializer(serializers.ModelSerializer):
    floor_map_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Block
        fields = ('id', 'name', 'floor_map_url',
                  'pixels_to_m_x', 'pixels_to_m_y', 'floor')

    def get_floor_map_url(self, block):
        """
        Returns the absolute url of the block floor map.
        """
        if block.floor_map and hasattr(block.floor_map, 'url'):
            return self.context.get('request').\
                build_absolute_uri(block.floor_map.url)


class BlockUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Block
        fields = ('id', 'name', 'pixels_to_m_x', 'pixels_to_m_y', 'floor')
        extra_kwargs = {
            'floor': {'read_only': True}
        }

    def update(self, instance, validated_data):
        try:
            return super().update(instance, validated_data)
        except IntegrityError as ex:
            raise serializers.ValidationError({"detail": ex.__cause__})


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
        fields = ('id', 'number', 'blocks', 'location')


class FloorUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Floor
        fields = []

    def update(self, instance, validated_data):
        try:
            return super().update(instance, validated_data)
        except IntegrityError as ex:
            raise serializers.ValidationError({"detail": ex.__cause__})


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


class LocationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ('id', 'name', 'organization')
        extra_kwargs = {
            'organization': {'read_only': True}
        }

    def update(self, instance, validated_data):
        try:
            return super().update(instance, validated_data)
        except IntegrityError as ex:
            raise serializers.ValidationError({"detail": ex.__cause__})
