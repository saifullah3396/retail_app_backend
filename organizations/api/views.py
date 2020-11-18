from rest_framework import authentication, permissions
from rest_framework.generics import GenericAPIView, ListAPIView, RetrieveAPIView, CreateAPIView
from ..models import Organization, SubOrganization
from .serializers import AdminOnlyOrganizationSerializer, AdminOnlySubOrganizationSerializer
from django.contrib.auth.mixins import UserPassesTestMixin


class PaginationConfig(pagination.PageNumberPagination):
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 100



class OrganizationDetailView(UserPassesTestMixin, RetrieveAPIView):
    queryset = Organization.objects.all()
    serializer_class = AdminOnlyOrganizationSerializer
    permission_classes = (permissions.IsAuthenticated, permissions.IsAdminUser)
    authentication_classes = [authentication.TokenAuthentication]


class SubOrganizationListView(UserPassesTestMixin, ListAPIView):
    queryset = SubOrganization.objects.all()
    serializer_class = AdminOnlySubOrganizationSerializer
    permission_classes = (permissions.IsAuthenticated, permissions.IsAdminUser)
    authentication_classes = [authentication.TokenAuthentication]


class SubOrganizationDetailView(UserPassesTestMixin, RetrieveAPIView):
    queryset = SubOrganization.objects.all()
    serializer_class = AdminOnlySubOrganizationSerializer
    permission_classes = (permissions.IsAuthenticated, permissions.IsAdminUser)
    authentication_classes = [authentication.TokenAuthentication]
