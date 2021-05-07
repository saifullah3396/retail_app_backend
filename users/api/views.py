"""
Defines the REST API views for users models.
"""

from rest_framework import exceptions, serializers, status
from rest_framework.response import Response

from core.permissions import UserGroups
from core.utils import is_employee, is_organization_admin
from core.views import CoreListCreateDestroyView, CoreRetrieveUpdateDestroyView
from locations.models import Location
from users.api.serializers import (AppUserCreateSerializer,
                                   AppUserEmployeeUpdateSerializer,
                                   AppUserListSerializer,
                                   AppUserOrganizationAdminUpdateSerializer,
                                   AppUserRetrieveSerializer,
                                   AppUserUpdateSerializer)
from users.api.utils import (filter_users_with_organizations,
                             get_users_in_organizations)
from users.models import AppUser
from users.permissions import (AppUsersListCreateDestroyPermission,
                               AppUsersRetrieveUpdateDestroyPermission)


class AppUsersListCreateDestroyView(CoreListCreateDestroyView):
    """
    Defines the list-create-destroy view.
    """

    queryset = AppUser.objects.none()
    permission_classes = (AppUsersListCreateDestroyPermission,)
    ordering_fields = ['id', 'username']
    filterset_fields = {
        'username': ['exact', 'icontains'],
    }

    # Define the mapping from request type to query that returns the
    # organizations tree that is used in the requests. For example, in DELETE
    # requests, organization does not include itself while in GET it does
    organizations_tree_wrt_request = {
        'GET': lambda organization: organization.get_descendants(
            include_self=True),
        'DELETE': lambda organization: organization.get_descendants()
    }

    def _order_by(self):
        """
        Returns the field with respect to which queries are to be ordered.
        """
        return 'first_name'

    def _get_list_serializer_class(self):
        """
        Returns the list serializer.
        """
        return AppUserListSerializer

    def _get_create_serializer_class(self):
        """
        Returns the create serializer.
        """
        return AppUserCreateSerializer

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
            'create': {}
        }

    def _get_organization_admin_queryset(self):
        """
        For an organization admin, all the users in the organizations below
        organization are returned. In case a list of ids is provided, the
        users are filtered further by ids.
        """
        organizations_tree = \
            self.organizations_tree_wrt_request[self.request.method](
                self.request.user.organization)
        return filter_users_with_organizations(organizations_tree)


class AppUsersRetrieveUpdateDestroyView(CoreRetrieveUpdateDestroyView):
    """
    Defines the retrieve-update-destroy view.
    """

    queryset = AppUser.objects.none()  # Added for model permissions
    permission_classes = (AppUsersRetrieveUpdateDestroyPermission,)

    def _get_detail_serializer_class(self):
        """
        Returns the detail serializer.
        """
        return AppUserRetrieveSerializer

    def _get_update_serializer_class(self):
        """
        Returns the update serializer.
        """
        if self.request.user.is_staff:
            return AppUserUpdateSerializer
        elif is_organization_admin(self.request.user):
            return AppUserOrganizationAdminUpdateSerializer
        elif is_employee(self.request.user):
            return AppUserEmployeeUpdateSerializer

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

    def get_queryset(self):
        """
        Implements the get_queryset function. Any final modifications to the
        query set are made here.
        """
        if self.kwargs.get('pk') == "self":
            self.kwargs['pk'] = self.request.user.id
        return super().get_queryset()

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
                    self._perform_update_by_organization_admin,
                UserGroups.EMPLOYEE_GROUP:
                    self._perform_update_by_employee,
            }
        }

    def _get_organization_admin_queryset(self):
        """
        Returns the get_queryset for organization admin user group
        """

        # get all organizations under this users organization
        organizations_tree = \
            self.organizations_tree_wrt_request[self.request.method](
                self.request.user.organization)

        # get all users in the tree
        users_in_tree = get_users_in_organizations(organizations_tree)
        return users_in_tree

    def _get_employee_queryset(self):
        """
        Returns the get_queryset for employee user group
        """
        return get_users_in_organizations(self.request.user.organization)

    def _perform_update_by_organization_admin(self, serializer):
        data = serializer.validated_data
        request_user = self.request.user
        app_user_to_update = self.get_object()

        # make sure user to be updated is within the admin's authorization
        request_user_organizations = request_user.organization.get_descendants(
            include_self=True)
        if not request_user_organizations.filter(
                id=app_user_to_update.organization.id).exists():
            raise exceptions.ValidationError(
                "Invalid user id.")

        to_organization = data.get('organization', None)
        if to_organization and not request_user_organizations.filter(
                id=to_organization.id).exists():
            raise exceptions.ValidationError({
                "organization": "Invalid field."
            })

        # get locations available to the organization tree
        available_locations = Location.objects.filter(
            organization__in=request_user_organizations)

        # check if requested locations are not associated with the
        # organization
        invalid_locations = []
        locations = data.get('authorized_locations')
        for location in locations:
            if location not in available_locations:
                invalid_locations.append(location.id)

        if len(invalid_locations) != 0:
            raise serializers.ValidationError({
                "authorized_locations": (
                    "The locations {} are not associated with the "
                    "organization: {}".format(
                        invalid_locations, request_user.organization))})

        serializer.save()

    def _perform_update_by_employee(self, serializer):
        request_user = self.request.user
        app_user_to_update = self.get_object()

        # make sure employee is only able to update himself
        if request_user is not app_user_to_update:
            raise exceptions.PermissionDenied()

        serializer.save()
