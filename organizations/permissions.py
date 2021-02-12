"""
Defines the permissions used in this application.
"""

import copy

from core.permissions import AppDjangoModelPermissions, UserGroups

from .models import Organization

"""
Define the user group permissions for the Organization model.
"""
USER_GROUP_PERMISSIONS = {
    # add organization admin permissions on Organization
    UserGroups.ORGANIZATION_ADMIN_GROUP.name: {
        Organization: ['add', 'change', 'view', 'delete'],
    },

    # add employee permissions on Organization
    UserGroups.EMPLOYEE_GROUP.name: {
        Organization: ['view'],
    },
}


class OrganizationsListCreateDestroyPermission(AppDjangoModelPermissions):
    """
    Permissions required on the OrganizationListCreateDestroyView
    """

    def __init__(self):
        self.perms_map = copy.deepcopy(self.perms_map)

        # add 'view' permission requirement on the view
        self.perms_map['GET'] = ['%(app_label)s.view_%(model_name)s']


class OrganizationsRetrieveUpdateDestroyPermission(AppDjangoModelPermissions):
    """
    Permissions required on the OrganizationListCreateDestroyView
    """

    def __init__(self):
        self.perms_map = copy.deepcopy(self.perms_map)

        # add 'view' permission requirement on the view
        self.perms_map['GET'] = ['%(app_label)s.view_%(model_name)s']
