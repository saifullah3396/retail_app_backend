
"""
Defines the REST API views for cameras models.
"""

from rest_framework import exceptions

from cameras.api.serializers import (CameraCreateSerializer,
                                     CameraDetailSerializer,
                                     CameraListSerializer,
                                     CameraUpdateSerializer)
from cameras.api.utils import filter_cameras_with_locations
from cameras.models import Camera
from cameras.permissions import (CamerasListCreateDestroyPermission,
                                 CamerasRetrieveUpdateDestroyPermission)
from core.permissions import UserGroups
from core.utils import (field_invalid_error, get_employee_authorized_locations,
                        get_object_by_id,
                        get_organization_admin_authorized_locations)
from core.views import CoreListCreateDestroyView, CoreRetrieveUpdateDestroyView
from locations.models import Block


class CamerasListCreateDestroyView(CoreListCreateDestroyView):
    """
    Defines the list-create-destroy view for Cameras.
    """

    queryset = Camera.objects.none()
    permission_classes = (CamerasListCreateDestroyPermission,)
    ordering_fields = ['id', 'ip_addr', 'block']
    filterset_fields = {
        'ip_addr': ['exact', 'icontains'],
        'block__id': ['exact'],
    }

    def _order_by(self):
        """
        Returns the field with respect to which queries are to be ordered.
        """
        return 'ip_addr'

    def _get_list_serializer_class(self):
        """
        Returns the list serializer.
        """
        return CameraListSerializer

    def _get_create_serializer_class(self):
        """
        Returns the create serializer.
        """
        return CameraCreateSerializer

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
        Return all cameras in authorized locations.
        """

        locations = get_organization_admin_authorized_locations(request.user)
        return filter_cameras_with_locations(request, locations)

    def _get_employee_queryset(self, request):
        """
        Return all cameras in authorized locations.
        """

        locations = get_employee_authorized_locations(request.user)
        return filter_cameras_with_locations(request, locations)

    def _perform_create_by_organization_admin(self, serializer):
        """
        Create camera if information is valid and within authorization.
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
                    'location': field_invalid_error()
                })

        # create camera in db
        serializer.save()


class CamerasRetrieveUpdateDestroyView(CoreRetrieveUpdateDestroyView):
    """
    Defines the retrieve-update-destroy view for cameras.
    """

    queryset = Camera.objects.none()  # Added for model permissions
    permission_classes = (CamerasRetrieveUpdateDestroyPermission,)

    def _get_detail_serializer_class(self):
        """
        Returns the detail serializer.
        """
        return CameraDetailSerializer

    def _get_update_serializer_class(self):
        """
        Returns the update serializer.
        """
        return CameraUpdateSerializer

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
        Return all cameras within authorized locations.
        """

        locations = get_organization_admin_authorized_locations(
            self.request.user)
        return filter_cameras_with_locations(request, locations)

    def _get_employee_queryset(self, request):
        """
        Return all cameras within authorized locations.
        """

        locations = get_employee_authorized_locations(request.user)
        return filter_cameras_with_locations(request, locations)

    def _perform_update_by_organization_admin(self, serializer):
        """
        Update if information is valid and within authorization.
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
