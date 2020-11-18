from rest_framework import permissions, pagination, filters, status
from rest_framework_jwt import authentication
from rest_framework.generics import \
    GenericAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from ..models import Organization, SubOrganization
from .serializers import AdminOnlyOrganizationSerializer, AdminOnlySubOrganizationSerializer
from django.contrib.auth.mixins import UserPassesTestMixin


class PaginationConfig(pagination.PageNumberPagination):
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 100


class OrganizationsListCreateView(ListCreateAPIView):
    queryset = Organization.objects.all().order_by('name')
    serializer_class = OrganizationSerializer
    # permission_classes = (
    #     permissions.IsAuthenticated, permissions.IsAdminUser)
    authentication_classes = [authentication.JSONWebTokenAuthentication]
    pagination_class = PaginationConfig
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['id', 'name', 'desc']
    filterset_fields = {
        'name': ['exact', 'icontains'],
    }


class OrganizationsRUDView(RetrieveUpdateDestroyAPIView):
    serializer_class = OrganizationSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        OrganizationsRUDPermissions)
    authentication_classes = [authentication.JSONWebTokenAuthentication]
    pagination_class = PaginationConfig
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['id', 'name', 'desc']
    filterset_fields = {
        'name': ['exact', 'icontains'],
    }

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            # return all if it is super admin
            queryset = \
                Organization.objects.all().order_by('name')
            return queryset
        else:
            # else can only be an organization admin according to permissions
            # on the view. Return all sub-organizations under the users
            # organization
            queryset = \
                Organization.objects.filter(
                    id=user.organization.id).order_by('name')
            return queryset


class SubOrganizationsListCreateView(ListCreateAPIView):
    serializer_class = SubOrganizationSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        SubOrganizationsListCreatePermissions)
    authentication_classes = [authentication.JSONWebTokenAuthentication]
    pagination_class = PaginationConfig
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['id', 'name', 'desc', 'organization']
    filterset_fields = {
        'name': ['exact', 'icontains'],
        'organization': ['exact']
    }

    def send_user_response(self, request, user):
        serializer = self.serializer_class(
            user, context={'request': request})
        return Response({"user": serializer.data}, status=status.HTTP_200_OK)

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            # return all if it is super admin
            queryset = SubOrganization.objects.all().order_by('name')
            return queryset
        else:
            # else can only be an organization admin according to permissions
            # on the view. Return all sub-organizations under the users
            # organization
            queryset = SubOrganization.objects.filter(
                organization__id=user.organization.id).order_by('name')
            return queryset

    def create(self, request, *args, **kwargs):
        # check that the user is admin of the organization in which
        # sub-organization is requested
        if request.user.is_staff or \
                request.data['organization'] == \
                str(request.user.organization.id):
            return super(SubOrganizationsListCreateView, self).create(
                request, *args, *kwargs)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)



class SubOrganizationDetailView(UserPassesTestMixin, RetrieveAPIView):
    queryset = SubOrganization.objects.all()
    serializer_class = AdminOnlySubOrganizationSerializer
    permission_classes = (permissions.IsAuthenticated, permissions.IsAdminUser)
    authentication_classes = [authentication.TokenAuthentication]
