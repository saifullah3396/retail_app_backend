# pylint: disable=missing-module-docstring

from rest_framework import exceptions

from cameras.models import Camera
from cameras.permissions import (CamerasListCreateDestroyPermission,
                                 CamerasRetrieveUpdateDestroyPermission)
from cameras.serializers import CameraSerializer
from core.permissions import UserGroups
from core.views import CoreListCreateDestroyView, CoreRetrieveUpdateDestroyView
from locations.models import Block
from locations.utils import (get_cameras_for_employee,
                             get_cameras_for_organization_admin,
                             get_locations_for_organization_admin)


# pylint: disable=missing-class-docstring
class CameraView:
    ordering_fields = ['id']
    filterset_fields = {
        'id': ['exact'],
        'block__id': ['exact'],
    }

    def _get_model(self):
        return Camera

    def _order_by(self):
        return 'id'


class CamerasListCreateDestroyView(CoreListCreateDestroyView, CameraView):

    queryset = Camera.objects.none()
    serializer_class = CameraSerializer
    permission_classes = (CamerasListCreateDestroyPermission,)

    def _get_model(self):

        return CameraView._get_model(self)

    def _define_get_queryset_by_group_fn(self):

        return {
            UserGroups.ORGANIZATION_ADMIN_GROUP:
                self._get_organizations_admin_queryset,
            UserGroups.EMPLOYEE_GROUP:
                self._get_employee_queryset,
        }

    def _perform_create_by_organization_admin(self, serializer):
        try:
            block = Block.objects.get(self.request.data['block'])
        except Block.DoesNotExist as exc:
            raise exceptions.ValidationError(
                {
                    'block': 'Block not found'
                }) from exc
        locations = get_locations_for_organization_admin(
            self.user, include_self=True)

        if not locations.filter(id=block.floor.location.id):
            raise exceptions.ValidationError(
                {
                    'block': 'User is not authorised'
                })

        serializer.save()

    def _get_organizations_admin_queryset(self):
        cameras = get_cameras_for_organization_admin(
            self.request.user)

        id_list = self._get_id_list()
        if id_list:
            return self._filter_objects_by_id_list(
                cameras, id_list)

        return cameras

    def _get_employee_queryset(self):
        cameras = get_cameras_for_employee(
            self.request.user)
        id_list = self._get_id_list()
        if id_list:
            return self._filter_objects_by_id_list(
                cameras, id_list)
        return cameras

    def _define_perform_create_by_group_fn(self):

        return {
            UserGroups.ORGANIZATION_ADMIN_GROUP:
            self._perform_create_by_organization_admin
        }

    def _order_by(self):

        return CameraView._order_by(self)


class CamerasRetrieveUpdateDestroyView(
        CoreRetrieveUpdateDestroyView, CameraView):
    """
    Defines the cameras retrieve-update-destroy view.
    """

    queryset = Camera.objects.none()  # Added for model permissions
    serializer_class = CameraSerializer
    permission_classes = (CamerasRetrieveUpdateDestroyPermission,)

    def _get_model(self):
        """
        Returns the model for this view
        """

        return CameraView._get_model(self)

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
        Returns the get_queryset for organization admin user group
        """
        return get_cameras_for_organization_admin(
            self.request.user)

    def _get_employee_queryset(self):
        """
        Returns the get_queryset for employee user group
        """
        return get_cameras_for_employee(
            self.request.user)

    def _perform_update_by_organization_admin(self, serializer):
        serializer.save()
