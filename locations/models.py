"""
Defines the models of this application.
"""
# pylint: disable=pointless-string-statement

import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _
from safedelete import SOFT_DELETE, SOFT_DELETE_CASCADE
from safedelete.models import SafeDeleteModel

from core.db.fields import CustomAutoSlugField


class Location(SafeDeleteModel):
    """
    An abstract model of a location
    """
    _safedelete_policy = SOFT_DELETE

    """Unique uuid for each location."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    """Location name."""
    name = models.CharField(max_length=120)

    """Location slug."""
    slug = CustomAutoSlugField(
        max_length=120,
        blank=False,
        editable=True,
        unique=True,
        populate_from="name",
        help_text=_(
            "The name in all lowercase, suitable for URL identification"),)


class OutletLocation(Location):
    """
    A model of a location associated with a organization
    """
    _safedelete_policy = SOFT_DELETE_CASCADE

    """Outlet with which this location is associated."""
    outlet = models.ForeignKey(
        'outlets.Outlet',
        on_delete=models.CASCADE)

    def __str__(self):
        """
        String serializer of the model
        """
        return "Location={}, Organization={}".format(
            self.name, self.outlet.name)


class Floor(SafeDeleteModel):
    """
    A model of a floor associated with a location
    """
    _safedelete_policy = SOFT_DELETE_CASCADE

    """Unique uuid for each location."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    """Floor number."""
    number = models.PositiveIntegerField()

    """Location with which this floor is associated."""
    location = models.ForeignKey(
        'locations.Location',
        on_delete=models.CASCADE,
    )

    class Meta:
        """Don't allow non-unique floors for any given location."""
        unique_together = ('number', 'location',)

    def __str__(self):
        """
        String serializer of the model
        """
        return "Floor={}, {}".format(self.number, str(self.location))


class Block(SafeDeleteModel):
    """
    A model of a single block floor associated with a location
    """
    _safedelete_policy = SOFT_DELETE_CASCADE

    """Unique uuid for each location."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    """Name number."""
    name = models.CharField(max_length=150)

    """Block floor map image."""
    floor_map = models.ImageField(upload_to='maps')

    """Pixel to meters resolution of the block from map to real world"""
    pixels_to_m_x = models.FloatField()
    pixels_to_m_y = models.FloatField()

    """Floor with which this block is associated."""
    floor = models.ForeignKey(
        'locations.Floor',
        on_delete=models.CASCADE,
    )

    class Meta:
        """Don't allow non-unique blocks for any given floor."""
        unique_together = ('name', 'floor',)

    def __str__(self):
        """
        String serializer of the model
        """
        return "Block={}, {}".format(self.name, str(self.floor))
