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
    organizations_tree_map = {
        'GET': lambda organization: organization.get_descendants(
            include_self=True),
        'DELETE': lambda organization: organization.get_descendants(
            include_self=True)
    }

    def get_organizations_tree(self, organization):
        return self.organizations_tree_map[self.request.method](organization)

    def get_locations_in_organizations(self, organizations):
        return Location.objects.filter(organization__in=organizations)

    def filter_queryset_by_id_list(self, query_set, id_list):
        return query_set.filter(id__in=id_list)

    def exclude_queryset_by_id_list(self, query_set, id_list):
        return query_set.exclude(id__in=id_list)

    def filter_locations_by_id_list(self, locations, id_list):
        # filter locations by id list
        filtered_locations = self.filter_queryset_by_id_list(
            locations, id_list)

        # make sure all the given ids are inside filtered locations,
        # otherwise raise a validation error
        if len(filtered_locations) != len(id_list):
            raise exceptions.NotFound(
                {
                    'id': 'The following requested ids are invalid: {}'.format(
                        self.exclude_queryset_by_id_list(
                            locations, id_list).values_list('id', flat=True))
                })
        return filtered_locations

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
                return self.filter_queryset_by_id_list(
                    Location.objects, id_list)
            return Location.objects.all()
        elif is_organization_admin(user):
            # get all organizations under this one
            organizations_tree = self.get_organizations_tree(
                user.organization)

            # get all locations in the tree
            locations_in_tree = self.get_locations_in_organizations(
                organizations_tree)

            if id_list:
                return self.filter_locations_by_id_list(
                    locations_in_tree, id_list)

            return locations_in_tree
        else:
            # any other group can only get locations that are authorized
            authorized_locations = user.authorized_locations.all()
            if id_list:
                return self.filter_locations_by_id_list(
                    authorized_locations, id_list)
            return authorized_locations

    def perform_create(self, serializer):
        user = self.request.user
        data = self.request.data

        if user.is_staff:
            # okay to create anything for staff
            return \
                super(LocationsListCreateDestroyView, self).perform_create(
                    serializer)
        elif is_organization_admin(user):
            # see if the organization of requested location is within
            # descendents of this admin
            descendents = user.organization.get_descendants(
                include_self=True)
            if not descendents.filter(id=data['organization']):
                raise exceptions.ValidationError(
                    {
                        'organization': 'Invalid value.'
                    })

            return \
                super(LocationsListCreateDestroyView, self).perform_create(
                    serializer)
        else:
            # no other user group can create a location
            raise exceptions.PermissionDenied()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_queryset()
        if not instance:
            raise exceptions.NotFound()
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

    organizations_tree_map = {
        'GET': lambda organization: organization.get_descendants(
            include_self=True),
        'POST': lambda organization: organization.get_descendants(
            include_self=True),
        'PATCH': lambda organization: organization.get_descendants(
            include_self=True),
        'DELETE': lambda organization: organization.get_descendants(
            include_self=True
        )
    }

    def get_organizations_tree(self, organization):
        return self.organizations_tree_map[self.request.method](organization)

    def get_locations_in_organizations(self, organizations):
        return Location.objects.filter(organization__in=organizations)

    def get_queryset(self):
        return self._get_queryset().order_by('name')

    def _get_queryset(self):
        user = self.request.user
        if user.is_staff:
            # return complete list if request user is a staff
            return Location.objects.all()
        elif is_organization_admin(user):
            # get all organizations under this one
            organizations_tree = self.get_organizations_tree(
                user.organization)

            # get all locations in the tree
            locations_in_tree = self.get_locations_in_organizations(
                organizations_tree)
            return locations_in_tree
        else:
            # any other group can only get locations that are authorized
            authorized_locations = user.authorized_locations.all()
            return authorized_locations

    def destroy(self, request, *args, **kwargs):
        resp = super(LocationsRetrieveUpdateDestroyView, self).destroy(
            request, *args, **kwargs)
        return Response(data={
            "msg": "Object(s) deleted successfully."},
            status=status.HTTP_200_OK)
