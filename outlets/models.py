"""
Defines the outlet related models for our application based on
django-organizations.
"""

import uuid

from django.db import models
from django.db.models.fields import related
from django.utils.translation import gettext_lazy as _
from organizations.abstract import (AbstractOrganization,
                                    AbstractOrganizationInvitation,
                                    AbstractOrganizationOwner,
                                    AbstractOrganizationUser)
from organizations.base import AbstractBaseOrganizationUser
from safedelete.config import HARD_DELETE, SOFT_DELETE_CASCADE
from safedelete.models import SafeDeleteModel


class AliasField(models.Field):
    def contribute_to_class(self, cls, name, private_only=False):
        super(AliasField, self).contribute_to_class(
            cls, name, private_only=True)
        setattr(cls, name, self)

    def __get__(self, instance, instance_type=None):
        return getattr(instance, self.db_column)


# pylint: disable=pointless-string-statement
class Outlet(SafeDeleteModel, AbstractOrganization):
    """
    A proxy model for django organization for customization
    """
    _safedelete_policy = SOFT_DELETE_CASCADE

    """Unique uuid for each organization."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    """Avatar image for each organization."""
    avatar = models.ImageField(
        upload_to='organizations/outlets/avatars', blank=True, null=True)

    """Organization with which this outlet is associated."""
    organization = models.ForeignKey(
        'app_organizations.AppOrganization',
        related_name='outlets',
        on_delete=models.CASCADE)

    class Meta:
        proxy = False
        verbose_name = _("outlet")
        verbose_name_plural = _("outlets")


class OutletUser(SafeDeleteModel, AbstractOrganizationUser):
    """
    A proxy model for django organization for customization
    """
    _safedelete_policy = HARD_DELETE

    class Meta:
        proxy = False
        verbose_name = _("outlet user")
        verbose_name_plural = _("outlet users")
        unique_together = ("user", "organization")

    """Unique uuid for each organization user."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    outlet = AliasField(db_column='organization_id')

    def __str__(self):
        return '{}'.format(self.user.username)


class OutletOwner(SafeDeleteModel, AbstractOrganizationOwner):
    _safedelete_policy = HARD_DELETE

    class Meta:
        proxy = False
        verbose_name = _("outlet owner")
        verbose_name_plural = _("outlet owners")

    def __str__(self):
        return '{}'.format(self.organization_user.user.username)


class OutletInvitation(SafeDeleteModel, AbstractOrganizationInvitation):
    _safedelete_policy = HARD_DELETE

    class Meta:
        proxy = False
        verbose_name = _("outlet invitation")
        verbose_name_plural = _("outlet invitations")
