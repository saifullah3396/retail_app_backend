
from core.utils import *
from core.views import *
from django.contrib.auth.models import Group
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import *
from rest_framework import filters, pagination
from rest_framework.generics import *
from rest_framework.response import Response
from rest_framework_jwt import authentication

from locations.models import Location, Floor
from locations.permissions import *
from locations.api.serializers import *


class FloorsListCreateDestroyView(CoreListCreateDestroyView):
    """
    Defines the list-create-destroy view for Floor.
    """

    queryset = Floor.objects.none()  # Added for model permissions
    serializer_class = FloorListSerializer
    permission_classes = (FloorsListCreateDestroyPermission,)
    ordering_fields = ['id', 'number']
    filterset_fields = {
        'number': ['exact'],
    }

    # Define the mapping from request type to query that returns the
    # organizations tree that is used in the requests.
    organizations_tree_wrt_request = {
        'GET': lambda organization: organization.get_descendants(
            include_self=True),
        'POST': lambda organization: organization.get_descendants(
            include_self=True),
    }

    def _get_organizations_tree(self, organization):
        """
        Returns the organizations descendents tree given the request type and
        organzation.
        """
        return self.organizations_tree_wrt_request[self.request.method](
            organization)

    def _get_location_by_uuid(self, uuid):
        try:
            return Location.objects.get(id=uuid)
        except Location.DoesNotExist:
            raise exceptions.ValidationError(
                "Queried location does not exist.")

    def _get_floors_in_location(self, location):
        return Floor.objects.filter(location=location)

    def _filter_floors_with_location(self, location):
        # get all floors of the requested location
        floors_in_location = self._get_floors_in_location(location)

        # filter with ids if present
        id_list = self._get_id_list()
        if id_list:
            return self._filter_objects_by_id_list(
                floors_in_location, id_list)

        return floors_in_location

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

    def _get_model(self):
        """
        Returns the get queryset for staff users.
        """

        return Floor

    def _order_by(self):
        """
        Returns the field with respect to which queries are to be ordered.
        """
        return 'number'

    def _get_queryset_by_staff(self):
        """
        Returns all the floors within any provided location for staff users.
        """
        uuid = self.kwargs.get('location_id')
        location = self._get_location_by_uuid(uuid)
        return self._filter_floors_with_location(location)

    def _get_organization_admin_queryset(self):
        """
        For organization admin, all floors are returned within the queried
        location as long as the location is within the organization
        descendents.
        """

        # get location uid
        uuid = self.kwargs.get('location_id')

        # get the location
        location = self._get_location_by_uuid(uuid)

        # get organizations tree of this admin
        organizations_tree = self._get_organizations_tree(
            self.request.user.organization)

        # see if the organization of the location is within descendents of
        # the organization of this admin.
        if not organizations_tree.exists(location.organization):
            raise exceptions.ValidationError("Invalid location provided.")

        return self._filter_floors_with_location(location)

    def _get_employee_queryset(self):
        """
        For employees, all floors are returned within the queried
        location as long as the location is within authorized_locations for the
        employee.
        """

        # get location uid
        uuid = self.kwargs.get('location_id')

        # get the location
        location = self._get_location_by_uuid(uuid)

        # see if the organization of the location and the employee match
        if location.organization != self.user.organization:
            raise exceptions.ValidationError("Invalid location provided.")

        # see if the location is within employees 'authorized_locations'
        if location not in self.user.authorized_locations:
            raise exceptions.ValidationError(
                "Unauthorized location requested.")

        return self._filter_floors_with_location(location)

    def _perform_create_by_organization_admin(self, serializer):
        """
        For organization admin, the floor is created within the queried
        location as long as the location is within the organization
        descendents.
        """

        # get location uid
        uuid = self.kwargs.get('location_id')

        # get the location
        location = self._get_location_by_uuid(uuid)

        # get organizations tree of this admin
        organizations_tree = self._get_organizations_tree(
            self.request.user.organization)

        # see if the organization of the location is within descendents of
        # the organization of this admin.
        if not organizations_tree.exists(location.organization):
            raise exceptions.ValidationError("Invalid location provided.")

        # create floor in db
        serializer.save()


class FloorsRetrieveUpdateDestroyView(CoreRetrieveUpdateDestroyView):
    """
    Defines the retrieve-update-destroy view for floors.
    """

    queryset = Location.objects.none()  # Added for model permissions
    serializer_class = FloorDetailSerializer
    permission_classes = (LocationsRetrieveUpdateDestroyPermission,)
    ordering_fields = ['id', 'number']
    filterset_fields = {
        'number': ['exact'],
    }

    # Define the mapping from request type to query that returns the
    # organizations tree that is used in the requests.
    organizations_tree_wrt_request = {
        'GET': lambda organization: organization.get_descendants(
            include_self=True),
        'POST': lambda organization: organization.get_descendants(
            include_self=True),
        'PATCH': lambda organization: organization.get_descendants(
            include_self=True),
        'DELETE': lambda organization: organization.get_descendants(
            include_self=True
        )
    }

    def _get_organizations_tree(self, organization):
        """
        Returns the organizations descendents tree given the request type and
        organzation.
        """
        return self.organizations_tree_wrt_request[self.request.method](
            organization)

    def _get_location_by_uuid(self, uuid):
        try:
            return Location.objects.get(id=uuid)
        except Location.DoesNotExist:
            raise exceptions.ValidationError(
                "Queried location does not exist.")

    def _get_floors_in_location(self, location):
        return Floor.objects.filter(location=location)

    def _filter_floors_with_location(self, location):
        # get all floors of the requested location
        floors_in_location = self._get_floors_in_location(location)

        # filter with ids if present
        id_list = self._get_id_list()
        if id_list:
            return self._filter_objects_by_id_list(
                floors_in_location, id_list)

        return floors_in_location

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

    def _get_model(self):
        """
        Returns the get queryset for staff users.
        """
        return Floor

    def _get_queryset_by_staff(self):
        """
        Returns all the floors within any provided location for staff users.
        """
        uuid = self.kwargs.get('location_id')
        location = self._get_location_by_uuid(uuid)
        return self._filter_floors_with_location(location)

    def _get_organization_admin_queryset(self):
        """
        For organization admin, all floors are returned within the queried
        location as long as the location is within the organization
        descendents.
        """

        # get location uid
        uuid = self.kwargs.get('location_id')

        # get the location
        location = self._get_location_by_uuid(uuid)

        # get organizations tree of this admin
        organizations_tree = self._get_organizations_tree(
            self.request.user.organization)

        # see if the organization of the location is within descendents of
        # the organization of this admin.
        if not organizations_tree.exists(location.organization):
            raise exceptions.ValidationError("Invalid location provided.")

        return self._filter_floors_with_location(location)

    def _get_employee_queryset(self):
        """
        For employees, all floors are returned within the queried
        location as long as the location is within authorized_locations for the
        employee.
        """

        # get location uid
        uuid = self.kwargs.get('location_id')

        # get the location
        location = self._get_location_by_uuid(uuid)

        # see if the organization of the location and the employee match
        if location.organization != self.user.organization:
            raise exceptions.ValidationError("Invalid location provided.")

        # see if the location is within employees 'authorized_locations'
        if location not in self.user.authorized_locations:
            raise exceptions.ValidationError(
                "Unauthorized location requested.")

        return self._filter_floors_with_location(location)
