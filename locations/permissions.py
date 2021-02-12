"""
Defines the permissions used in this application.
"""

import copy

from core.permissions import AppDjangoModelPermissions, UserGroups

from .models import Location, Floor, Block

"""
Define the user group permissions for the models of this application.
"""
USER_GROUP_PERMISSIONS = {
    UserGroups.ORGANIZATION_ADMIN_GROUP.name: {
        Location: ['add', 'change', 'view', 'delete'],
        Floor: ['add', 'change', 'view', 'delete'],
        Block: ['add', 'change', 'view', 'delete']
    },
    UserGroups.EMPLOYEE_GROUP.name: {
        Location: ['view'],
        Floor: ['view'],
        Block: ['view']
    },
}


class LocationsListCreateDestroyPermission(AppDjangoModelPermissions):
    """
    Permissions required on the LocationsListCreateDestroyView
    """

    def __init__(self):
        self.perms_map = copy.deepcopy(self.perms_map)
        self.perms_map['GET'] = ['%(app_label)s.view_%(model_name)s']


class LocationsRetrieveUpdateDestroyPermission(AppDjangoModelPermissions):
    """
    Permissions required on the LocationsRetrieveUpdateDestroyView
    """

    def __init__(self):
        self.perms_map = copy.deepcopy(self.perms_map)
        self.perms_map['GET'] = ['%(app_label)s.view_%(model_name)s']


class FloorsListCreateDestroyPermission(AppDjangoModelPermissions):
    """
    Permissions required on the FloorsListCreateDestroyView
    """

    def __init__(self):
        self.perms_map = copy.deepcopy(self.perms_map)
        self.perms_map['GET'] = ['%(app_label)s.view_%(model_name)s']


class FloorsRetrieveUpdateDestroyPermission(AppDjangoModelPermissions):
    """
    Permissions required on the FloorsRetrieveUpdateDestroyView
    """

    def __init__(self):
        self.perms_map = copy.deepcopy(self.perms_map)
        self.perms_map['GET'] = ['%(app_label)s.view_%(model_name)s']


class BlocksListCreateDestroyPermission(AppDjangoModelPermissions):
    """
    Permissions required on the BlocksListCreateDestroyView
    """

    def __init__(self):
        self.perms_map = copy.deepcopy(self.perms_map)
        self.perms_map['GET'] = ['%(app_label)s.view_%(model_name)s']


class BlocksRetrieveUpdateDestroyPermission(AppDjangoModelPermissions):
    """
    Permissions required on the BlocksRetrieveUpdateDestroyView
    """

    def __init__(self):
        self.perms_map = copy.deepcopy(self.perms_map)
        self.perms_map['GET'] = ['%(app_label)s.view_%(model_name)s']
