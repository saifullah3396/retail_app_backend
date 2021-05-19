"""
Defines the user auth related models for our application
"""

from enum import Enum

from django.contrib import auth
from django.contrib.auth.models import Permission, PermissionsMixin
from django.core.exceptions import PermissionDenied
from django.db import models
from django.utils.translation import gettext as _
from safedelete.managers import SafeDeleteManager
from safedelete.models import SafeDeleteModel


class DefaultUserGroups(Enum):
    """
    An enumration for all the user groups that are available in our
    applications
    """
    SUPER_USER = 0
    FREE_USER = 1


class UserGroupManager(SafeDeleteManager):
    """
    Defines user group manager
    """
    use_in_migrations = True

    def get_by_natural_key(self, name):
        return self.get(name=name)


class UserGroup(SafeDeleteModel):
    name = models.CharField(_('name'), max_length=150, unique=True)
    authority = models.PositiveIntegerField()
    permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('permissions'),
        blank=True,
        related_name="user_group_set",
        related_query_name="user_group",
    )

    objects = UserGroupManager()

    class Meta:
        verbose_name = _('user group')
        verbose_name_plural = _('user groups')

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.name,)


def _user_has_perm(user, perm, obj):
    """
    A backend can raise `PermissionDenied` to short-circuit permission checking.
    """
    for backend in auth.get_backends():
        if not hasattr(backend, 'has_perm'):
            continue
        try:
            if backend.has_perm(user, perm, obj):
                return True
        except PermissionDenied:
            return False
    return False


def _user_has_module_perms(user, app_label):
    """
    A backend can raise `PermissionDenied` to short-circuit permission checking.
    """
    for backend in auth.get_backends():
        if not hasattr(backend, 'has_module_perms'):
            continue
        try:
            if backend.has_module_perms(user, app_label):
                return True
        except PermissionDenied:
            return False
    return False


class UserPermissionsMixin(PermissionsMixin):
    """
    Add the fields and methods necessary to support the Group and Permission
    models using the ModelBackend.
    """

    groups = models.ManyToManyField(
        UserGroup,
        verbose_name=_('groups'),
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name="user_set",
        related_query_name="user",
    )

    class Meta:
        abstract = True
