
from core.utils import *
from core.views import *
from django.contrib.auth.models import Group
from django_filters.rest_framework import DjangoFilterBackend
from locations.api.serializers import *
from locations.models import Block, Location
from locations.permissions import *
from rest_framework import *
from rest_framework import filters, pagination
from rest_framework.generics import *
from rest_framework.response import Response
from rest_framework_jwt import authentication


class BlocksView:
    ordering_fields = ['id', 'name']
    filterset_fields = {
        'name': ['exact', 'icontains'],
    }

    def _get_model(self):
        """
        Returns the get queryset for staff users.
        """

        return Block

    def _order_by(self):
        """
        Returns the field with respect to which queries are to be ordered.
        """
        return 'name'

    def _get_queryset_by_staff(self):
        """
        Returns all the floors within any provided location for staff users.
        """
        location = self._get_location_by_uuid(self.kwargs.get('location_id'))
        floor = self._get_floor_by_uuid(self.kwargs.get('floor_id'))
        return self._filter_blocks_with_location_and_floor(location, floor)

    def _get_organizations_tree(self, organization):
        """
        Returns the organizations descendents tree given the request type and
        organzation.
        """
        return self.organizations_tree_wrt_request[self.request.method](
            organization)

    def _get_location_by_uuid(self, uuid):
        """
        Returns the location given its id if it exists
        """
        try:
            return Location.objects.get(id=uuid)
        except Location.DoesNotExist:
            raise exceptions.ValidationError(
                "Queried location does not exist.")

    def _get_floor_by_uuid(self, uuid):
        """
        Returns the floor given its id if it exists
        """
        try:
            return Floor.objects.get(id=uuid)
        except Floor.DoesNotExist:
            raise exceptions.ValidationError(
                "Queried floor does not exist.")

    def _get_floors_in_location(self, location):
        """
        Returns all floors in given location
        """
        return Location.objects.filter(location=location)

    def _get_blocks_in_floor(self, floor):
        """
        Returns all blocks in given floor
        """
        return Block.objects.filter(floor=floor)

    def _filter_blocks_with_location_and_floor(self, location, floor):
        """
        Checks whether the location of the floor and requested location match.
        After that it returns all the blocks in the given floor.
        """

        # match location of floor with requested location
        if floor.location != location:
            raise exceptions.ValidationError(
                "Queried floor does not exist in queried location.")

        # get all blocks in requested floor
        blocks_in_floors = self._get_blocks_in_floor(floor)

        # filter with ids if present
        id_list = self._get_id_list()
        if id_list:
            return self._filter_objects_by_id_list(
                blocks_in_floors, id_list)

        return blocks_in_floors


class BlocksListCreateDestroyView(CoreListCreateDestroyView, BlocksView):
    """
    Defines the list-create-destroy view for Block.
    """

    queryset = Block.objects.none()  # Added for model permissions
    serializer_class = BlockListSerializer
    permission_classes = (BlocksListCreateDestroyPermission,)

    # Define the mapping from request type to query that returns the
    # organizations tree that is used in the requests.
    organizations_tree_wrt_request = {
        'GET': lambda organization: organization.get_descendants(
            include_self=True),
        'POST': lambda organization: organization.get_descendants(
            include_self=True),
    }

    def _get_model(self):
        """
        Returns the get queryset for staff users.
        """

        return BlocksView._get_model(self)

    def _order_by(self):
        """
        Returns the field with respect to which queries are to be ordered.
        """
        return BlocksView._order_by(self)

    def _get_queryset_by_staff(self):
        """
        Returns all the floors within any provided location for staff users.
        """
        return BlocksView._get_queryset_by_staff(self)

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
        location and floor as long as the location is within the organization
        descendents.
        """

        # get location and floor
        location = self._get_location_by_uuid(self.kwargs.get('location_id'))
        floor = self._get_floor_by_uuid(self.kwargs.get('floor_id'))

        # get organizations tree of this admin
        organizations_tree = self._get_organizations_tree(
            self.request.user.organization)

        # see if the organization of the location is within descendents of
        # the organization of this admin.
        if not organizations_tree.exists(location.organization):
            raise exceptions.ValidationError("Invalid location provided.")

        return self._filter_blocks_with_location_and_floor(location, floor)

    def _get_employee_queryset(self):
        """
        For employees, all floors are returned within the queried
        location as long as the location is within authorized_locations for the
        employee.
        """

        # get location and floor
        location = self._get_location_by_uuid(self.kwargs.get('location_id'))
        floor = self._get_floor_by_uuid(self.kwargs.get('floor_id'))

        # see if the organization of the location and the employee match
        if location.organization != self.user.organization:
            raise exceptions.ValidationError("Invalid location provided.")

        # see if the location is within employees 'authorized_locations'
        if location not in self.user.authorized_locations:
            raise exceptions.ValidationError(
                "Unauthorized location requested.")

        return self._filter_blocks_with_location_and_floor(location, floor)

    def _perform_create_by_organization_admin(self, serializer):
        """
        For organization admin, the floor is created within the queried
        location as long as the location is within the organization
        descendents.
        """

        # get location and floor
        location = self._get_location_by_uuid(self.kwargs.get('location_id'))
        floor = self._get_floor_by_uuid(self.kwargs.get('floor_id'))

        # get organizations tree of this admin
        organizations_tree = self._get_organizations_tree(
            self.request.user.organization)

        # see if the organization of the location is within descendents of
        # the organization of this admin.
        if not organizations_tree.exists(location.organization):
            raise exceptions.ValidationError("Invalid location provided.")

        # create floor in db
        serializer.save()


class BlocksRetrieveUpdateDestroyView(
        CoreRetrieveUpdateDestroyView, BlocksView):
    """
    Defines the retrieve-update-destroy view for floors.
    """

    queryset = Location.objects.none()  # Added for model permissions
    serializer_class = BlockDetailSerializer
    permission_classes = (LocationsRetrieveUpdateDestroyPermission,)

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

    def _get_model(self):
        """
        Returns the get queryset for staff users.
        """

        return BlocksView._get_model(self)

    def _get_queryset_by_staff(self):
        """
        Returns all the floors within any provided location for staff users.
        """
        return BlocksView._get_queryset_by_staff(self)

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
        location and floor as long as the location is within the organization
        descendents.
        """

        # get location and floor
        location = self._get_location_by_uuid(self.kwargs.get('location_id'))
        floor = self._get_floor_by_uuid(self.kwargs.get('floor_id'))

        # get organizations tree of this admin
        organizations_tree = self._get_organizations_tree(
            self.request.user.organization)

        # see if the organization of the location is within descendents of
        # the organization of this admin.
        if not organizations_tree.exists(location.organization):
            raise exceptions.ValidationError("Invalid location provided.")

        return self._filter_blocks_with_location_and_floor(location, floor)

    def _get_employee_queryset(self):
        """
        For employees, all floors are returned within the queried
        location as long as the location is within authorized_locations for the
        employee.
        """

        # get location and floor
        location = self._get_location_by_uuid(self.kwargs.get('location_id'))
        floor = self._get_floor_by_uuid(self.kwargs.get('floor_id'))

        # see if the organization of the location and the employee match
        if location.organization != self.user.organization:
            raise exceptions.ValidationError("Invalid location provided.")

        # see if the location is within employees 'authorized_locations'
        if location not in self.user.authorized_locations:
            raise exceptions.ValidationError(
                "Unauthorized location requested.")

        return self._filter_blocks_with_location_and_floor(location, floor)

    def _perform_update_by_organization_admin(self, serializer):
        serializer.save()
