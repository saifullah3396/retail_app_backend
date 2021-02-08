from core.utils import *
from core.views import *
from django.contrib.auth.models import Group
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import *
from rest_framework import filters, pagination
from rest_framework.generics import *
from rest_framework.response import Response
from rest_framework_jwt import authentication

from ..models import Organization
from ..permissions import *
from .serializers import OrganizationSerializer


class OrganizationsListCreateDestroyView(CoreListCreateDestroyView):
    """
    Defines the organizations list-create-destroy view.
    """

    queryset = Organization.objects.none()
    serializer_class = OrganizationSerializer
    permission_classes = (OrganizationsListCreateDestroyPermission,)
    ordering_fields = ['id', 'name', 'desc']
    filterset_fields = {
        'name': ['exact', 'icontains'],
    }

    # Define the mapping from request type to query that returns the
    # organizations tree that is used in the requests. For example, in DELETE
    # requests, organization does not include itself while in GET it does
    organizations_tree_wrt_request = {
        'GET': lambda organization: organization.get_descendants(
            include_self=True),
        'DELETE': lambda organization: organization.get_descendants()
    }

    def _define_get_queryset_by_group_fn(self):
        """
        Returns a dictionary mapping user group to get_queryset function
        that will be called if the request user is in that user group.
        """
        return {
            UserGroups.ORGANIZATION_ADMIN_GROUP:
                self._get_organization_admin_queryset
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

        return Organization

    def _order_by(self):
        """
        Returns the field with respect to which queries are to be ordered.
        """
        return 'name'

    def _get_organizations_tree(self, organization):
        """
        Returns the organizations descendents tree given the request type and
        organzation.
        """
        return self.organizations_tree_wrt_request[self.request.method](
            organization)

    def _get_organization_admin_queryset(self):
        """
        For an organization admin, all the organizations below the user
        organization are returned. In case a list of ids is provided, the
        organizations tree is filtered further by ids.
        """
        id_list = self._get_id_list()
        organizations_tree = self._get_organizations_tree(
            self.request.user.organization)

        # get the organization tree of the user if its an admin
        if id_list:
            return self._filter_objects_by_id_list(
                organizations_tree, id_list
            )
        return organizations_tree

    def _perform_create_by_organization_admin(self, serializer):
        """
        Creates a new organization, given the request is valid for an
        organization admin. This functions validates two things; the new
        organization must have a parent, and the parent must be within the
        descendents of the organization of this admin.
        """

        # an organization cannot be created without a parent id
        if 'parent' not in self.request.data:
            raise exceptions.PermissionDenied()

        # see if the parent of requested organization is within descendents
        # of the current user.
        descendents = self.request.user.organization.get_descendants(
            include_self=True)
        if not descendents.filter(id=self.request.data.get('parent', None)):
            raise exceptions.PermissionDenied()

        # create organization in db
        serializer.save()


class OrganizationsRetrieveUpdateDestroyView(CoreRetrieveUpdateDestroyView):
    """
    Defines the organizations retrieve-update-destroy view.
    """

    queryset = Organization.objects.none()  # Added for model permissions
    serializer_class = OrganizationSerializer
    permission_classes = (OrganizationsRetrieveUpdateDestroyPermission,)
    ordering_fields = ['id', 'name', 'desc']
    filterset_fields = {
        'name': ['exact', 'icontains'],
    }

    # Define the mapping from request type to query that returns the
    # organizations tree that is used in the requests. For example, in DELETE
    # requests, organization does not include itself while in GET it does
    organizations_tree_wrt_request = {
        'GET': lambda organization: organization.get_descendants(
            include_self=True),
        'POST': lambda organization: organization.get_descendants(
            include_self=True),
        'PATCH': lambda organization: organization.get_descendants(
            include_self=True),
        'DELETE': lambda organization: organization.get_descendants()
    }

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
        return Organization

    def _get_organizations_tree(self, organization):
        """
        Returns the organizations descendents tree given the request type and
        organzation.
        """
        return self.organizations_tree_wrt_request[self.request.method](
            organization)

    def _get_organization_admin_queryset(self):
        """
        Returns the get_queryset for organization admin user group
        """
        return self._get_organizations_tree(self.request.user.organization)

    def _get_employee_queryset(self):
        """
        Returns the get_queryset for employee user group
        """
        return self._get_model().objects.filter(
            id=self.request.user.organization.id)
