"""
Defines the REST API views for floors models.
"""

from rest_framework import exceptions

from core.permissions import UserGroups
from core.utils import (field_invalid_error, get_employee_authorized_locations,
                        get_organization_admin_authorized_locations)
from core.views import CoreListCreateDestroyView, CoreRetrieveUpdateDestroyView
from locations.api.serializers import (FloorDetailSerializer,
                                       FloorListSerializer)
from locations.models import Floor, Location
from locations.permissions import (FloorsListCreateDestroyPermission,
                                   FloorsRetrieveUpdateDestroyPermission)


class FloorsView:
    """
    Defines the base interface class for the floors rest api views.
    """
    # pylint: disable=no-member

    ordering_fields = ['id', 'number']
    filterset_fields = {
        'number': ['exact'],
    }

    def _get_model(self):
        """
        Returns the view model.
        """

        return Floor

    def _order_by(self):
        """
        Returns the field with respect to which queries are to be ordered.
        """
        return 'number'

    def _filter_floors_with_locations(self, locations):
        # get all floors of the requested location
        floors_in_location = \
            self._get_model().objects.filter(location__in=locations)

        # filter with ids if present
        id_list = self._get_id_list()
        if id_list:
            return self._filter_objects_by_id_list(
                floors_in_location, id_list)

        return floors_in_location


class FloorsListCreateDestroyView(CoreListCreateDestroyView, FloorsView):
    """
    Defines the list-create-destroy view for Floor.
    """

    queryset = Floor.objects.none()  # Added for model permissions
    serializer_class = FloorListSerializer
    permission_classes = (FloorsListCreateDestroyPermission,)

    def _get_model(self):
        """
        Returns the model of this view
        """

        return FloorsView._get_model(self)

    def _order_by(self):
        """
        Returns the field with respect to which queries are to be ordered.
        """
        return FloorsView._order_by(self)

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
        For organization admin, all floors are returned as long as the
        floor location is authorized to the user.
        """

        locations = get_organization_admin_authorized_locations(
            self.request.user)
        return self._filter_floors_with_locations(locations)

    def _get_employee_queryset(self):
        """
        For employees, all floors are returned within the queried
        location as long as the location is within authorized_locations for the
        employee.
        """

        # get all locations authorized to user
        locations = get_employee_authorized_locations(self.request.user)
        return self._filter_floors_with_locations(locations)

    def _perform_create_by_organization_admin(self, serializer):
        """
        For organization admin, the floor is created as long as the
        floor location is authorized to the user.
        """

        # get all locations authorized to user
        locations = \
            get_organization_admin_authorized_locations(self.request.user)
        if not locations.filter(id=self.request.data.get('location', None)):
            raise exceptions.ValidationError(
                {
                    'location': field_invalid_error()
                })

        # create floor in db
        serializer.save()

    def delete(self, request, *args, **kwargs):
        """Removes the ability to delete floors by a list of ids."""
        raise exceptions.PermissionDenied()


class FloorsRetrieveUpdateDestroyView(
        CoreRetrieveUpdateDestroyView, FloorsView):
    """
    Defines the retrieve-update-destroy view for floors.
    """

    queryset = Location.objects.none()  # Added for model permissions
    serializer_class = FloorDetailSerializer
    permission_classes = (FloorsRetrieveUpdateDestroyPermission,)

    def _get_model(self):
        """
        Returns the model of this view
        """

        return FloorsView._get_model(self)

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
        return {}

    def _get_organization_admin_queryset(self):
        """
        For organization admin, all floors are returned as long as the
        floor location is authorized to the user.
        """

        locations = get_organization_admin_authorized_locations(
            self.request.user)
        return self._filter_floors_with_locations(locations)

    def _get_employee_queryset(self):
        """
        For employees, all floors are returned within the queried
        location as long as the location is within authorized_locations for the
        employee.
        """

        locations = get_employee_authorized_locations(self.request.user)
        return self._filter_floors_with_locations(locations)

    def perform_destroy(self, instance):
        """
        Implements the customized destroy functionalty for a floor
        """
        # get all floors in this floor's location
        floors = Floor.objects.filter(location=instance.location).order_by('number')
        if instance.number != floors.last().number:
            raise exceptions.ValidationError(
                "Cannot be deleted. Higher floors depend on this floor.")

        # pylint: disable=no-member
        super().perform_destroy(instance)

    def put(self, request, *args, **kwargs):
        """
        Removes functionality to call PUT on a floor
        """
        raise exceptions.PermissionDenied()

    def patch(self, request, *args, **kwargs):
        """
        Removes functionality to call PATCH on a floor
        """
        raise exceptions.PermissionDenied()