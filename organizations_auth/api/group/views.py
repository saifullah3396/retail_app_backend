"""
Defines the REST API views for users models.
"""


from core import views
from app_organizations.api.group.serializers import (
    AddUserSerializer, OrganizationGroupCreateSerializer,
    OrganizationGroupListSerializer, OrganizationGroupRetrieveSerializer,
    OrganizationGroupUpdateSerializer, RemoveUserSerializer)
from app_organizations.models import OrganizationGroup
from app_organizations.permissions import OrganizationDjangoModelPermissions
from app_organizations.views import (BaseOrganizationListGetQuerySet,
                                     BaseOrganizationRetrieveGetQuerySet)


class OrganizationGroupsListCreateDestroyView(
        views.CoreListAPIView,
        views.CoreCreateAPIView,
        views.CoreListDestroyAPIView,
        BaseOrganizationListGetQuerySet):
    """
    Defines the list-create-destroy view.
    """

    lookup_field = 'name'
    lookup_url_kwarg = 'name'
    queryset = OrganizationGroup.objects.none()
    permission_classes = (OrganizationDjangoModelPermissions,)
    ordering_fields = ['name', 'authority']
    order_by = 'authority'
    # groups filtering with name conflicts with its lookup url name
    # filterset_fields = {
    #     'name': ['exact', 'icontains'],
    # }
    list_serializer = OrganizationGroupListSerializer
    create_serializer = OrganizationGroupCreateSerializer


class OrganizationGroupsRetrieveUpdateDestroyView(
        views.CoreRetrieveAPIView,
        views.CoreUpdateAPIView,
        views.CoreDestroyAPIView,
        BaseOrganizationRetrieveGetQuerySet):
    """
    Defines the retrieve-update-destroy view.
    """

    lookup_field = 'name'
    lookup_url_kwarg = 'name'
    queryset = OrganizationGroup.objects.none()  # Added for model permissions
    permission_classes = (OrganizationDjangoModelPermissions,)

    retrieve_serializer = OrganizationGroupRetrieveSerializer
    update_serializer = OrganizationGroupUpdateSerializer


class AddUserView(
        views.CoreUpdateAPIView,
        BaseOrganizationRetrieveGetQuerySet):
    """
    Defines the view for adding users to the group
    """

    lookup_field = 'name'
    lookup_url_kwarg = 'name'
    queryset = OrganizationGroup.objects.none()  # Added for model permissions
    permission_classes = (OrganizationDjangoModelPermissions,)
    update_serializer = AddUserSerializer


class RemoveUserView(
        views.CoreUpdateAPIView,
        BaseOrganizationRetrieveGetQuerySet):
    """
    Defines the view for removing users from the group
    """

    lookup_field = 'name'
    lookup_url_kwarg = 'name'
    queryset = OrganizationGroup.objects.none()  # Added for model permissions
    permission_classes = (OrganizationDjangoModelPermissions,)
    update_serializer = RemoveUserSerializer
