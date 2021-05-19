"""
Defines the REST API views for users models.
"""


from core import views
from core.permissions import AppDjangoModelPermissions
from user_auth.api.group.serializers import (AddUserSerializer,
                                             GroupCreateSerializer,
                                             GroupListSerializer,
                                             GroupRetrieveSerializer,
                                             GroupUpdateSerializer,
                                             RemoveUserSerializer)
from user_auth.models import UserGroup


class GroupsListCreateDestroyView(
        views.CoreListAPIView,
        views.CoreCreateAPIView,
        views.CoreListDestroyAPIView):
    """
    Defines the list-create-destroy view.
    """

    lookup_field = 'name'
    lookup_url_kwarg = 'name'
    queryset = UserGroup.objects.none()
    permission_classes = (AppDjangoModelPermissions,)
    ordering_fields = ['name', 'authority']
    order_by = 'authority'
    # groups filtering with name conflicts with its lookup url name
    # filterset_fields = {
    #     'name': ['exact', 'icontains'],
    # }

    # define serializers
    list_serializer = GroupListSerializer
    create_serializer = GroupCreateSerializer

    def _get_list_queryset_user(self):
        """
        Returns the list of groups
        """
        # 0 highest authority
        return self.model.objects.filter(
            authority__gte=self.request.user.highest_group.authority)


class GroupsRetrieveUpdateDestroyView(
        views.CoreRetrieveAPIView,
        views.CoreUpdateAPIView,
        views.CoreDestroyAPIView):
    """
    Defines the retrieve-update-destroy view.
    """

    lookup_field = 'name'
    lookup_url_kwarg = 'name'
    queryset = UserGroup.objects.none()  # Added for model permissions
    permission_classes = (AppDjangoModelPermissions,)

    # define serializers
    retrieve_serializer = GroupRetrieveSerializer
    update_serializer = GroupUpdateSerializer

    def _get_retrieve_queryset_user(self):
        """
        Returns the list of groups within authority
        """
        # return all groups that are lower in authority than the user's own group
        # 0 highest authority
        return self.model.objects.filter(
            authority__gte=self.request.user.highest_group.authority)


class AddRemoveUserView(
        views.CoreUpdateAPIView,
        views.CoreRetrieveGetQueryset):
    """
    Defines the view for adding users to the group
    """

    lookup_field = 'name'
    lookup_url_kwarg = 'name'
    queryset = UserGroup.objects.none()  # Added for model permissions
    permission_classes = (AppDjangoModelPermissions,)

    def _get_retrieve_queryset_user(self):
        """
        Returns the list of groups within authority
        """
        # return all groups that are lower in authority than the user's own group
        # 0 highest authority
        return self.model.objects.filter(
            authority__gte=self.request.user.highest_group.authority)


class AddUserView(AddRemoveUserView):
    """
    Defines the view for adding users to the group
    """

    update_serializer = AddUserSerializer


class RemoveUserView(AddRemoveUserView):
    """
    Defines the view for removing users from the group
    """

    update_serializer = RemoveUserSerializer
