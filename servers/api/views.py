from core.permissions import UserGroups
from core.utils import *
from core.views import *
from locations.models import Block
from locations.utils import *
from servers.utils import *

from ..models import Server
from ..permissions import (ServersListCreateDestroyPermission,
                           ServersRetrieveUpdateDestroyPermission)
from .serializers import ServerSerializer


class ServerView:
    ordering_fields = ['id', 'ip_addr', 'block', 'camera']

    def _get_model(self):
        """
        Returns the get queryset.
        """

        return Server


class ServersListCreateDestroyView(CoreListCreateDestroyView, ServerView):
    queryset = Server.objects.none()
    serializer_class = ServerSerializer
    permission_classes = (ServersListCreateDestroyPermission,)

    def _get_model(self):

        return ServerView._get_model(self)


def _define_get_queryset_by_group_fn(self):

    return {
        UserGroups.ORGANIZATION_ADMIN_GROUP:
            self._get_organizations_admin_queryset,
        UserGroups.EMPLOYEE_GROUP:
            self._get_employee_queryset,
    }


def _perform_create_by_organization_admin(self, serializer):
    try:
        block = Block.objects.get(self.request.data['block'])
    except Exception as exceptions:
        raise exceptions.ValidationError(
            {
                'block': 'Block not found'
            })
    locations = get_locations_for_organization_admin(
        self.user, include_self=true)

    if not locations.filter(id=block.floor.location.id):
        raise exceptions.ValidationError(
            {
                'block': 'User is not authorised'
            })

    serializer.save()


def _get_organizations_admin_queryset(self):
    servers = get_servers_for_organization_admin(
        self.request.user)

    id_list = self._get_id_list()
    if id_list:
        return self._filter_objects_by_id_list(
            servers, id_list)

        return servers


def _get_employee_queryset(self):
    servers = get_servers_for_employee(
        self.request.user)
    id_list = self._get_id_list()
    if id_list:
        return self._filter_objects_by_id_list(
            servers, id_list)
        return servers


def _define_perform_create_by_group_fn(self):

    return {
        UserGroups.ORGANIZATION_ADMIN_GROUP:
        self._perform_create_by_organization_admin
    }

    def _order_by(self):

        return ServerView._order_by(self)


class ServersRetrieveUpdateDestroyView(
        CoreRetrieveUpdateDestroyView, ServerView):
    """
    Defines the servers retrieve-update-destroy view.
    """
    queryset = Server.objects.none()
    serializer_class = ServerSerializer
    permission_classes = (ServersListCreateDestroyPermission,)

    def _get_model(self):
        """
        Returns the model for this view
        """

        return ServerView._get_model(self)

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
        return get_servers_for_organization_admin(
            self.request.user)

    def _get_employee_queryset(self):
        """
        Returns the get_queryset for employee user group
        """
        return get_servers_for_employee(
            self.request.user)

    def _perform_update_by_organization_admin(self, serializer):
        serializer.save()
