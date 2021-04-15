"""
Defines the REST API views for users models.
"""

from rest_framework import exceptions, serializers, status
from rest_framework.response import Response

from core.permissions import UserGroups
from core.views import CoreListCreateDestroyView, CoreRetrieveUpdateDestroyView
from locations.models import Location
from users.api.serializers import (AppUserDetailRetrieveSerializer,
                                   AppUserDetailUpdateSerializer,
                                   AppUserListSerializer)
from users.models import AppUser
from users.permissions import (AppUsersListCreateDestroyPermission,
                               AppUsersRetrieveUpdateDestroyPermission)


class AppUsersView:
    """
    Defines the base class for the organizations rest api views.
    """

    ordering_fields = ['id', 'username']
    filterset_fields = {
        'username': ['exact', 'icontains'],
    }
    organizations_tree_wrt_request = []

    def _get_model(self):
        """
        Returns the view model.
        """

        return AppUser

    def _order_by(self):
        """
        Returns the field with respect to which queries are to be ordered.
        """
        return 'first_name'

    def _get_users_in_organizations(self, organizations):
        """
        Returns all users which present within the given organizations
        queryset
        """
        return AppUser.objects.filter(organization__in=organizations)


class AppUsersListCreateDestroyView(
        CoreListCreateDestroyView, AppUsersView):
    """
    Defines the users list-create-destroy view.
    """

    queryset = AppUser.objects.none()
    serializer_class = AppUserListSerializer
    permission_classes = (AppUsersListCreateDestroyPermission,)

    # Define the mapping from request type to query that returns the
    # organizations tree that is used in the requests. For example, in DELETE
    # requests, organization does not include itself while in GET it does
    organizations_tree_wrt_request = {
        'GET': lambda organization: organization.get_descendants(
            include_self=True),
        'DELETE': lambda organization: organization.get_descendants()
    }

    def _get_model(self):
        """
        Returns the view model.
        """
        return AppUsersView._get_model(self)

    def _order_by(self):
        """
        Returns the field with respect to which queries are to be ordered.
        """
        return AppUsersView._order_by(self)

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
        return {}

    def _get_organization_admin_queryset(self):
        """
        For an organization admin, all the users in the organizations below
        organization are returned. In case a list of ids is provided, the
        users are filtered further by ids.
        """
        id_list = self._get_id_list()
        organizations_tree = \
            self.organizations_tree_wrt_request[self.request.method](
                self.request.user.organization)

        # get all users in the organizations tree
        users_in_tree = self._get_users_in_organizations(
            organizations_tree)

        id_list = self._get_id_list()
        if id_list:
            return self._filter_objects_by_id_list(
                users_in_tree, id_list)

        return users_in_tree

    def perform_create(self):
        """
        User creation is done through RegisterView from django rest-auth
        """

        return Response(status=status.HTTP_400_BAD_REQUEST)


class AppUsersRetrieveUpdateDestroyView(
        CoreRetrieveUpdateDestroyView, AppUsersView):
    """
    Defines the organizations retrieve-update-destroy view.
    """

    queryset = AppUser.objects.none()  # Added for model permissions
    permission_classes = (AppUsersRetrieveUpdateDestroyPermission,)

    def get_serializer_class(self):
        """
        Returns separate serializer classes for get/put/patch requests.
        """

        if self.request.method == 'GET':
            return AppUserDetailRetrieveSerializer
        if self.request.method == 'PUT' or self.request.method == 'PATCH':
            return AppUserDetailUpdateSerializer
        return AppUserDetailRetrieveSerializer

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

    def _get_model(self):
        """
        Returns the view model.
        """

        return AppUsersView._get_model(self)

    def _get_queryset(self):
        """
        Implements the customized get_queryset functionalty.
        """
        primary_key = self.kwargs.get('pk')
        if primary_key == "self":
            self.kwargs['pk'] = self.request.user.id
            return self._get_model().objects.filter(id=self.request.user.id)
        else:
            return super()._get_queryset()

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
                self._perform_update_by_organization_admin,
            UserGroups.EMPLOYEE_GROUP:
                self._perform_update_by_employee
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
        users_in_tree = self._get_users_in_organizations(
            organizations_tree)
        return users_in_tree

    def _get_employee_queryset(self):
        """
        Returns the get_queryset for employee user group
        """
        return self._get_users_in_organizations(
            self.request.user.organization)

    def _perform_update_by_organization_admin(self, serializer):
        data = serializer.validated_data
        request_user = self.request.user
        app_user_to_update = self.get_object()

        # make sure user to be updated is within the admin's authorization
        request_user_organizations = request_user.organization.get_descendants(
            include_self=True)
        if app_user_to_update.organization not in request_user_organizations:
            raise exceptions.ValidationError(
                "Invalid user id.")

        to_organization = data.get('organization', None)
        if to_organization is not None and \
                to_organization not in request_user_organizations:
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
        data = serializer.validated_data()
        request_user = self.request.user
        app_user_to_update = self.get_object()

        # make sure employee is only able to update himself
        if request_user is not app_user_to_update:
            raise exceptions.PermissionDenied()

        # make sure employee cannot update the organization,
        # authorized_locations and the user groups
        error = {}
        request_invalid = False
        invalid_inputs = ['authorized_locations', 'organizations', 'group']
        for field in invalid_inputs:
            if data.get(field, None) is not None:
                error[field] = "Not authorized to update this field."
                request_invalid = True

        if request_invalid:
            raise exceptions.ValidationError(error)

        serializer.save()
