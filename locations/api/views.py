from rest_framework import permissions,pagination,filters, status
from rest_framework_jwt import authentication
from rest_framework.generics import ListAPIView, RetrieveAPIView,RetrieveUpdateDestroyAPIView
from ..models import Location, Floor, Block
from .serializers import \
    (
        LocationSerializerAdminAccess,
        FloorSerializerAdminAccess,
        BlockSerializerAdminAccess,
        LocationDetailsSerializerAppUserAccess,
        LocationSerializer
    )
from .filters import HasLocationAuthorizationFilter
from ..permissions import (
    LocationsRUDPermissions
    )


class PaginationConfig(pagination.PageNumberPagination):
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 100

class OrganizationsRUDView(RetrieveUpdateDestroyAPIView):
    serializer_class = LocationSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        LocationsRUDPermissions)
    authentication_classes = [authentication.JSONWebTokenAuthentication]
    pagination_class = PaginationConfig
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['id', 'name', 'organization', 'sub_organization  ']
    filterset_fields = {
        'name': ['exact', 'icontains'],
    }

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            # return all if it is super admin
            queryset = \
                Organization.objects.all().order_by('name')
            return queryset
        else:
            # else can only be an organization admin according to permissions
            # on the view. Return all sub-organizations under the users
            # organization
            queryset = \
                Organization.objects.filter(
                    id=user.organization.id).order_by('name')
            return queryset

    def delete(self, request, *args, **kwargs):
        # update delete response
        try:
            organization_name = self.get_object().name
            resp = super(OrganizationsRUDView, self).delete(
                request, *args, **kwargs)
            return Response(data={
                "msg": "Organization {} deleted successfully.".format(
                    organization_name)}, status=status.HTTP_200_OK)
        except Organization.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

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



