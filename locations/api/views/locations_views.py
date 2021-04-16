
"""
Defines the REST API views for locations models.
"""

from rest_framework import exceptions

from core.permissions import UserGroups
from core.utils import (field_invalid_error, get_employee_authorized_locations,
                        get_organization_admin_authorized_locations)
from core.views import CoreListCreateDestroyView, CoreRetrieveUpdateDestroyView
from locations.api.serializers import (LocationDetailSerializer,
                                       LocationListSerializer)
from locations.models import Location
from locations.permissions import (LocationsListCreateDestroyPermission,
                                   LocationsRetrieveUpdateDestroyPermission)


class LocationsView:
    """
    Defines the base interface class for the locations rest api views.
    """
    # pylint: disable=no-member

    ordering_fields = ['id', 'name']
    filterset_fields = {
        'name': ['exact', 'icontains'],
        'organization__id': ['exact']
    }

    def _get_model(self):
        """
        Returns the view model.
        """

        return Location

    def _order_by(self):
        """
        Returns the default ordering field.
        """
        return 'name'

    def _filter_locations(self, locations):
        """
        Filter input locations by id list.
        """
        id_list = self._get_id_list()
        if id_list:
            return self._filter_objects_by_id_list(
                locations, id_list)

        return locations


class LocationsListCreateDestroyView(
        CoreListCreateDestroyView, LocationsView):
    """
    Defines the locations list-create-destroy view.
    """

    queryset = Location.objects.none()  # Added for model permissions
    serializer_class = LocationListSerializer
    permission_classes = (LocationsListCreateDestroyPermission,)

    def _get_model(self):
        """
        Returns the model for this view
        """

        return LocationsView._get_model(self)

    def _order_by(self):
        """
        Returns the field with respect to which queries are to be ordered.
        """
        return LocationsView._order_by(self)

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
        For an organization admin, locations in all the organizations below
        the user organization are returned. In case a list of ids is provided,
        the locations are filtered further by ids.
        """

        locations = get_organization_admin_authorized_locations(
            self.request.user)
        return self._filter_locations(locations)

    def _get_employee_queryset(self):
        """
        For an employee, only authorized_locations are returned. If ids are
        provided, locations are further filtered by the them.
        """
        locations = get_employee_authorized_locations(self.request.user)
        return self._filter_locations(locations)

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


class LocationsRetrieveUpdateDestroyView(
        CoreRetrieveUpdateDestroyView, LocationsView):
    """
    Defines the locations retrieve-update-destroy view.
    """

    queryset = Location.objects.none()  # Added for model permissions
    serializer_class = LocationDetailSerializer
    permission_classes = (LocationsRetrieveUpdateDestroyPermission,)

    def _get_model(self):
        """
        Returns the model for this view
        """

        return LocationsView._get_model(self)

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
        organizations_tree = self.request.user.organization.get_descendants(
            include_self=True)
        return self._get_model().objects.filter(
            organization__in=organizations_tree)

    def _get_employee_queryset(self):
        """
        Returns the get_queryset for employee user group
        """
        return self.request.user.authorized_locations.all()

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
