import copy
from common.permissions import UserGroups, AppDjangoModelPermissions
from .models import Location

USER_GROUP_PERMISSIONS = {
    UserGroups.ORGANIZATION_ADMIN_GROUP.name: {
        Location: ['add', 'change', 'view', 'delete'],
    },
    UserGroups.EMPLOYEE_GROUP.name: {
        Location: ['change', 'view'],
    },
}


class LocationListCreateDestroyPermission(AppDjangoModelPermissions):

    def __init__(self):
        self.perms_map = copy.deepcopy(self.perms_map)
        self.perms_map['GET'] = ['%(app_label)s.view_%(model_name)s']


class LocationRetrieveUpdateDestroyPermission(AppDjangoModelPermissions):

    def __init__(self):
        self.perms_map = copy.deepcopy(self.perms_map)
        self.perms_map['GET'] = ['%(app_label)s.view_%(model_name)s']
