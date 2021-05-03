
"""
Defines the REST API views for measurement frames models.
"""

from rest_framework import exceptions

from core.permissions import UserGroups
from core.utils import (field_invalid_error, get_employee_authorized_locations,
                        get_object_by_id,
                        get_organization_admin_authorized_locations)
from core.views import CoreListCreateDestroyView, CoreRetrieveUpdateDestroyView
from locations.models import Block
from measurement_frames.api.serializers import (
    MeasurementFrameCreateSerializer, MeasurementFrameDetailSerializer,
    MeasurementFrameListSerializer, MeasurementFrameUpdateSerializer)
from measurement_frames.api.utils import filter_frames_with_locations
from measurement_frames.models import MeasurementFrame
from measurement_frames.permissions import (
    MeasurementFramesListCreateDestroyPermission,
    MeasurementFramesRetrieveUpdateDestroyPermission)


class MeasurementFramesListCreateDestroyView(CoreListCreateDestroyView):
    """
    Defines the list-create-destroy view for MeasurementFrames.
    """

    queryset = MeasurementFrame.objects.none()
    permission_classes = (MeasurementFramesListCreateDestroyPermission,)
    ordering_fields = ['name']
    filterset_fields = {
        'name': ['exact', 'icontains'],
    }

    def _order_by(self):
        """
        Returns the field with respect to which queries are to be ordered.
        """
        return 'name'

    def _get_list_serializer_class(self):
        """
        Returns the list serializer.
        """
        return MeasurementFrameListSerializer

    def _get_create_serializer_class(self):
        """
        Returns the create serializer.
        """
        return MeasurementFrameCreateSerializer

    def _define_api_handler_by_group(self):
        """
        Returns a dictionary mapping user group to rest api handler functions
        that will be called if the request user is in that user group.
        """
        api_handler_by_group = super()._define_api_handler_by_group()
        return {
            'get': {
                **api_handler_by_group['get'],
                UserGroups.ORGANIZATION_ADMIN_GROUP:
                    self._get_organization_admin_queryset,
                UserGroups.EMPLOYEE_GROUP:
                    self._get_employee_queryset,
            },
            'create': {
                **api_handler_by_group['create'],
                UserGroups.ORGANIZATION_ADMIN_GROUP:
                    self._perform_create_by_organization_admin
            }
        }

    def _get_organization_admin_queryset(self, request):
        """
        Returns all frames within user authorized locations.
        """

        locations = get_organization_admin_authorized_locations(request.user)
        return filter_frames_with_locations(request, locations)

    def _get_employee_queryset(self, request):
        """
        Returns all frames within user authorized locations.
        """

        locations = get_employee_authorized_locations(request.user)
        return filter_frames_with_locations(request, locations)

    def _perform_create_by_organization_admin(self, serializer):
        """
        Creates a frame as long as its block is valid and is within
        user authorized locations.
        """

        # get block
        block = get_object_by_id(
            Block, self.request.data.get('block', None))

        if not block:
            raise exceptions.ValidationError(
                {
                    'block': field_invalid_error()
                })

        # see whether block location is within authorized locations
        locations = get_organization_admin_authorized_locations(
            self.request.user)
        if not locations.filter(id=block.floor.location.id).exists():
            raise exceptions.ValidationError(
                {
                    'block': field_invalid_error()
                })

        # create floor in db
        serializer.save()


class MeasurementFramesRetrieveUpdateDestroyView(CoreRetrieveUpdateDestroyView):
    """
    Defines the retrieve-update-destroy view for blocks.
    """

    queryset = MeasurementFrame.objects.none()  # Added for model permissions
    permission_classes = (MeasurementFramesRetrieveUpdateDestroyPermission,)

    def _get_detail_serializer_class(self):
        """
        Returns the detail serializer.
        """
        return MeasurementFrameDetailSerializer

    def _get_update_serializer_class(self):
        """
        Returns the update serializer.
        """
        return MeasurementFrameUpdateSerializer

    def _define_api_handler_by_group(self):
        """
        Returns a dictionary mapping user group to rest api handler functions
        that will be called if the request user is in that user group.
        """
        api_handler_by_group = super()._define_api_handler_by_group()
        return {
            'get': {
                **api_handler_by_group['get'],
                UserGroups.ORGANIZATION_ADMIN_GROUP:
                    self._get_organization_admin_queryset,
                UserGroups.EMPLOYEE_GROUP:
                    self._get_employee_queryset,
            },
            'update': {
                **api_handler_by_group['update'],
                UserGroups.ORGANIZATION_ADMIN_GROUP:
                    self._perform_update_by_organization_admin
            }
        }

    def _get_organization_admin_queryset(self, request):
        """
        Returns all frames are returned within the users
        authorized locations.
        """

        locations = get_organization_admin_authorized_locations(request.user)
        return filter_frames_with_locations(request, locations)

    def _get_employee_queryset(self, request):
        """
        Returns all frames are returned within the users
        authorized locations.
        """

        locations = get_employee_authorized_locations(request.user)
        return filter_frames_with_locations(request, locations)

    def _perform_update_by_organization_admin(self, serializer):
        """
        Updates the model based on validated data.
        """

        if 'block' in self.request.data:
            # get block
            block = get_object_by_id(
                Block, self.request.data.get('block', None))

            if not block:
                raise exceptions.ValidationError(
                    {
                        'block': field_invalid_error()
                    })

            # see whether block location is within authorized locations
            locations = get_organization_admin_authorized_locations(
                self.request.user)
            if not locations.filter(id=block.floor.location.id).exists():
                raise exceptions.ValidationError(
                    {
                        'block': field_invalid_error()
                    })

        serializer.save()
