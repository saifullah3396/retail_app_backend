"""
Defines the REST API views for floors models.
"""


from rest_framework import exceptions

from core.permissions import UserGroups
from core.utils import (field_invalid_error, get_employee_authorized_locations,
                        get_object_by_id,
                        get_organization_admin_authorized_locations)
from core.views import CoreListCreateDestroyView, CoreRetrieveUpdateDestroyView
from locations.api.serializers import (BlockCreateSerializer,
                                       BlockDetailSerializer,
                                       BlockListSerializer,
                                       BlockUpdateSerializer)
from locations.models import Block, Floor
from locations.permissions import (BlocksListCreateDestroyPermission,
                                   BlocksRetrieveUpdateDestroyPermission)


class BlocksView:
    """
    Defines the base interface class for the floors rest api views.
    """

    # pylint: disable=no-member
    ordering_fields = ['id', 'name']
    filterset_fields = {
        'name': ['exact', 'icontains'],
    }

    def _get_model(self):
        """
        Returns the view model.
        """

        return Block

    def _order_by(self):
        """
        Returns the field with respect to which queries are to be ordered.
        """
        return 'name'

    def _filter_blocks_with_locations(self, locations):
        """
        Returns all the blocks in the given locations set
        """

        # get all blocks in requested floor
        blocks_in_locations = \
            self._get_model().objects.filter(floor__location__in=locations)

        # filter with ids if present
        id_list = self._get_id_list()
        if id_list:
            return self._filter_objects_by_id_list(
                blocks_in_locations, id_list)

        return blocks_in_locations


class BlocksListCreateDestroyView(CoreListCreateDestroyView, BlocksView):
    """
    Defines the list-create-destroy view for Blocks.
    """

    queryset = Block.objects.none()  # Added for model permissions
    permission_classes = (BlocksListCreateDestroyPermission,)

    def _get_model(self):
        """
        Returns the view model.
        """

        return BlocksView._get_model(self)

    def _order_by(self):
        """
        Returns the field with respect to which queries are to be ordered.
        """
        return BlocksView._order_by(self)

    def _get_list_serializer_class(self):
        """
        Returns the list serializer.
        """
        return BlockListSerializer

    def _get_create_serializer_class(self):
        """
        Returns the create serializer.
        """
        return BlockCreateSerializer

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

        locations = get_organization_admin_authorized_locations(
            self.request.user)
        blocks = self._filter_blocks_with_locations(locations)
        return blocks

    def _get_employee_queryset(self):
        """
        For employee, all blocks are returned within the queried
        floor/location as long as the location is authorized.
        """

        locations = get_employee_authorized_locations(self.request.user)
        return self._filter_blocks_with_locations(locations)

    def _perform_create_by_organization_admin(self, serializer):
        """
        For organization admin, the block is created within the queried
        floor/location as long as the location is authorized.
        """

        # get floor
        floor = get_object_by_id(
            Floor, self.request.data.get('floor', None))

        if not floor:
            raise exceptions.ValidationError(
                {
                    'floor': field_invalid_error()
                })

        # see whether floor location is within authorized locations
        locations = get_organization_admin_authorized_locations(
            self.request.user)
        if not locations.filter(id=floor.location.id).exists():
            raise exceptions.ValidationError(
                {
                    'location': field_invalid_error()
                })

        # create floor in db
        serializer.save()


class BlocksRetrieveUpdateDestroyView(
        CoreRetrieveUpdateDestroyView, BlocksView):
    """
    Defines the retrieve-update-destroy view for blocks.
    """

    queryset = Block.objects.none()  # Added for model permissions
    permission_classes = (BlocksRetrieveUpdateDestroyPermission,)

    def _get_model(self):
        """
        Returns the view model.
        """

        return BlocksView._get_model(self)

    def _get_detail_serializer_class(self):
        """
        Returns the detail serializer.
        """
        return BlockDetailSerializer

    def _get_update_serializer_class(self):
        """
        Returns the update serializer.
        """
        return BlockUpdateSerializer

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

        locations = get_organization_admin_authorized_locations(
            self.request.user)
        return self._filter_blocks_with_locations(locations)

    def _get_employee_queryset(self):
        """
        For employee, all blocks are returned within the queried
        floor/location as long as the location is authorized.
        """

        locations = get_employee_authorized_locations(self.request.user)
        return self._filter_blocks_with_locations(locations)

    def _perform_update_by_organization_admin(self, serializer):
        """
        For organization admin, the block is updated as long as it is within
        the get queryset
        """

        if 'floor' in self.request.data:
            # get floor
            floor = get_object_by_id(
                Floor, self.request.data.get('floor', None))

            if not floor:
                raise exceptions.ValidationError(
                    {
                        'floor': field_invalid_error()
                    })

            # see whether floor location is within authorized locations
            locations = get_organization_admin_authorized_locations(
                self.request.user)
            if not locations.filter(id=floor.location.id).exists():
                raise exceptions.ValidationError(
                    {
                        'location': field_invalid_error()
                    })

        serializer.save()
