# permissions.py
import copy

from core.permissions import AppDjangoModelPermissions, UserGroups
from django.contrib.auth.models import Group
from rest_framework import permissions

from .models import AppUser

USER_GROUP_PERMISSIONS = {
    UserGroups.ORGANIZATION_ADMIN_GROUP.name: {
        AppUser: ['add', 'change', 'view', 'delete'],
    },
    UserGroups.EMPLOYEE_GROUP.name: {
        AppUser: ['view', 'change'],
    },
}


class AppUsersListCreateDestroyPermission(AppDjangoModelPermissions):

    def __init__(self):
        self.perms_map = copy.deepcopy(self.perms_map)
        self.perms_map['GET'] = ['%(app_label)s.view_%(model_name)s']


class AppUsersRetrieveUpdateDestroyPermission(AppDjangoModelPermissions):

    def __init__(self):
        self.perms_map = copy.deepcopy(self.perms_map)
        self.perms_map['GET'] = ['%(app_label)s.view_%(model_name)s']
