from rest_framework.generics import ListAPIView, RetrieveAPIView
from ..models import Location, Floor, Block
from .serializers import LocationSerializer, FloorSerializer, BlockSerializer


class LocationListView(ListAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer


class LocationDetailView(RetrieveAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer


class FloorListView(ListAPIView):
    serializer_class = FloorSerializer

    def get_queryset(self):
        queryset = Floor.objects.all()
        location = self.request.query_params.get('location', None)
        if location is not None:
            # get the floor number
            queryset = queryset.filter(location__title=location)

        return queryset


class FloorDetailView(RetrieveAPIView):
    serializer_class = FloorSerializer

    def get_queryset(self):
        queryset = Floor.objects.all()
        location = self.request.query_params.get('location', None)
        if location is not None:
            # get the floor number
            queryset = queryset.filter(location__title=location)

        return queryset


class BlockListView(ListAPIView):
    serializer_class = BlockSerializer

    def get_queryset(self):
        queryset = Block.objects.all()
        location = self.request.query_params.get('location', None)
        if location is not None:
            # get the floor number
            queryset = queryset.filter(floor__location__title=location)

        floor_number = self.request.query_params.get('floor', None)
        if floor_number is not None:
            # get the floor number
            queryset = queryset.filter(floor__number=floor_number)
        return queryset


class BlockDetailView(RetrieveAPIView):
    queryset = Block.objects.all()
    serializer_class = BlockSerializer
