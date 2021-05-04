"""
Defines the REST api views for deepstream servers.
"""
from rest_framework import exceptions

from core.permissions import UserGroups
from core.utils import (field_invalid_error, get_employee_authorized_locations,
                        get_object_by_id, get_organization_servers)
from core.views import CoreListCreateDestroyView, CoreRetrieveUpdateDestroyView
from deepstream_servers.api.serializers import (
    DeepstreamServerCreateSerializer, DeepstreamServerDetailSerializer,
    DeepstreamServerListSerializer, DeepstreamServerUpdateSerializer)
from deepstream_servers.api.utils import filter_servers
from deepstream_servers.models import DeepstreamServer
from deepstream_servers.permissions import (
    DeepstreamServersListCreateDestroyPermission,
    DeepstreamServersRetrieveUpdateDestroyPermission)


class DeepstreamServersListCreateDestroyView(CoreListCreateDestroyView):
    """
    Defines the deepstream servers retrieve-update-destroy view.
    """
    queryset = DeepstreamServer.objects.none()
    permission_classes = (DeepstreamServersListCreateDestroyPermission,)
    ordering_fields = ['id', 'ip_addr', 'organization']
    filterset_fields = {
        'organization__name': ['icontains'],
    }

    def _order_by(self):
        """
        Returns the field with respect to which queries are to be ordered.
        """
        return 'id'

    def _get_list_serializer_class(self):
        """
        Returns the list serializer.
        """
        return DeepstreamServerListSerializer

    def _get_create_serializer_class(self):
        """
        Returns the create serializer.
        """
        return DeepstreamServerCreateSerializer

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
                    self._get_employee_queryset
            },
            'create': {
                **api_handler_by_group['create'],
                UserGroups.ORGANIZATION_ADMIN_GROUP:
                    self._perform_create_by_organization_admin
            }
        }

    def _get_organization_admin_queryset(self, request):
        """
        Returns all servers within user authorized locations.
        """
        servers = get_organization_servers(request.user.organization)
        return filter_servers(request, servers)

    def _get_employee_queryset(self, request):
        """
        Returns all servers are returned within the users
        authorized locations.
        """
        servers = get_organization_servers(request.user.organization)
        return filter_servers(request, servers)

    def _perform_create_by_organization_admin(self, serializer):
        """
        Creates a server as long as its block is valid and is within
        user authorized locations.
        """

        # see if the organization of requested server is within
        # descendents of this admin
        descendents = self.request.user.organization.get_descendants(
            include_self=True)
        if not descendents.filter(id=self.request.data['organization']):
            raise exceptions.ValidationError(
                {
                    'organization': field_invalid_error()
                })

        # create floor in db
        serializer.save()


class DeepstreamServersRetrieveUpdateDestroyView(CoreRetrieveUpdateDestroyView):
    """
    Defines the deepstream servers retrieve-update-destroy view.
    """
    queryset = DeepstreamServer.objects.none()
    permission_classes = (DeepstreamServersRetrieveUpdateDestroyPermission,)

    def _get_detail_serializer_class(self):
        """
        Returns the detail serializer.
        """
        return DeepstreamServerDetailSerializer

    def _get_update_serializer_class(self):
        """
        Returns the update serializer.
        """
        return DeepstreamServerUpdateSerializer

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
                    self._get_employee_queryset
            },
            'update': {
                **api_handler_by_group['update'],
                UserGroups.ORGANIZATION_ADMIN_GROUP:
                    self._perform_update_by_organization_admin
            }
        }

    def _get_organization_admin_queryset(self, request):
        """
        Returns all servers are returned within the users
        authorized locations.
        """
        servers = get_organization_servers(request.user.organization)
        return filter_servers(request, servers)

    def _get_employee_queryset(self, request):
        """
        Returns all servers are returned within the users
        authorized locations.
        """
        servers = get_organization_servers(request.user.organization)
        return filter_servers(request, servers)

    def _perform_update_by_organization_admin(self, serializer):
        """
        Updates the model based on validated data.
        """

        if 'organization' in self.request.data:
            # see if the organization of requested server is within
            # descendents of this admin
            descendents = self.request.user.organization.get_descendants(
                include_self=True)
            if not descendents.filter(id=self.request.data['organization']):
                raise exceptions.ValidationError(
                    {
                        'organization': field_invalid_error()
                    })
        serializer.save()
