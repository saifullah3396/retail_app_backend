"""
Defines the permissions used in this application.
"""

import copy

from core.permissions import AppDjangoModelPermissions, UserGroups

from .models import DeepstreamServer

"""
Define the user group permissions for the Server model.
"""
USER_GROUP_PERMISSIONS = {
    # add organization admin permissions on DeepstreamServer
    UserGroups.ORGANIZATION_ADMIN_GROUP.name: {
        DeepstreamServer: ['add', 'change', 'view', 'delete'],
    },

    # add employee permissions on DeepstreamServer
    UserGroups.EMPLOYEE_GROUP.name: {
        DeepstreamServer: ['view'],
    },
}


class DeepstreamServersListCreateDestroyPermission(AppDjangoModelPermissions):
    """
    Permissions required on the DeepstreamServersListCreateDestroyView
    """

    def __init__(self):
        self.perms_map = copy.deepcopy(self.perms_map)

        # add 'view' permission requirement on the view
        self.perms_map['GET'] = ['%(app_label)s.view_%(model_name)s']


class DeepstreamServersRetrieveUpdateDestroyPermission(AppDjangoModelPermissions):
    """
    Permissions required on the DeepstreamServerCreateDestroyView
    """

    def __init__(self):
        self.perms_map = copy.deepcopy(self.perms_map)

        # Add 'view' permission requirement on the view
        self.perms_map['GET'] = ['%(app_label)s.view_%(model_name)s']
