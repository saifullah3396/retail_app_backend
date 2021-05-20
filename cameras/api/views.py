
"""
Defines the REST API views for cameras models.
"""


from app_organizations.permissions import OrganizationDjangoModelPermissions
from cameras.api.serializers import (CameraCreateSerializer,
                                     CameraListSerializer,
                                     CameraRetrieveSerializer,
                                     CameraUpdateSerializer)
from cameras.models import Camera
from core import views
from locations.views import (BaseBlockListGetQuerySet,
                             BaseBlockRetrieveGetQuerySet)


class CamerasListCreateDestroyView(
        views.CoreListAPIView,
        views.CoreCreateAPIView,
        views.CoreListDestroyAPIView,
        BaseBlockListGetQuerySet):

    """
    Defines the Cameras list-create-destroy view.
    """

    queryset = Camera.objects.none()
    permission_classes = (OrganizationDjangoModelPermissions,)
    ordering_fields = ['id', 'ip_addr']
    filterset_fields = {
        'ip_addr': ['exact', 'icontains']
    }
    order_by = 'ip_addr'
    list_serializer = CameraListSerializer
    create_serializer = CameraCreateSerializer


class CamerasRetrieveUpdateDestroyView(
        views.CoreRetrieveAPIView,
        views.CoreUpdateAPIView,
        views.CoreDestroyAPIView,
        BaseBlockRetrieveGetQuerySet):
    """
    Defines the Cameras list-create-destroy view.
    """

    queryset = Camera.objects.none()  # Added for model permissions
    permission_classes = (OrganizationDjangoModelPermissions,)
    retrieve_serializer = CameraRetrieveSerializer
    update_serializer = CameraUpdateSerializer
