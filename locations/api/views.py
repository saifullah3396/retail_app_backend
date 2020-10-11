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
    queryset = Floor.objects.all()
    serializer_class = FloorSerializer


class FloorDetailView(RetrieveAPIView):
    queryset = Floor.objects.all()
    serializer_class = FloorSerializer


class BlockListView(ListAPIView):
    queryset = Block.objects.all()
    serializer_class = BlockSerializer


class BlockDetailView(RetrieveAPIView):
    queryset = Block.objects.all()
    serializer_class = BlockSerializer
