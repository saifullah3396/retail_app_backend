from rest_framework.generics import ListAPIView, RetrieveAPIView
from ..models import Organization
from .serializers import OrganizationSerializer


class OrganizationListView(ListAPIView):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer


class OrganizationDetailView(RetrieveAPIView):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
