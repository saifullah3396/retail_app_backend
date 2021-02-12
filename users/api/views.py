from core.utils import *
from core.views import *
from django.contrib.auth.models import Group
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import *
from rest_framework import filters, pagination
from rest_framework.generics import *
from rest_framework.response import Response
from rest_framework_jwt import authentication

from ..models import AppUser
from ..permissions import *
from .serializers import *


class AppUsersView:
    ordering_fields = ['id', 'username']
    filterset_fields = {
        'username': ['exact', 'icontains'],
    }

    def _get_model(self):
        """
        Returns the get queryset for staff users.
        """

        return AppUser

    def _order_by(self):
        """
        Returns the field with respect to which queries are to be ordered.
        """
        return 'first_name'

    def _get_organizations_tree(self, organization):
        """
        Returns the organizations descendents tree given the request type and
        organzation.
        """
        return self.organizations_tree_wrt_request[self.request.method](
            organization)

    def _get_users_in_organizations(self, organizations):
        """
        Returns all users which present within the given organizations
        queryset
        """
        return AppUser.objects.filter(organization__in=organizations)


class AppUsersListCreateDestroyView(
        CoreListCreateDestroyView, AppUsersView):
    """
    Defines the organizations list-create-destroy view.
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
        Returns the get queryset for staff users.
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
        print("_get_organization_admin_queryset")
        id_list = self._get_id_list()
        organizations_tree = self._get_organizations_tree(
            self.request.user.organization)

        # get all users in the organizations tree
        users_in_tree = self._get_users_in_organizations(
            organizations_tree)

        id_list = self._get_id_list()
        if id_list:
            return self._filter_objects_by_id_list(
                users_in_tree, id_list)

        return users_in_tree

        # get the organization tree of the user if its an admin
        if id_list:
            return self._filter_objects_by_id_list(
                organizations_tree, id_list
            )
        return organizations_tree

    def perform_create(self, serializer):
        """
        User creation is done through RegisterView from django rest-auth
        """

        return Response(status=status.HTTP_400_BAD_REQUEST)


    """
    Lists all app users. Can only be accessed by staff users.
    """
    queryset = AppUser.objects.all()
    serializer_class = AppUserSerializerAdminAccess
    permission_classes = (
        permissions.IsAuthenticated,
        permissions.IsAdminUser,)
    authentication_classes = [authentication.JSONWebTokenAuthentication]


class AppUserListAppUserAccess(APIView):
    """
    Lists all app users under organization of app admin. AppAdmin corresponds
    to organization or sub_organization admins.
    """
    serializer_class = AppUserSerializerAppUserAccess
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = [authentication.JSONWebTokenAuthentication]

    def send_user_list_response(self, request, user_list):
        serializer = self.serializer_class(
            user_list, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get(self, request):
        """
        Return the users under this user, for example if this user is an
        organization admin, this get request will return all organization
        users.
        """
        try:
            user_list = AppUser.objects.filter(
                organization=request.user.organization,
                authority__lte=request.user.authority).\
                exclude(id=request.user.id)
            if user_list:
                return self.send_user_list_response(request, user_list)
            else:
                return Response(status=status.HTTP_403_FORBIDDEN)
        except AppUser.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class AppUserDetailAppUserAccess(APIView):
    serializer_class = AppUserSerializerAppUserAccess
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = [authentication.JSONWebTokenAuthentication]

    def send_user_response(self, request, user):
        serializer = self.serializer_class(
            user, context={'request': request})
        return Response({"user": serializer.data}, status=status.HTTP_200_OK)

    def get(self, request, *args, **kwargs):
        """
        Return the user itself if <pk>=me else returns the user with
        input <pk> if the request user has authority.
        """
        if request.user.is_staff:
            self.serializer_class = AdminUserSerializerAdminAccess
        else:
            self.serializer_class = AppUserSerializerAppUserAccess

        pk = self.kwargs.get('pk')
        if pk == "me":
            return self.send_user_response(request, request.user)
        else:
            try:
                if request.user.sub_organization is None:
                    # if sub is none then its parent to sub
                    user = AppUser.objects.filter(
                        pk=pk,
                        organization=request.user.organization,
                        authority__lte=request.user.authority)
                else:
                    # if this does not work that means user > request.user
                    # so it is forbidden
                    user = AppUser.objects.filter(
                        pk=pk,
                        organization=request.user.organization,
                        sub_organization=request.user.sub_organization,
                        authority__lte=request.user.authority)
                if user:
                    return self.send_user_response(request, user[0])
                else:
                    return Response(status=status.HTTP_403_FORBIDDEN)
            except AppUser.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
