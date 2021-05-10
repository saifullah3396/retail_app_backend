"""
Defines the permissions used in this application.
"""

import copy

from core.permissions import AppDjangoModelPermissions, UserGroups

from .models import AppUser

USER_GROUP_PERMISSIONS = {
    UserGroups.ORGANIZATION_ADMIN_GROUP: {
        AppUser: ['add', 'change', 'view', 'delete'],
    },
    UserGroups.EMPLOYEE_GROUP: {
        AppUser: ['view', 'change'],
    },
}


class AppUsersListCreateDestroyPermission(AppDjangoModelPermissions):
    """
    Permissions required on the AppUserListCreateDestroyView
    """

    def __init__(self):
        self.perms_map = copy.deepcopy(self.perms_map)
        self.perms_map['GET'] = ['%(app_label)s.view_%(model_name)s']


class AppUsersRetrieveUpdateDestroyPermission(AppDjangoModelPermissions):
    """
    Permissions required on the AppUserRetrieveUpdateDestroyView
    """

    def __init__(self):
        self.perms_map = copy.deepcopy(self.perms_map)
        self.perms_map['GET'] = ['%(app_label)s.view_%(model_name)s']
