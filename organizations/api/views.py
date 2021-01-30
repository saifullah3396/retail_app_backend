from django.contrib.auth.models import Group
from rest_framework import \
    mixins, permissions, pagination, filters, status, exceptions
from rest_framework_jwt import authentication
from rest_framework.generics import (
    GenericAPIView,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    DestroyAPIView
)
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from ..models import Organization
from ..permissions import *
from .serializers import OrganizationSerializer
from backend.permissions import HasGroupPermission
from common.utils import *


class PaginationConfig(pagination.PageNumberPagination):
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 100


class OrganizationsListCreateDestroyView(ListCreateAPIView, DestroyAPIView):
    queryset = Organization.objects.none()  # Added for model permissions
    serializer_class = OrganizationSerializer
    permission_classes = (OrganizationListCreateDestroyPermission,)
    pagination_class = PaginationConfig
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['id', 'name', 'desc']
    filterset_fields = {
        'name': ['exact', 'icontains'],
    }
    method_to_tree_map = {
        'GET': lambda organization: organization.get_descendants(
            include_self=True),
        'DELETE': lambda organization: organization.get_descendants()
    }

    def get_queryset(self):
        return self._get_queryset().order_by('name')

    def _get_queryset(self):
        user = self.request.user
        if self.request.method == "GET":
            id_list = self.request.query_params.getlist('id')
        else:
            id_list = self.request.data.get('id')

        if user.is_staff:
            # return complete list if request user is a staff
            if id_list:
                return Organization.objects.filter(id__in=id_list)
            return Organization.objects.all()
        else:
            if is_organization_admin(user):
                organizations_tree = \
                    self.method_to_tree_map[self.request.method](
                        user.organization)

                # get the organization tree of the user if its an admin
                if id_list:
                    ids_in_tree = organizations_tree.filter(id__in=id_list)

                    # make sure all the given ids are inside the user
                    # descendents, otherwise return permission denied
                    if len(ids_in_tree) != len(id_list):
                        raise exceptions.PermissionDenied()
                    else:
                        return ids_in_tree

                return organizations_tree
            else:  # any other group cannot access lists
                raise exceptions.PermissionDenied()

    def perform_create(self, serializer):
        if self.request.user.is_staff:
            # okay to create anything for staff
            return \
                super(OrganizationsListCreateDestroyView, self).perform_create(
                    serializer)
        else:
            # an organization cannot be created by any user other than
            # super admin without a parent id
            if 'parent' not in self.request.data:
                raise exceptions.PermissionDenied()

            # see if the parent of requested organization is within descendents
            # of the current user. Current user can only be organization admin
            # as defined by group permissions so this should work
            descendents = self.request.user.organization.get_descendants(
                include_self=True)
            if not descendents.filter(id=self.request.data['parent']):
                raise exceptions.PermissionDenied()

            return \
                super(OrganizationsListCreateDestroyView, self).perform_create(
                    serializer)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_queryset()
        self.perform_destroy(instance)
        return Response(data={
            "msg": "Object(s) deleted successfully."},
            status=status.HTTP_200_OK)


class OrganizationsRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Organization.objects.none()  # Added for model permissions
    serializer_class = OrganizationSerializer
    permission_classes = (OrganizationRetrieveUpdateDestroyPermission,)
    pagination_class = PaginationConfig
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['id', 'name', 'desc']
    filterset_fields = {
        'name': ['exact', 'icontains'],
    }
    method_to_tree_map = {
        'GET': lambda organization: organization.get_descendants(
            include_self=True),
        'POST': lambda organization: organization.get_descendants(
            include_self=True),
        'PATCH': lambda organization: organization.get_descendants(
            include_self=True),
        'DELETE': lambda organization: organization.get_descendants()
    }

    def get_queryset(self):
        return self._get_queryset().order_by('name')

    def _get_queryset(self):
        user = self.request.user
        if user.is_staff:
            # return complete list if request user is a staff
            return Organization.objects.all()
        else:
            if is_organization_admin(user):
                organizations_tree = \
                    self.method_to_tree_map[self.request.method](
                        user.organization)
                return organizations_tree
            else:
                # any other group can only access object if its in the same
                # organization
                return Organization.objects.filter(
                    id=user.organization.id)

    def destroy(self, request, *args, **kwargs):
        resp = super(OrganizationsRetrieveUpdateDestroyView, self).destroy(
            request, *args, **kwargs)
        return Response(data={
            "msg": "Object(s) deleted successfully."},
            status=status.HTTP_200_OK)
