"""
Defines the permissions used in this application.
"""

import copy

from core.permissions import AppDjangoModelPermissions, UserGroups

from .models import Location

"""
Define the user group permissions for the Locations model.
"""
USER_GROUP_PERMISSIONS = {
    UserGroups.ORGANIZATION_ADMIN_GROUP.name: {
        Location: ['add', 'change', 'view', 'delete'],
    },
    UserGroups.EMPLOYEE_GROUP.name: {
        Location: ['view'],
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
