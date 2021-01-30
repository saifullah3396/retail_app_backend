from rest_framework import permissions
from enum import Enum


class UserGroups(Enum):
    ORGANIZATION_ADMIN_GROUP = 1
    EMPLOYEE_GROUP = 2


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
