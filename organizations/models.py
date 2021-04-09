"""
Defines the model of an organization
"""

import uuid
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey


class Organization(MPTTModel):
    """
    A heirarchical tree based model of an organization
    """

    """Unique uuid for each organization."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    """Unique organization name."""
    name = models.CharField(max_length=125, default="Unknown", unique=True)

    """Description of the organization."""
    desc = models.TextField(blank=True)

    """Parent organization if any exists."""
    parent = TreeForeignKey('self', on_delete=models.PROTECT,
                            null=True, blank=True, related_name='children')

    def __str__(self):
        """
        String serializer of the model
        """
        return "Name = {}, Parent = {}".format(
            self.name, self.parent.name if self.parent else None)
