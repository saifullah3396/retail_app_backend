
"""
Defines the REST API views for measurement frames models.
"""


from app_organizations.permissions import OrganizationDjangoModelPermissions
from core import views
from locations.views import (BaseBlockListGetQuerySet,
                             BaseBlockRetrieveGetQuerySet)
from measurement_frames.api.serializers import (
    MeasurementFrameCreateSerializer, MeasurementFrameListSerializer,
    MeasurementFrameRetrieveSerializer, MeasurementFrameUpdateSerializer)
from measurement_frames.models import MeasurementFrame


class MeasurementFramesListCreateDestroyView(
        views.CoreListAPIView,
        views.CoreCreateAPIView,
        views.CoreListDestroyAPIView,
        BaseBlockListGetQuerySet):

    """
    Defines the MeasurementFrames list-create-destroy view.
    """

    queryset = MeasurementFrame.objects.none()
    permission_classes = (OrganizationDjangoModelPermissions,)
    ordering_fields = ['id', 'name']
    filterset_fields = {
        'name': ['exact', 'icontains'],
    }
    order_by = 'name'
    list_serializer = MeasurementFrameListSerializer
    create_serializer = MeasurementFrameCreateSerializer


class MeasurementFramesRetrieveUpdateDestroyView(
        views.CoreRetrieveAPIView,
        views.CoreUpdateAPIView,
        views.CoreDestroyAPIView,
        BaseBlockRetrieveGetQuerySet):
    """
    Defines the MeasurementFrames list-create-destroy view.
    """

    queryset = MeasurementFrame.objects.none()  # Added for model permissions
    permission_classes = (OrganizationDjangoModelPermissions,)
    retrieve_serializer = MeasurementFrameRetrieveSerializer
    update_serializer = MeasurementFrameUpdateSerializer
