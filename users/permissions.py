# pylint: disable=missing-module-docstring
import copy

from core.permissions import AppDjangoModelPermissions, UserGroups

from .models import AppUser

USER_GROUP_PERMISSIONS = {
    UserGroups.ORGANIZATION_ADMIN_GROUP.name: {
        AppUser: ['add', 'change', 'view', 'delete'],
    },
    UserGroups.EMPLOYEE_GROUP.name: {
        AppUser: ['view', 'change'],
    },
}

# pylint: disable=missing-class-docstring


class AppUsersListCreateDestroyPermission(AppDjangoModelPermissions):

    def __init__(self):
        self.perms_map = copy.deepcopy(self.perms_map)
        self.perms_map['GET'] = ['%(app_label)s.view_%(model_name)s']


class AppUsersRetrieveUpdateDestroyPermission(AppDjangoModelPermissions):

    def __init__(self):
        self.perms_map = copy.deepcopy(self.perms_map)
        self.perms_map['GET'] = ['%(app_label)s.view_%(model_name)s']
