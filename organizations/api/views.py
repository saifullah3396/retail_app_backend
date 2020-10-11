from rest_framework.generics import ListAPIView, RetrieveAPIView
from ..models import Organization, SubOrganization
from .serializers import OrganizationSerializer, SubOrganizationSerializer


class OrganizationListView(ListAPIView):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer


class OrganizationDetailView(RetrieveAPIView):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer


class SubOrganizationListView(ListAPIView):
    queryset = SubOrganization.objects.all()
    serializer_class = SubOrganizationSerializer


class SubOrganizationDetailView(RetrieveAPIView):
    queryset = SubOrganization.objects.all()
    serializer_class = SubOrganizationSerializer
