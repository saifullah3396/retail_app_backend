from django.contrib.auth.models import Group
from rest_framework import *
from rest_framework import pagination, filters
from rest_framework_jwt import authentication
from rest_framework.generics import *
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from ..models import Location
from ..permissions import *
from .serializers import *
from core.utils import *


class PaginationConfig(pagination.PageNumberPagination):
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 100


class LocationsListCreateDestroyView(ListCreateAPIView, DestroyAPIView):
    queryset = Location.objects.none()  # Added for model permissions
    serializer_class = LocationSerializer
    permission_classes = (LocationListCreateDestroyPermission,)
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
            print('user.is_staff')
            # return complete list if request user is a staff
            if id_list:
                return Location.objects.filter(id__in=id_list)
            return Location.objects.all()
        else:
            print(user.groups.all())
            if is_organization_admin(user):
                print('is_organization_admin')
                organizations_tree = \
                    self.method_to_tree_map[self.request.method](
                        user.organization)

                locations_in_tree = \
                    Location.objects.filter(
                        organization__in=organizations_tree)

                print('org tree', organizations_tree)
                print('locations_in_tree', locations_in_tree)

                # get the organization tree of the user if its an admin
                if id_list:
                    ids_in_tree = locations_in_tree.filter(id__in=id_list)

                    # make sure all the given ids are inside the user
                    # descendents, otherwise return permission denied
                    if len(ids_in_tree) != len(id_list):
                        raise exceptions.PermissionDenied()
                    else:
                        return ids_in_tree

                return locations_in_tree
            else:  # any other group can only get locations that are authorized
                return user.authorized_locations.all()

    def perform_create(self, serializer):
        if self.request.user.is_staff:
            # okay to create anything for staff
            return \
                super(LocationListCreateDestroyView, self).perform_create(
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
                super(LocationListCreateDestroyView, self).perform_create(
                    serializer)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_queryset()
        self.perform_destroy(instance)
        return Response(data={
            "msg": "Object(s) deleted successfully."},
            status=status.HTTP_200_OK)


class LocationsRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Location.objects.none()  # Added for model permissions
    serializer_class = LocationDetailSerializer
    permission_classes = (LocationRetrieveUpdateDestroyPermission,)
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
            return Location.objects.all()
        else:
            if is_organization_admin(user):
                organizations_tree = \
                    self.method_to_tree_map[self.request.method](
                        user.organization)
                locations_in_tree = \
                    Location.objects.filter(
                        organization__in=organizations_tree)
                return locations_in_tree
            else:  # any other group can only get locations that are authorized
                return user.authorized_locations.all()

    def destroy(self, request, *args, **kwargs):
        resp = super(LocationRetrieveUpdateDestroyView, self).destroy(
            request, *args, **kwargs)
        return Response(data={
            "msg": "Object(s) deleted successfully."},
            status=status.HTTP_200_OK)
