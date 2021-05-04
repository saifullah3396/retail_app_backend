
"""
Defines the REST API views for locations models.
"""

from rest_framework import exceptions

from core.permissions import UserGroups
from core.utils import (field_invalid_error, get_employee_authorized_locations,
                        get_organization_admin_authorized_locations)
from core.views import CoreListCreateDestroyView, CoreRetrieveUpdateDestroyView
from locations.api.serializers import (LocationCreateSerializer,
                                       LocationDetailSerializer,
                                       LocationListSerializer,
                                       LocationUpdateSerializer)
from locations.api.utils import filter_locations
from locations.models import Location
from locations.permissions import (LocationsListCreateDestroyPermission,
                                   LocationsRetrieveUpdateDestroyPermission)


class LocationsListCreateDestroyView(CoreListCreateDestroyView):
    """
    Defines the locations list-create-destroy view.
    """

    queryset = Location.objects.none()  # Added for model permissions
    permission_classes = (LocationsListCreateDestroyPermission,)
    ordering_fields = ['id', 'name']
    filterset_fields = {
        'name': ['exact', 'icontains'],
        'organization__id': ['exact']
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
        return LocationListSerializer

    def _get_create_serializer_class(self):
        """
        Returns the create serializer.
        """
        return LocationCreateSerializer

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
        For an organization admin, locations in all the organizations below
        the user organization are returned. In case a list of ids is provided,
        the locations are filtered further by ids.
        """

        locations = get_organization_admin_authorized_locations(request.user)
        return filter_locations(request, locations)

    def _get_employee_queryset(self, request):
        """
        For an employee, only authorized_locations are returned. If ids are
        provided, locations are further filtered by the them.
        """
        locations = get_employee_authorized_locations(request.user)
        return filter_locations(request, locations)

    def _perform_create_by_organization_admin(self, serializer):
        """
        Creates a new location as long as the organization related to location
        is within descendents of this admin's organization
        """

        # see if the organization of requested location is within
        # descendents of this admin
        descendents = self.request.user.organization.get_descendants(
            include_self=True)
        if not descendents.filter(id=self.request.data['organization']):
            raise exceptions.ValidationError(
                {
                    'organization': field_invalid_error()
                })

        # create organization in db
        serializer.save()


class LocationsRetrieveUpdateDestroyView(CoreRetrieveUpdateDestroyView):
    """
    Defines the locations retrieve-update-destroy view.
    """

    queryset = Location.objects.none()  # Added for model permissions
    permission_classes = (LocationsRetrieveUpdateDestroyPermission,)

    def _get_detail_serializer_class(self):
        """
        Returns the detail serializer.
        """
        return LocationDetailSerializer

    def _get_update_serializer_class(self):
        """
        Returns the update serializer.
        """
        return LocationUpdateSerializer

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
        Returns the get_queryset for organization admin user group
        """
        organizations_tree = request.user.organization.get_descendants(
            include_self=True)
        return self._model.objects.filter(
            organization__in=organizations_tree)

    def _get_employee_queryset(self, request):
        """
        Returns the get_queryset for employee user group
        """
        return request.user.authorized_locations.all()

    def _perform_update_by_organization_admin(self, serializer):
        """
        For organization admin, the location is updated as long as it is within
        the get queryset
        """

        if 'organization' in self.request.data:
            # see if new requested organization is within users organization
            # tree
            descendents = self.request.user.organization.get_descendants(
                include_self=True)
            if not descendents.filter(
                    id=self.request.data.get('organization', None)):
                raise exceptions.ValidationError(
                    {
                        'organization': field_invalid_error()
                    })

        serializer.save()
