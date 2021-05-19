
"""
Defines the REST API views for locations models.
"""

from rest_framework import exceptions

from core import views
from core.permissions import AppDjangoModelPermissions
from locations.api.serializers import (LocationCreateSerializer,
                                       LocationDetailSerializer,
                                       LocationListSerializer,
                                       LocationUpdateSerializer)
from locations.models import OrganizationLocation, UserLocation
from app_organizations.permissions import OrganizationDjangoModelPermissions
from app_organizations.views import (BaseOrganizationListGetQuerySet,
                                     BaseOrganizationRetrieveGetQuerySet)


class UserLocationsListCreateDestroyView(
        views.CoreListAPIView,
        views.CoreCreateAPIView,
        views.CoreListDestroyAPIView):

    """
    Defines the user locations list-create-destroy view.
    """

    queryset = UserLocation.objects.none()
    permission_classes = (AppDjangoModelPermissions,)
    # list destroy is not allowed
    ordering_fields = ['id', 'name']
    filterset_fields = {
        'name': ['exact', 'icontains'],
    }
    order_by = 'name'
    list_serializer = LocationListSerializer
    create_serializer = LocationCreateSerializer

    def _get_list_queryset(self):
        return self.model.objects.filter(user=self.request.user)


class UserLocationsRetrieveUpdateDestroyView(
        views.CoreRetrieveAPIView,
        views.CoreUpdateAPIView,
        views.CoreDestroyAPIView):
    """
    Defines the user locations retrieve-update-destroy view.
    """
    queryset = UserLocation.objects.none()  # Added for model permissions
    permission_classes = (AppDjangoModelPermissions,)
    retrieve_serializer = LocationDetailSerializer
    update_serializer = LocationUpdateSerializer

    def _get_retrieve_queryset(self):
        return self.model.objects.filter(user=self.request.user)


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
    retrieve_serializer = LocationDetailSerializer
    update_serializer = LocationUpdateSerializer

    def _get_retrieve_queryset(self):
        return self.model.objects.filter(user=self.request.user)
