"""
Defines the REST API views for floors models.
"""

from rest_framework import exceptions

from core.permissions import UserGroups
from core.utils import (field_invalid_error, get_employee_authorized_locations,
                        get_organization_admin_authorized_locations)
from core.views import CoreListCreateDestroyView, CoreRetrieveUpdateDestroyView
from locations.api.serializers import (FloorCreateSerializer,
                                       FloorDetailSerializer,
                                       FloorListSerializer,
                                       FloorUpdateSerializer)
from locations.api.utils import filter_floors_with_locations
from locations.models import Floor, Location
from locations.permissions import (FloorsListCreateDestroyPermission,
                                   FloorsRetrieveUpdateDestroyPermission)


class FloorsListCreateDestroyView(CoreListCreateDestroyView):
    """
    Defines the list-create-destroy view for Floor.
    """

    queryset = Floor.objects.none()  # Added for model permissions
    permission_classes = (FloorsListCreateDestroyPermission,)
    ordering_fields = ['id', 'number']
    filterset_fields = {
        'number': ['exact'],
    }

    def _order_by(self):
        """
        Returns the field with respect to which queries are to be ordered.
        """
        return 'number'

    def _get_list_serializer_class(self):
        """
        Returns the list serializer.
        """
        return FloorListSerializer

    def _get_create_serializer_class(self):
        """
        Returns the create serializer.
        """
        return FloorCreateSerializer

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
        For organization admin, all floors are returned as long as the
        floor location is authorized to the user.
        """

        locations = get_organization_admin_authorized_locations(request.user)
        return filter_floors_with_locations(request, locations)

    def _get_employee_queryset(self, request):
        """
        For employees, all floors are returned within the queried
        location as long as the location is within authorized_locations for the
        employee.
        """

        # get all locations authorized to user
        locations = get_employee_authorized_locations(request.user)
        return filter_floors_with_locations(request, locations)

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


class FloorsRetrieveUpdateDestroyView(CoreRetrieveUpdateDestroyView):
    """
    Defines the retrieve-update-destroy view for floors.
    """

    queryset = Floor.objects.none()  # Added for model permissions
    permission_classes = (FloorsRetrieveUpdateDestroyPermission,)

    def _get_detail_serializer_class(self):
        """
        Returns the detail serializer.
        """
        return FloorDetailSerializer

    def _get_update_serializer_class(self):
        """
        Returns the update serializer.
        """
        return FloorUpdateSerializer

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
            'update': {}
        }

    def _get_organization_admin_queryset(self, request):
        """
        For organization admin, all floors are returned as long as the
        floor location is authorized to the user.
        """

        locations = get_organization_admin_authorized_locations(
            request.user)
        return filter_floors_with_locations(request, locations)

    def _get_employee_queryset(self, request):
        """
        For employees, all floors are returned within the queried
        location as long as the location is within authorized_locations for the
        employee.
        """

        locations = get_employee_authorized_locations(request.user)
        return filter_floors_with_locations(request, locations)

    def perform_destroy(self, instance):
        """
        Implements the customized destroy functionalty for a floor
        """
        # get all floors in this floor's location
        floors = Floor.objects.filter(
            location=instance.location).order_by('number')
        if instance.number != floors.last().number:
            raise exceptions.ValidationError(
                "Cannot be deleted. Higher floors depend on this floor.")

        # pylint: disable=no-member
        super().perform_destroy(instance)
