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
from locations.api.utils import filter_blocks_with_locations
from locations.models import Block, Floor
from locations.permissions import (BlocksListCreateDestroyPermission,
                                   BlocksRetrieveUpdateDestroyPermission)


class BlocksListCreateDestroyView(CoreListCreateDestroyView):
    """
    Defines the list-create-destroy view for Blocks.
    """

    queryset = Block.objects.none()  # Added for model permissions
    permission_classes = (BlocksListCreateDestroyPermission,)
    ordering_fields = ['id', 'name']
    filterset_fields = {
        'name': ['exact', 'icontains'],
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
        return BlockListSerializer

    def _get_create_serializer_class(self):
        """
        Returns the create serializer.
        """
        return BlockCreateSerializer

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
        For organization admin, all blocks are returned within the queried
        floor/location as long as the location is authorized.
        """

        locations = get_organization_admin_authorized_locations(request.user)
        blocks = filter_blocks_with_locations(request, locations)
        return blocks

    def _get_employee_queryset(self, request):
        """
        For employee, all blocks are returned within the queried
        floor/location as long as the location is authorized.
        """

        locations = get_employee_authorized_locations(request.user)
        return filter_blocks_with_locations(request, locations)

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


class BlocksRetrieveUpdateDestroyView(CoreRetrieveUpdateDestroyView):
    """
    Defines the retrieve-update-destroy view for blocks.
    """

    queryset = Block.objects.none()  # Added for model permissions
    permission_classes = (BlocksRetrieveUpdateDestroyPermission,)

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
        For organization admin, all blocks are returned within the queried
        floor/location as long as the location is authorized.
        """

        locations = get_organization_admin_authorized_locations(request.user)
        return filter_blocks_with_locations(request, locations)

    def _get_employee_queryset(self, request):
        """
        For employee, all blocks are returned within the queried
        floor/location as long as the location is authorized.
        """

        locations = get_employee_authorized_locations(request.user)
        return filter_blocks_with_locations(request, locations)

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
