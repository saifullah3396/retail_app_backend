from core.utils import *
from core.views import *
from django.contrib.auth.models import Group
from django_filters.rest_framework import DjangoFilterBackend
from locations.api.serializers import *
from locations.models import MeasurementFrame
from locations.permissions import *
from locations.utils import *
from rest_framework import *
from rest_framework import filters, pagination
from rest_framework.generics import *
from rest_framework.response import Response
from rest_framework_jwt import authentication


class MeasurementFrameView:
    ordering_fields = ['name']
    filterset_fields = {
        'name':  ['exact'],
    }

    def _get_model(self):
        """
        Returns the get queryset for staff users.
        """

        return Location

    def _order_by(self):
        """
        Returns the field with respect to which queries are to be ordered.
        """
        return 'name'

class MeasurementFrameListCreateDestroyView(CoreListCreateDestroyView, MeasurementFrameView):

    queryset = MeasurementFrame.objects.none()
    serializer_class = MeasurementFrameSerializer
    permission_classes = (MeasurementFrameListCreateDestroyPermission,)

    def _get_model(self):

        return MeasurementFrameView._get_model(self)

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
        except Exception as exceptions:
            raise exceptions.ValidationError(
                {
                    'block': 'Block not found'
                })
        locations = get_locations_for_organization_admin(
            self.user, include_self=true)

        if not locations.filter(id=block.floor.location.id):
            raise exceptions.ValidationError(
                {
                    'block': 'User is not authorised'
                })

        serializer.save()

    def _get_organizations_admin_queryset(self):
        measurementframes = get_measurement_frame_for_organization_admin(
            self.request.user)

        id_list = self._get_id_list()
        if id_list:
            return self._filter_objects_by_id_list(
                measurementframes, id_list)

        return measurementframes

    def _get_employee_queryset(self):
        measurementframes = get_measurement_frame_for_employee(
            self.request.user)
        id_list = self._get_id_list()
        if id_list:
            return self._filter_objects_by_id_list(
                measurementframes, id_list)
        return measurementframes

    def _define_perform_create_by_group_fn(self):

        return {
            UserGroups.ORGANIZATION_ADMIN_GROUP:
            self._perform_create_by_organization_admin
        }

    def _order_by(self):

        return MeasurementFrameView._order_by(self)

class MeasurementFrameRetrieveUpdateDestroyView(
        CoreRetrieveUpdateDestroyView, MeasurementFrameView):
    """
    Defines the cameras retrieve-update-destroy view.
    """

    queryset = MeasurementFrame.objects.none()  # Added for model permissions
    serializer_class = MeasurementFrameSerializer
    permission_classes = (MeasurementFrameRetrieveUpdateDestroyPermission,)

    def _get_model(self):
        """
        Returns the model for this view
        """
        return MeasurementFrameView._get_model(self)

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
        return get_measurement_frame_for_organization_admin(
            self.request.user)

    def _get_employee_queryset(self):
        """
        Returns the get_queryset for employee user group
        """
        return get_measurement_frame_for_employee(
            self.request.user)

    def _perform_update_by_organization_admin(self, serializer):
        serializer.save()
