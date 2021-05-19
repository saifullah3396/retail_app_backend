"""
Defines the REST API views for users models.
"""


from allauth.account.models import EmailAddress

from core import views
from core.permissions import AppDjangoModelPermissions
from core.utils import filter_objects_by_lookup_list, get_lookup_list
from users.api.app_user.permissions import AppUsersListCreateDestroyPermission
from users.api.app_user.serializers import (AppUserCreateSerializer,
                                            AppUserListSerializer,
                                            AppUserRetrieveSerializer,
                                            AppUserUpdateSerializer)
from users.models import AppUser


class AppUsersListCreateDestroyView(
        views.CoreListAPIView,
        # views.CoreCreateAPIView, create not allowed
        views.CoreListDestroyAPIView):
    """
    Defines the list-create-destroy view.
    """

    queryset = AppUser.objects.none()
    permission_classes = (AppUsersListCreateDestroyPermission,)
    ordering_fields = ['id', 'username']
    filterset_fields = {
        'username': ['exact', 'icontains'],
    }
    order_by = 'username'

    # define serializers
    list_serializer = AppUserListSerializer
    create_serializer = AppUserCreateSerializer

    def _get_list_queryset_user(self):
        """
        Returns the list of all users except staff or super users
        """
        return self.model.objects.exclude(
            is_staff=True, is_superuser=True)


class AppUsersRetrieveUpdateDestroyView(
        views.CoreRetrieveAPIView,
        views.CoreUpdateAPIView,
        views.CoreDestroyAPIView):
    """
    Defines the retrieve-update-destroy view.
    """

    queryset = AppUser.objects.none()  # Added for model permissions
    permission_classes = (AppDjangoModelPermissions,)

    # define serializers
    retrieve_serializer = AppUserRetrieveSerializer
    update_serializer = AppUserUpdateSerializer

    def get_queryset(self):
        """
        Implements the get_queryset function. Any final modifications to the
        query set are made here.
        """
        if self.kwargs.get('pk') == "self":
            self.kwargs['pk'] = self.request.user.id
        return super().get_queryset()

    def _get_retrieve_queryset_user(self):
        """
        Returns the list with user himself
        """
        return self.model.objects.filter(id=self.request.user.id)

    def perform_destroy(self, instance):
        # also delete associated email address object
        try:
            email_address = EmailAddress.objects.get(user=instance)
            email_address.delete()
        except EmailAddress.DoesNotExist:
            pass

        super().perform_destroy(instance)
