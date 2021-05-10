"""
Defines the permissions used in this application.
"""

import copy

from core.permissions import AppDjangoModelPermissions, UserGroups

from .models import MeasurementFrame

# Define the user group permissions for the models of this application.
USER_GROUP_PERMISSIONS = {
    UserGroups.ORGANIZATION_ADMIN_GROUP: {
        MeasurementFrame: ['add', 'change', 'view', 'delete'],
    },
    UserGroups.EMPLOYEE_GROUP: {
        MeasurementFrame: ['view'],
    },
}


class MeasurementFramesListCreateDestroyPermission(AppDjangoModelPermissions):
    """
    Permissions required on the MeasurementFrameListCreateDestroyView
    """

    def __init__(self):
        self.perms_map = copy.deepcopy(self.perms_map)
        self.perms_map['GET'] = ['%(app_label)s.view_%(model_name)s']


class MeasurementFramesRetrieveUpdateDestroyPermission(
        AppDjangoModelPermissions):
    """
    Permissions required on the MeasurementFrameRetrieveUpdateDestroyView
    """

    def __init__(self):
        self.perms_map = copy.deepcopy(self.perms_map)
        self.perms_map['GET'] = ['%(app_label)s.view_%(model_name)s']
