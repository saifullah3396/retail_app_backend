
from django.contrib.auth.models import Group
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import *
from rest_framework import filters, pagination
from rest_framework.generics import *
from rest_framework.response import Response
from rest_framework_jwt import authentication

from core.utils import *
from core.views import *
from locations.api.serializers import *
from locations.models import Location
from locations.permissions import *
from locations.utils import *


class LocationsView:
    ordering_fields = ['id', 'name']
    filterset_fields = {
        'name': ['exact', 'icontains'],
        'organization__id': ['exact']
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

        locations = get_locations_for_organization_admin(
            self.request.user, include_self=True)

        id_list = self._get_id_list()
        if id_list:
            return self._filter_objects_by_id_list(
                locations, id_list)

        return locations

    def _get_employee_queryset(self):
        """
        For an employee, only authorized_locations are returned. If ids are
        provided, locations are further filtered by the them.
        """
        locations = get_locations_for_employee(
            self.request.user, include_self=True)
        id_list = self._get_id_list()
        if id_list:
            return self._filter_objects_by_id_list(
                locations, id_list)
        return locations

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
                    'organization': 'Invalid value.'
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
        return get_locations_for_organization_admin(
            self.request.user, include_self=True)

    def _get_employee_queryset(self):
        """
        Returns the get_queryset for employee user group
        """
        return get_locations_for_employee(
            self.request.user, include_self=True)

    def _perform_update_by_organization_admin(self, serializer):
        serializer.save()
