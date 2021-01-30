import copy
from rest_framework import permissions
from backend.settings import UserGroups
from .models import Organization

USER_GROUP_PERMISSIONS = {
    UserGroups.ORGANIZATION_ADMIN_GROUP.name: {
        Organization: ['add', 'change', 'view', 'delete'],
    },
    UserGroups.EMPLOYEE_GROUP.name: {
        Organization: ['view'],
    },
}


class AppDjangoModelPermissions(permissions.DjangoModelPermissions):

    def _queryset(self, view):
        assert hasattr(view, 'get_queryset') \
            or getattr(view, 'queryset', None) is not None, (
            'Cannot apply {} on a view that does not set '
            '`.queryset` or have a `.get_queryset()` method.'
        ).format(self.__class__.__name__)

        queryset = getattr(view, 'queryset', None)
        if queryset is None:
            queryset = view.get_queryset()
            assert queryset is not None, (
                'The value of {0}.queryset and {0}.get_queryset() is None.'.format(
                    view.__class__.__name__)
            )
        return queryset


class OrganizationListCreateDestroyPermission(AppDjangoModelPermissions):

    def __init__(self):
        self.perms_map = copy.deepcopy(self.perms_map)
        self.perms_map['GET'] = ['%(app_label)s.view_%(model_name)s']


class OrganizationRetrieveUpdateDestroyPermission(AppDjangoModelPermissions):

    def __init__(self):
        self.perms_map = copy.deepcopy(self.perms_map)
        self.perms_map['GET'] = ['%(app_label)s.view_%(model_name)s']
