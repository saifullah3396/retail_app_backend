"""
Defines the permissions used in this application.
"""

import copy

from core.permissions import AppDjangoModelPermissions
from core.utils import get_organization_user_model

ORGANIZATION_USER_MODEL = get_organization_user_model()


class OrganizationDjangoModelPermissions(AppDjangoModelPermissions):
    """
    Customizes the base DjangoModlePermissions class for organization
    user groups.
    """

    def has_permission(self, request, view):
        """
        Extends the django model permissions to also check permissions on the
        spec
        """
        if not super().has_permission(request, view):
            # if request.user does not have permissions, return false
            return False

        if not request.user.is_superuser:
            if not getattr(view, 'get_organization', False):
                # this requires the OrganizationMixin to be attached to the view
                # wherever we require the view to be restricted within
                # the organization
                raise PermissionError(
                    "Organization is required when using "
                    "OrganizationDjangoModelPermissions on a view. "
                    "Check whether you have attached the "
                    "GetOrganizationMixin attached to the {} view.".format(
                        view))

            organization = view.get_organization()
            try:
                # get the organization_user as link between organization and
                # user
                organization_user = organization.organization_users.get(
                    user=request.user)

                # get group permission of the organization user based on view
                # permissions
                queryset = self._queryset(view)
                perms = self.get_required_permissions(
                    request.method, queryset.model)
                return organization_user.has_perms(perms)
            except ORGANIZATION_USER_MODEL.DoesNotExist:
                # user does not exist inside the organization
                return False

        return True


class AppOrganizationsListCreateDestroyPermission(AppDjangoModelPermissions):
    """
    Permissions required on the AppOrganizationListCreateDestroyView
    """

    def __init__(self):
        self.perms_map = copy.deepcopy(self.perms_map)

        # add 'view' permission requirement on the view
        self.perms_map['DELETE'] = ['%(app_label)s.list_delete_%(model_name)s']
