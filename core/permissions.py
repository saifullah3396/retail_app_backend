"""
Defines the core permissions functionality used across our applications.
"""


import copy

from rest_framework import permissions


class AppDjangoModelPermissions(permissions.DjangoModelPermissions):
    """
    Customizes the base DjangoModlePermissions class.
    """

    def __init__(self):
        self.perms_map = copy.deepcopy(self.perms_map)
        self.perms_map['GET'] = ['%(app_label)s.view_%(model_name)s']

    def _queryset(self, view):
        """
        Redefines function so that DjangoModelPermissions does not use
        get_queryset() just to get the model if self.queryset is already
        available. For this reason, self.queryset should be set to
        model.objects.none() if get_queryset is implemented in the view.
        """
        assert hasattr(view, 'get_queryset') \
            or getattr(view, 'queryset', None) is not None, (
            'Cannot apply {} on a view that does not set '
            '`.queryset` or have a `.get_queryset()` method.'
        ).format(self.__class__.__name__)

        queryset = getattr(view, 'queryset', None)
        if queryset is None:
            queryset = view.get_queryset()
            assert queryset is not None, (
                'The value of {0}.queryset and '
                '{0}.get_queryset() is None.'.format(
                    view.__class__.__name__)
            )
        return queryset
