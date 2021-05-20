"""
Defines the serializers used in the locations api.
"""
# pylint: disable=missing-class-docstring

from django.db import IntegrityError
from rest_framework import exceptions, serializers, status

from locations.models import Block, Floor, Location, OutletLocation


class BlockListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Block
        fields = ('id', 'name')


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
                  'pixels_to_m_x', 'pixels_to_m_y')
        extra_kwargs = {
            'name': {'required': True},
            'floor_map': {'required': True, 'write_only': True},
            'floor_map_url': {'required': True, 'read_only': True},
            'pixels_to_m_x': {'required': True},
            'pixels_to_m_y': {'required': True}
        }

    def create(self, validated_data):
        try:
            validated_data['floor'] = self.context['view'].validate_kwargs()
            return super().create(validated_data)
        except IntegrityError as ex:
            raise serializers.ValidationError({"detail": ex.__cause__})


class BlockRetrieveSerializer(serializers.ModelSerializer):
    floor_map_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Block
        fields = ('id', 'name', 'floor_map_url',
                  'pixels_to_m_x', 'pixels_to_m_y')

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
        fields = ('id', 'name', 'pixels_to_m_x', 'pixels_to_m_y')

    def update(self, instance, validated_data):
        try:
            return super().update(instance, validated_data)
        except IntegrityError as ex:
            raise serializers.ValidationError({"detail": ex.__cause__})


class FloorListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Floor
        fields = ('id', 'number')


class FloorCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Floor
        fields = ('id', 'number')
        extra_kwargs = {
            'number': {'required': True},
        }

    def validate_number(self, number):
        # get all floors in location
        location = self.context['view'].get_location()
        floors = Floor.objects.filter(location=location).order_by('number')
        if floors.exists():
            if number != floors.last().number + 1:
                raise exceptions.ValidationError(detail={
                    "number": "Please add an intermediate floor value."
                }, code=status.HTTP_400_BAD_REQUEST)
        else:
            if number != 0:
                raise exceptions.ValidationError(detail={
                    "number": "Floor numbers start from 0."
                }, code=status.HTTP_400_BAD_REQUEST)
        return number

    def create(self, validated_data):
        try:
            validated_data['location'] = self.context['view'].validate_kwargs()
            return super().create(validated_data)
        except IntegrityError as ex:
            raise serializers.ValidationError({"detail": ex.__cause__})


class FloorRetrieveSerializer(serializers.ModelSerializer):
    blocks = serializers.SerializerMethodField(read_only=True)

    def get_blocks(self, floor):
        """
        Return the details of all the blocks in the floor
        """
        blocks = Block.objects.filter(floor=floor)
        return \
            BlockRetrieveSerializer(
                blocks, many=True, context=self.context).data

    class Meta:
        model = Floor
        fields = ('id', 'number', 'blocks')


class LocationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ('id', 'name')


class LocationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ('id', 'name')
        extra_kwargs = {
            'name': {'required': True},
        }
        abstract = True

    def create(self, validated_data):
        try:
            validated_data = self._updated_data(validated_data)
            return super().create(validated_data)
        except IntegrityError as ex:
            raise serializers.ValidationError({"detail": ex.__cause__})

    def _updated_data(self, validated_data):
        raise NotImplementedError()


class OutletLocationCreateSerializer(LocationCreateSerializer):
    class Meta:
        model = OutletLocation
        fields = ('id', 'name')
        extra_kwargs = {
            'name': {'required': True},
        }

    def _updated_data(self, validated_data):
        validated_data['outlet'] = self.context['view'].validate_kwargs()
        return validated_data


class LocationRetrieveSerializer(serializers.ModelSerializer):
    floors = serializers.SerializerMethodField(read_only=True)

    def get_floors(self, location):
        """
        Return the details of all the floors in the location
        """
        floors = Floor.objects.filter(location__id=location.id)
        return \
            FloorRetrieveSerializer(
                floors, many=True, context=self.context).data

    class Meta:
        model = OutletLocation
        fields = ('id', 'name', 'floors')


class LocationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OutletLocation
        fields = ('id', 'name')
        extra_kwargs = {
            'id': {'read_only': True}
        }

    def update(self, instance, validated_data):
        try:
            return super().update(instance, validated_data)
        except IntegrityError as ex:
            raise serializers.ValidationError({"detail": ex.__cause__})
