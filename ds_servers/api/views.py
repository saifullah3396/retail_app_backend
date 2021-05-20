"""
Defines the REST api views for deepstream servers.
"""

from core import views
from core.permissions import AppDjangoModelPermissions
from ds_servers.api.serializers import (DSServerCreateSerializer,
                                        DSServerListSerializer,
                                        DSServerRetrieveSerializer,
                                        DSServerUpdateSerializer)
from ds_servers.models import DSServer


class DSServersListCreateDestroyView(
        views.CoreListAPIView,
        views.CoreCreateAPIView,
        views.CoreListDestroyAPIView):

    """
    Defines the DSServers list-create-destroy view.
    """

    queryset = DSServer.objects.none()
    permission_classes = (AppDjangoModelPermissions,)
    ordering_fields = ['id', 'ip_addr']
    filterset_fields = {
        'ip_addr': ['exact', 'icontains']
    }
    order_by = 'id'
    list_serializer = DSServerListSerializer
    create_serializer = DSServerCreateSerializer


class DSServersRetrieveUpdateDestroyView(
        views.CoreRetrieveAPIView,
        views.CoreUpdateAPIView,
        views.CoreDestroyAPIView):
    """
    Defines the DSServers list-create-destroy view.
    """

    queryset = DSServer.objects.none()  # Added for model permissions
    permission_classes = (AppDjangoModelPermissions,)
    retrieve_serializer = DSServerRetrieveSerializer
    update_serializer = DSServerUpdateSerializer
