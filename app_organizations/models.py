"""
Defines the organization related models for our application based on
django-organizations.
"""

from enum import Enum
from importlib import import_module

from django.apps import apps
from django.contrib.auth.models import Permission, PermissionsMixin
from django.core.exceptions import PermissionDenied
from django.core.management import call_command
from django.db import models
from django.utils.module_loading import module_has_submodule
from django.utils.translation import gettext as _
from organizations.abstract import (AbstractOrganization,
                                    AbstractOrganizationInvitation,
                                    AbstractOrganizationOwner,
                                    AbstractOrganizationUser)
from safedelete.config import HARD_DELETE, SOFT_DELETE_CASCADE
from safedelete.managers import SafeDeleteManager
from safedelete.models import SafeDeleteModel

from core.utils import get_organization_auth_backend


class DefaultOrganizationGroups(Enum):
    """
    An enumration for all the default organization user groups with their
    authority levels
    """
    OWNER = 0
    ADMIN = 1
    MEMBER = 2


class OrganizationGroupManager(SafeDeleteManager):
    """
    Defines organization group manager
    """
    use_in_migrations = True

    def get_by_natural_key(self, name):
        return self.get(name=name)


class OrganizationGroup(SafeDeleteModel):
    """
    Defines organization group model
    """
    name = models.CharField(_('name'), max_length=150)
    authority = models.PositiveIntegerField()
    organization = models.ForeignKey(
        'app_organizations.AppOrganization', on_delete=models.deletion.CASCADE)
    permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('permissions'),
        blank=True,
        related_name="organization_group_set",
        related_query_name="organization_group",
    )

    objects = OrganizationGroupManager()

    class Meta:
        verbose_name = _('organization group')
        verbose_name_plural = _('organization groups')
        unique_together = ['name', 'organization']

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.name,)


def _user_has_perm(user, perm, obj):
    """
    A backend can raise `PermissionDenied` to short-circuit permission checking.
    """

    auth_backend = get_organization_auth_backend()
    if not hasattr(auth_backend, 'has_perm'):
        return False
    try:
        if auth_backend().has_perm(user, perm, obj):
            return True
    except PermissionDenied:
        return False


def _user_has_module_perms(user, app_label):
    """
    A backend can raise `PermissionDenied` to short-circuit permission checking.
    """
    auth_backend = get_organization_auth_backend()
    if not hasattr(auth_backend, 'has_module_perms'):
        return False
    try:
        if auth_backend().has_module_perms(user, app_label):
            return True
    except PermissionDenied:
        return False


class OrganizationPermissionsMixin(PermissionsMixin):
    """
    Extends the permissions mixin for organization dependent roles and
    permissions
    """

    """We don't need this attribute for organizations"""
    is_superuser = None
    groups = models.ManyToManyField(
        OrganizationGroup,
        verbose_name=_('organization groups'),
        blank=True,
        help_text=_(
            'The organization groups this organization user belongs to. '
            'A organization user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name="organization_user_set",
        related_query_name="organization_user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=('organization permissions'),
        blank=True,
        help_text=('Specific permissions for this organization user.'),
        related_name="organization_user_set",
        related_query_name="organization_user",
    )

    class Meta:
        abstract = True

    def has_perm(self, perm, obj=None):
        """
        Return True if the user has the specified permission. Query all
        available auth backends, but return immediately if any backend returns
        True. Thus, a user who has permission from a single auth backend is
        assumed to have permission in general. If an object is provided, check
        permissions for that object.
        """

        # Otherwise we need to check the backends.
        return _user_has_perm(self, perm, obj)

    def has_module_perms(self, app_label):
        """
        Return True if the user has any permissions in the given app label.
        Use similar logic as has_perm(), above.
        """

        return _user_has_module_perms(self, app_label)


# pylint: disable=pointless-string-statement
class AppOrganization(SafeDeleteModel, AbstractOrganization):
    """
    A proxy model for django organization for customization
    """
    _safedelete_policy = SOFT_DELETE_CASCADE

    """Avatar image for each organization."""
    avatar = models.ImageField(
        upload_to='organizations/avatars', blank=True, null=True)

    class Meta(AbstractOrganization.Meta):
        proxy = False
        verbose_name = _("organization")
        verbose_name_plural = _("organizations")


class AppOrganizationUser(SafeDeleteModel, OrganizationPermissionsMixin,
                          AbstractOrganizationUser):
    """
    A proxy model for django organization for customization
    """
    _safedelete_policy = HARD_DELETE

    class Meta(AbstractOrganizationUser.Meta):
        proxy = False
        verbose_name = _("organization user")
        verbose_name_plural = _("organization users")

    def __str__(self):
        return '{}'.format(self.user.username)

    @property
    def highest_group(self):
        # get highest authority group
        return self.groups.all().order_by('authority').first()


class AppOrganizationOwner(SafeDeleteModel, AbstractOrganizationOwner):
    _safedelete_policy = HARD_DELETE

    class Meta(AbstractOrganizationOwner.Meta):
        proxy = False
        verbose_name = _("organization owner")
        verbose_name_plural = _("organization owners")

    def __str__(self):
        return '{}'.format(self.organization_user.user.username)


class AppOrganizationInvitation(SafeDeleteModel, AbstractOrganizationInvitation):
    _safedelete_policy = HARD_DELETE

    class Meta(AbstractOrganizationInvitation.Meta):
        proxy = False
        verbose_name = _("organization invitation")
        verbose_name_plural = _("organization invitations")
