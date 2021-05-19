
"""
Defines the REST API views for locations models.
"""


from core import views
from locations.models import OrganizationLocation
from app_organizations.permissions import OrganizationDjangoModelPermissions
from app_organizations.views import (BaseOrganizationListGetQuerySet,
                                     BaseOrganizationRetrieveGetQuerySet)

from .serializers import (LocationCreateSerializer, LocationListSerializer,
                          LocationRetrieveSerializer, LocationUpdateSerializer)


class OrganizationLocationsListCreateDestroyView(
        views.CoreListAPIView,
        views.CoreCreateAPIView,
        views.CoreListDestroyAPIView,
        BaseOrganizationListGetQuerySet):

    """
    Defines the organization locations list-create-destroy view.
    """

    queryset = OrganizationLocation.objects.none()
    permission_classes = (OrganizationDjangoModelPermissions,)
    # list destroy is not allowed
    ordering_fields = ['id', 'name']
    filterset_fields = {
        'name': ['exact', 'icontains'],
    }
    order_by = 'name'
    list_serializer = LocationListSerializer
    create_serializer = LocationCreateSerializer


class OrganizationLocationsRetrieveUpdateDestroyView(
        views.CoreRetrieveAPIView,
        views.CoreUpdateAPIView,
        views.CoreDestroyAPIView,
        BaseOrganizationRetrieveGetQuerySet):
    """
    Defines the organizations locations list-create-destroy view.
    """

    queryset = OrganizationLocation.objects.none()  # Added for model permissions
    permission_classes = (OrganizationDjangoModelPermissions,)
    retrieve_serializer = LocationRetrieveSerializer
    update_serializer = LocationUpdateSerializer
