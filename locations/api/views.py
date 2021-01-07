from rest_framework import permissions
from rest_framework_jwt import authentication
from rest_framework.generics import ListAPIView, RetrieveAPIView
from ..models import Location, Floor, Block
from .serializers import \
    (
        LocationSerializerAdminAccess,
        FloorSerializerAdminAccess,
        BlockSerializerAdminAccess,
        LocationDetailsSerializerAppUserAccess
    )
from .filters import HasLocationAuthorizationFilter


class AdminLocationListView(ListAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializerAdminAccess
    permission_classes = (permissions.IsAuthenticated, permissions.IsAdminUser)
    authentication_classes = [authentication.JSONWebTokenAuthentication]


class AdminLocationDetailView(RetrieveAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializerAdminAccess
    permission_classes = (permissions.IsAuthenticated, permissions.IsAdminUser)
    authentication_classes = [authentication.JSONWebTokenAuthentication]


class AdminFloorListView(ListAPIView):
    serializer_class = FloorSerializerAdminAccess
    permission_classes = (permissions.IsAuthenticated, permissions.IsAdminUser)
    authentication_classes = [authentication.JSONWebTokenAuthentication]

    def get_queryset(self):
        queryset = Floor.objects.all()
        location = self.request.query_params.get('location', None)
        if location is not None:
            # get the floor number
            queryset = queryset.filter(location__title=location)

        return queryset


class AdminFloorDetailView(RetrieveAPIView):
    serializer_class = FloorSerializerAdminAccess
    permission_classes = (permissions.IsAuthenticated, permissions.IsAdminUser)
    authentication_classes = [authentication.JSONWebTokenAuthentication]

    def get_queryset(self):
        queryset = Floor.objects.all()
        location = self.request.query_params.get('location', None)
        if location is not None:
            # get the floor number
            queryset = queryset.filter(location__title=location)

        return queryset


class AdminBlockListView(ListAPIView):
    serializer_class = BlockSerializerAdminAccess
    permission_classes = (permissions.IsAuthenticated, permissions.IsAdminUser)
    authentication_classes = [authentication.JSONWebTokenAuthentication]

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


class AdminBlockDetailView(RetrieveAPIView):
    queryset = Block.objects.all()
    serializer_class = BlockSerializerAdminAccess
    permission_classes = (permissions.IsAuthenticated, permissions.IsAdminUser)
    authentication_classes = [authentication.JSONWebTokenAuthentication]


class LocationDetailsAppUserAccess(RetrieveAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationDetailsSerializerAppUserAccess
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = [authentication.JSONWebTokenAuthentication]
    filter_backends = [HasLocationAuthorizationFilter]
