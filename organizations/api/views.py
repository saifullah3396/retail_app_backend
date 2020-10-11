from rest_framework import permissions
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView
from ..models import Organization, SubOrganization
from .serializers import OrganizationSerializer, SubOrganizationSerializer


class OrganizationListView(ListAPIView):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = (permissions.AllowAny, )


class OrganizationDetailView(RetrieveAPIView):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = (permissions.AllowAny, )


class SubOrganizationListView(ListAPIView):
    queryset = SubOrganization.objects.all()
    serializer_class = SubOrganizationSerializer
    permission_classes = (permissions.AllowAny, )


class SubOrganizationDetailView(RetrieveAPIView):
    queryset = SubOrganization.objects.all()
    serializer_class = SubOrganizationSerializer
    permission_classes = (permissions.AllowAny, )
