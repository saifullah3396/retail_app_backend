"""
Defines the model of an organization
"""

import uuid

from django.db import models
from django.db.models import Q
from django.db.models.constraints import UniqueConstraint
from mptt.models import MPTTModel, TreeForeignKey


# pylint: disable=pointless-string-statement
class Organization(MPTTModel):
    """
    A heirarchical tree based model of an organization
    """

    """Unique uuid for each organization."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    """Unique organization name."""
    name = models.CharField(max_length=125)

    """Parent organization if any exists."""
    parent = TreeForeignKey('self', on_delete=models.PROTECT,
                            null=True, blank=True, related_name='children')

    class Meta:
        """Don't allow non-unique names for any given parent."""
        constraints = [
            UniqueConstraint(fields=['name', 'parent'],
                             name='unique_with_parent'),
            UniqueConstraint(fields=['name'],
                             condition=Q(parent=None),
                             name='unique_without_parent'),
        ]

    def __str__(self):
        """
        String serializer of the model
        """
        return "Name = {}, Parent = {}".format(
            self.name, self.parent.name if self.parent else None)
