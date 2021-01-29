from rest_framework.generics import ListAPIView, RetrieveAPIView
from ..models import Camera
from .serializers import CameraSerializer


class CameraListView(ListAPIView):
    queryset = Camera.objects.all()
    serializer_class = CameraSerializer


class CameraDetailView(RetrieveAPIView):
    queryset = Camera.objects.all()
    serializer_class = CameraSerializer


class CameraFilterListView(ListAPIView):
    serializer_class = CameraSerializer

    def get_queryset(self):
        queryset = Camera.objects.all()
        location = self.request.query_params.get('location', None)
        if location is not None:
            # get all cameras in input location
            queryset = queryset.filter(block__floor__location__title=location)

        floor_number = self.request.query_params.get('floor', None)
        if floor_number is not None:
            # get all cameras in input floor
            queryset = queryset.filter(block__floor__number=floor_number)

        block = self.request.query_params.get('block', None)
        if floor_number is not None:
            # get all cameras in input block
            queryset = queryset.filter(block__name=block)
        return queryset


class CameraFilterDetailView(RetrieveAPIView):
    serializer_class = CameraSerializer

    def get_queryset(self):
        queryset = Camera.objects.all()
        location = self.request.query_params.get('location', None)
        if location is not None:
            # get all cameras in input location
            queryset = queryset.filter(block__floor__location__title=location)

        floor_number = self.request.query_params.get('floor', None)
        if floor_number is not None:
            # get all cameras in input floor
            queryset = queryset.filter(block__floor__number=floor_number)

        block = self.request.query_params.get('block', None)
        if floor_number is not None:
            # get all cameras in input block
            queryset = queryset.filter(block__name=block)
        return queryset
