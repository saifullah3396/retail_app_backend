
"""
Defines the REST API views for cameras models.
"""

from rest_framework import exceptions

from cameras.api.serializers import (CameraDetailSerializer,
                                     CameraListSerializer)
from cameras.models import Camera
from cameras.permissions import (CamerasListCreateDestroyPermission,
                                 CamerasRetrieveUpdateDestroyPermission)
from core.permissions import UserGroups
from core.utils import (field_invalid_error, get_object_by_id,
                        get_user_authorized_locations)
from core.views import CoreListCreateDestroyView, CoreRetrieveUpdateDestroyView
from locations.models import Block


class CamerasView:
    """
    Defines the base interface class for the cameras rest api views.
    """
    # pylint: disable=no-member

    ordering_fields = ['ip_addr']
    filterset_fields = {
        'ip_addr': ['exact', 'icontains'],
        'block__id': ['exact'],
    }

    def _get_model(self):
        """
        Returns the view model.
        """

        return Camera

    def _order_by(self):
        """
        Returns the field with respect to which queries are to be ordered.
        """
        return 'ip_addr'

    def _filter_cameras_with_locations(self, locations):
        """
        Returns all the cameras in the given locations set
        """

        # get all blocks in requested floor
        cameras_in_locations = \
            self._get_model().objects.filter(
                block__floor__location__in=locations)

        # filter with ids if present
        id_list = self._get_id_list()
        if id_list:
            return self._filter_objects_by_id_list(
                cameras_in_locations, id_list)

        return cameras_in_locations


class CamerasListCreateDestroyView(
        CoreListCreateDestroyView, CamerasView):
    """
    Defines the list-create-destroy view for Cameras.
    """

    queryset = Camera.objects.none()
    serializer_class = CameraListSerializer
    permission_classes = (CamerasListCreateDestroyPermission,)

    def _get_model(self):
        """
        Returns the view model.
        """

        return CamerasView._get_model(self)

    def _order_by(self):
        """
        Returns the field with respect to which queries are to be ordered.
        """
        return CamerasView._order_by(self)

    def _define_get_queryset_by_group_fn(self):
        """
        Returns a dictionary mapping user group to get_queryset function
        that will be called if the request user is in that user group.
        """
        return {
            UserGroups.ORGANIZATION_ADMIN_GROUP:
                self._get_organization_admin_queryset,
            UserGroups.EMPLOYEE_GROUP:
                self._get_employee_queryset,
        }

    def _define_perform_create_by_group_fn(self):
        """
        Returns a dictionary mapping user group to perform_create function
        that will be called if the request user is in that user group.
        """
        return {
            UserGroups.ORGANIZATION_ADMIN_GROUP:
                self._perform_create_by_organization_admin
        }

    def _get_organization_admin_queryset(self):
        """
        For organization admin, all blocks are returned within the queried
        floor/location as long as the location is authorized.
        """

        locations = get_user_authorized_locations(self.response.user)
        return self._filter_cameras_with_locations(locations)

    def _get_employee_queryset(self):
        """
        For employee, all blocks are returned within the queried
        floor/location as long as the location is authorized.
        """

        locations = get_user_authorized_locations(self.response.user)
        return self._filter_cameras_with_locations(locations)

    def _perform_create_by_organization_admin(self, serializer):
        """
        For organization admin, the block is created within the queried
        floor/location as long as the location is authorized.
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
        locations = get_user_authorized_locations(self.response.user)
        if not locations.filter(id=block.floor.location.id).exists():
            raise exceptions.ValidationError(
                {
                    'location': field_invalid_error()
                })

        # create floor in db
        serializer.save()


class CamerasRetrieveUpdateDestroyView(
        CoreRetrieveUpdateDestroyView, CamerasView):
    """
    Defines the retrieve-update-destroy view for blocks.
    """

    queryset = Camera.objects.none()  # Added for model permissions
    serializer_class = CameraDetailSerializer
    permission_classes = (CamerasRetrieveUpdateDestroyPermission,)

    def _get_model(self):
        """
        Returns the view model.
        """

        return CamerasView._get_model(self)

    def _define_get_queryset_by_group_fn(self):
        """
        Returns a dictionary mapping user group to get_queryset function
        that will be called if the request user is in that user group.
        """
        return {
            UserGroups.ORGANIZATION_ADMIN_GROUP:
                self._get_organization_admin_queryset,
            UserGroups.EMPLOYEE_GROUP:
                self._get_employee_queryset,
        }

    def _define_perform_update_by_group_fn(self):
        """
        Returns a dictionary mapping user group to perform_update function
        that will be called if the request user is in that user group.
        """
        return {
            UserGroups.ORGANIZATION_ADMIN_GROUP:
                self._perform_update_by_organization_admin
        }

    def _get_organization_admin_queryset(self):
        """
        For organization admin, all blocks are returned within the queried
        floor/location as long as the location is authorized.
        """

        locations = get_user_authorized_locations(self.response.user)
        return self._filter_cameras_with_locations(locations)

    def _get_employee_queryset(self):
        """
        For employee, all blocks are returned within the queried
        floor/location as long as the location is authorized.
        """

        locations = get_user_authorized_locations(self.response.user)
        return self._filter_cameras_with_locations(locations)

    def _perform_update_by_organization_admin(self, serializer):
        """
        For organization admin, the block is updated as long as it is within
        the get queryset
        """
        serializer.save()
