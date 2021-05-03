"""
Defines the REST API views for organizations models.
"""

from rest_framework import exceptions

from core.permissions import UserGroups
from core.utils import (field_invalid_error, field_required_error,
                        filter_objects_by_id_list, get_id_list)
from core.views import CoreListCreateDestroyView, CoreRetrieveUpdateDestroyView
from organizations.api.serializers import (OrganizationCreateSerializer,
                                           OrganizationDetailSerializer,
                                           OrganizationListSerializer,
                                           OrganizationUpdateSerializer)
from organizations.models import Organization
from organizations.permissions import (
    OrganizationsListCreateDestroyPermission,
    OrganizationsRetrieveUpdateDestroyPermission)


class OrganizationsListCreateDestroyView(CoreListCreateDestroyView):
    """
    Defines the organizations list-create-destroy view.
    """

    queryset = Organization.objects.none()
    permission_classes = (OrganizationsListCreateDestroyPermission,)
    ordering_fields = ['id', 'name']
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
        'DELETE': lambda organization: organization.get_descendants()
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
        return OrganizationListSerializer

    def _get_create_serializer_class(self):
        """
        Returns the create serializer.
        """
        return OrganizationCreateSerializer

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
            },
            'create': {
                **api_handler_by_group['create'],
                UserGroups.ORGANIZATION_ADMIN_GROUP:
                    self._perform_create_by_organization_admin
            }
        }

    def _get_organization_admin_queryset(self, request):
        """
        For an organization admin, all the organizations below the user
        organization are returned. In case a list of ids is provided, the
        organizations tree is filtered further by ids.
        """
        id_list = get_id_list(request)
        organizations_tree = \
            self.organizations_tree_wrt_request[request.method](
                request.user.organization)

        # get the organization tree of the user if its an admin
        if id_list:
            return filter_objects_by_id_list(
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
            raise exceptions.ValidationError({
                'parent': field_required_error()
            })

        # see if the parent of requested organization is within descendents
        # of the current user.
        organizations_tree = \
            self.organizations_tree_wrt_request[self.request.method](
                self.request.user.organization)
        if not organizations_tree.filter(
                id=self.request.data.get('parent', None)).exists():
            raise exceptions.ValidationError({
                'parent': field_invalid_error()
            })

        # create organization in db
        serializer.save()


class OrganizationsRetrieveUpdateDestroyView(CoreRetrieveUpdateDestroyView):
    """
    Defines the organizations retrieve-update-destroy view.
    """

    queryset = Organization.objects.none()  # Added for model permissions
    permission_classes = (OrganizationsRetrieveUpdateDestroyPermission,)

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

    def _get_detail_serializer_class(self):
        """
        Returns the detail serializer.
        """
        return OrganizationDetailSerializer

    def _get_update_serializer_class(self):
        """
        Returns the update serializer.
        """
        return OrganizationUpdateSerializer

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
        return self.organizations_tree_wrt_request[request.method](
            request.user.organization)

    def _get_employee_queryset(self, request):
        """
        Returns the get_queryset for employee user group
        """
        return self._model.objects.filter(
            id=request.user.organization.id)

    def _perform_update_by_organization_admin(self, serializer):
        """
        Performs update on organization as long as it is in the get_queryset.
        """
        serializer.save()
