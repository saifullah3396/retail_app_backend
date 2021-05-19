"""
Defines the REST API views for organizations models.
"""


from app_organizations.api.organization.serializers import (
    AppOrganizationCreateSerializer, AppOrganizationListSerializer,
    AppOrganizationRetrieveSerializer, AppOrganizationUpdateSerializer,
    AppOrganizationUserCreateSerializer, AppOrganizationUserListSerializer,
    AppOrganizationUserRetrieveSerializer, AppOrganizationUserUpdateSerializer)
from app_organizations.models import AppOrganization, AppOrganizationUser
from app_organizations.permissions import \
    AppOrganizationsListCreateDestroyPermission
from core import views
from core.permissions import AppDjangoModelPermissions
from app_organizations.permissions import OrganizationDjangoModelPermissions
from app_organizations.views import (BaseOrganizationListGetQuerySet,
                                     BaseOrganizationRetrieveGetQuerySet,
                                     GetOrganizationMixin)


class AppOrganizationsListCreateDestroyView(
        views.CoreListAPIView,
        views.CoreCreateAPIView,
        views.CoreListDestroyAPIView):

    """
    Defines the organizations list-create-destroy view.
    """

    queryset = AppOrganization.objects.none()
    permission_classes = (AppOrganizationsListCreateDestroyPermission,)
    ordering_fields = ['id', 'name']
    order_by = 'name'
    filterset_fields = {
        'name': ['exact', 'icontains'],
    }
    list_serializer = AppOrganizationListSerializer
    create_serializer = AppOrganizationCreateSerializer

    def _get_list_queryset_user(self):
        """
        Returns the list of all users except staff or super users
        """
        return self.model.objects.filter(users=self.request.user)


class AppOrganizationsRetrieveUpdateDestroyView(
        views.CoreRetrieveAPIView,
        views.CoreUpdateAPIView,
        views.CoreDestroyAPIView,
        GetOrganizationMixin):
    """
    Defines the organizations retrieve-update-destroy view.
    """

    lookup_url_kwarg = 'organization_pk'
    queryset = AppOrganization.objects.none()  # Added for model permissions
    permission_classes = (OrganizationDjangoModelPermissions,)
    retrieve_serializer = AppOrganizationRetrieveSerializer
    update_serializer = AppOrganizationUpdateSerializer

    def _get_retrieve_queryset_user(self):
        """
        Get all organizations in which the user is present.
        """

        return self.model.objects.filter(users=self.request.user)


class AppOrganizationUsersListCreateDestroyView(
        views.CoreListAPIView,
        views.CoreCreateAPIView,
        views.CoreListDestroyAPIView,
        BaseOrganizationListGetQuerySet):

    """
    Defines the organization users list-create-destroy view.
    """

    queryset = AppOrganizationUser.objects.none()
    permission_classes = (OrganizationDjangoModelPermissions,)
    # list destroy is not allowed
    ordering_fields = ['id']
    order_by = 'id'
    filterset_fields = {
        'id': ['exact', 'icontains'],
    }
    list_serializer = AppOrganizationUserListSerializer
    create_serializer = AppOrganizationUserCreateSerializer


class AppOrganizationUsersRetrieveUpdateDestroyView(
        views.CoreRetrieveAPIView,
        views.CoreUpdateAPIView,
        views.CoreDestroyAPIView,
        BaseOrganizationRetrieveGetQuerySet):
    """
    Defines the organization users retrieve-update-destroy view.
    """

    queryset = AppOrganizationUser.objects.none()  # Added for model permissions
    permission_classes = (OrganizationDjangoModelPermissions,)
    retrieve_serializer = AppOrganizationUserRetrieveSerializer
    update_serializer = AppOrganizationUserUpdateSerializer
