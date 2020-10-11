from rest_framework.generics import ListAPIView, RetrieveAPIView
from ..models import Camera
from .serializers import CameraSerializer


class CameraListView(ListAPIView):
    queryset = Camera.objects.all()
    serializer_class = CameraSerializer


class CameraDetailView(RetrieveAPIView):
    queryset = Camera.objects.all()
    serializer_class = CameraSerializer
