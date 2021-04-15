
"""
Defines the REST API views for measurement frames models.
"""

from rest_framework import exceptions

from core.permissions import UserGroups
from core.utils import (field_invalid_error, get_object_by_id,
                        get_user_authorized_locations)
from core.views import CoreListCreateDestroyView, CoreRetrieveUpdateDestroyView
from locations.models import Block
from measurement_frames.api.serializers import (
    MeasurementFrameDetailSerializer, MeasurementFrameListSerializer)
from measurement_frames.models import MeasurementFrame
from measurement_frames.permissions import (
    MeasurementFramesListCreateDestroyPermission,
    MeasurementFramesRetrieveUpdateDestroyPermission)


class MeasurementFramesView:
    """
    Defines the base interface class for the floors rest api views.
    """
    # pylint: disable=no-member

    ordering_fields = ['name']
    filterset_fields = {
        'name': ['exact', 'icontains'],
    }

    def _get_model(self):
        """
        Returns the get queryset for staff users.
        """

        return MeasurementFrame

    def _order_by(self):
        """
        Returns the field with respect to which queries are to be ordered.
        """
        return 'name'

    def _filter_frames_with_locations(self, locations):
        """
        Returns all the frames in the given locations set
        """

        # get all blocks in requested floor
        frames_in_locations = \
            self._get_model().objects.filter(
                block__floor__location__in=locations)

        # filter with ids if present
        id_list = self._get_id_list()
        if id_list:
            return self._filter_objects_by_id_list(
                frames_in_locations, id_list)

        return frames_in_locations


class MeasurementFramesListCreateDestroyView(
        CoreListCreateDestroyView, MeasurementFramesView):
    """
    Defines the list-create-destroy view for MeasurementFrames.
    """

    queryset = MeasurementFrame.objects.none()
    serializer_class = MeasurementFrameListSerializer
    permission_classes = (MeasurementFramesListCreateDestroyPermission,)

    def _get_model(self):
        """
        Returns the get queryset for staff users.
        """

        return MeasurementFramesView._get_model(self)

    def _order_by(self):
        """
        Returns the field with respect to which queries are to be ordered.
        """
        return MeasurementFramesView._order_by(self)

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
        return self._filter_frames_with_locations(locations)

    def _get_employee_queryset(self):
        """
        For employee, all blocks are returned within the queried
        floor/location as long as the location is authorized.
        """

        locations = get_user_authorized_locations(self.response.user)
        return self._filter_frames_with_locations(locations)

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


class MeasurementFramesRetrieveUpdateDestroyView(
        CoreRetrieveUpdateDestroyView, MeasurementFramesView):
    """
    Defines the retrieve-update-destroy view for blocks.
    """

    queryset = MeasurementFrame.objects.none()  # Added for model permissions
    serializer_class = MeasurementFrameDetailSerializer
    permission_classes = (MeasurementFramesRetrieveUpdateDestroyPermission,)

    def _get_model(self):
        """
        Returns the get queryset for staff users.
        """

        return MeasurementFramesView._get_model(self)

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
        return self._filter_frames_with_locations(locations)

    def _get_employee_queryset(self):
        """
        For employee, all blocks are returned within the queried
        floor/location as long as the location is authorized.
        """

        locations = get_user_authorized_locations(self.response.user)
        return self._filter_frames_with_locations(locations)

    def _perform_update_by_organization_admin(self, serializer):
        """
        For organization admin, the block is updated as long as it is within
        the get queryset
        """
        serializer.save()
