
"""
Defines the REST API views for locations models.
"""


from app_organizations.permissions import OrganizationDjangoModelPermissions
from core import views
from locations.api.serializers import (BlockCreateSerializer,
                                       BlockListSerializer,
                                       BlockRetrieveSerializer,
                                       BlockUpdateSerializer,
                                       FloorCreateSerializer,
                                       FloorListSerializer,
                                       FloorRetrieveSerializer,
                                       LocationListSerializer,
                                       LocationRetrieveSerializer,
                                       LocationUpdateSerializer,
                                       OutletLocationCreateSerializer)
from locations.models import Block, Floor, OutletLocation
from locations.views import (BaseFloorListGetQuerySet,
                             BaseFloorRetrieveGetQuerySet,
                             BaseOutletLocationListGetQuerySet,
                             BaseOutletLocationRetrieveGetQuerySet)
from outlets.views import (BaseOutletListGetQuerySet,
                           BaseOutletRetrieveGetQuerySet)


class OutletLocationsListCreateDestroyView(
        views.CoreListAPIView,
        views.CoreCreateAPIView,
        views.CoreListDestroyAPIView,
        BaseOutletListGetQuerySet):

    """
    Defines the outlet locations list-create-destroy view.
    """

    queryset = OutletLocation.objects.none()
    permission_classes = (OrganizationDjangoModelPermissions,)
    ordering_fields = ['id', 'name']
    filterset_fields = {
        'name': ['exact', 'icontains'],
    }
    order_by = 'name'
    list_serializer = LocationListSerializer
    create_serializer = OutletLocationCreateSerializer


class OutletLocationsRetrieveUpdateDestroyView(
        views.CoreRetrieveAPIView,
        views.CoreUpdateAPIView,
        views.CoreDestroyAPIView,
        BaseOutletRetrieveGetQuerySet):
    """
    Defines the outlet locations list-create-destroy view.
    """

    queryset = OutletLocation.objects.none()  # Added for model permissions
    permission_classes = (OrganizationDjangoModelPermissions,)
    retrieve_serializer = LocationRetrieveSerializer
    update_serializer = LocationUpdateSerializer


class FloorsListCreateDestroyView(
        views.CoreListAPIView,
        views.CoreCreateAPIView,
        views.CoreListDestroyAPIView,
        BaseOutletLocationListGetQuerySet):

    """
    Defines the floors list-create-destroy view.
    """

    queryset = Floor.objects.none()
    permission_classes = (OrganizationDjangoModelPermissions,)
    ordering_fields = ['id', 'number']
    filterset_fields = {
        'number': ['exact'],
    }
    order_by = 'number'
    list_serializer = FloorListSerializer
    create_serializer = FloorCreateSerializer


class FloorsRetrieveUpdateDestroyView(
        views.CoreRetrieveAPIView,  # no update possible on floors
        views.CoreDestroyAPIView,
        BaseOutletLocationRetrieveGetQuerySet):
    """
    Defines the floors list-create-destroy view.
    """

    queryset = Floor.objects.none()  # Added for model permissions
    permission_classes = (OrganizationDjangoModelPermissions,)
    retrieve_serializer = FloorRetrieveSerializer


class BlocksListCreateDestroyView(
        views.CoreListAPIView,
        views.CoreCreateAPIView,
        views.CoreListDestroyAPIView,
        BaseFloorListGetQuerySet):

    """
    Defines the blocks list-create-destroy view.
    """

    queryset = Block.objects.none()
    permission_classes = (OrganizationDjangoModelPermissions,)
    ordering_fields = ['id', 'name']
    filterset_fields = {
        'name': ['exact', 'icontains'],
    }
    order_by = 'name'
    list_serializer = BlockListSerializer
    create_serializer = BlockCreateSerializer


class BlocksRetrieveUpdateDestroyView(
        views.CoreRetrieveAPIView,
        views.CoreUpdateAPIView,
        views.CoreDestroyAPIView,
        BaseFloorRetrieveGetQuerySet):
    """
    Defines the blocks list-create-destroy view.
    """

    queryset = Block.objects.none()  # Added for model permissions
    permission_classes = (OrganizationDjangoModelPermissions,)
    retrieve_serializer = BlockRetrieveSerializer
    update_serializer = BlockUpdateSerializer
