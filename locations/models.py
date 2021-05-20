"""
Defines the models of this application.
"""
# pylint: disable=pointless-string-statement


from django.db import models
from django.db.models import Q, UniqueConstraint, When
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from safedelete import SOFT_DELETE_CASCADE
from safedelete.models import SafeDeleteModel

from core.db.fields import CustomAutoSlugField


class Location(SafeDeleteModel):
    """
    An abstract model of a location
    """
    _safedelete_policy = SOFT_DELETE_CASCADE

    """Location name."""
    name = models.CharField(max_length=120)

    class Meta:
        constraints = [
            UniqueConstraint(fields=["name"], condition=Q(
                deleted__isnull=True), name='unique_location_if_not_deleted')
        ]


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

    """Floor number."""
    number = models.PositiveIntegerField()

    """Location with which this floor is associated."""
    location = models.ForeignKey(
        'locations.Location',
        on_delete=models.CASCADE,
    )

    class Meta:
        """Don't allow non-unique floors for any given location."""
        constraints = [
            UniqueConstraint(fields=['number', 'location'], condition=Q(
                deleted__isnull=True), name='unique_floor_if_not_deleted')
        ]

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
        constraints = [
            UniqueConstraint(fields=["name", "floor"], condition=Q(
                deleted__isnull=True), name='unique_block_if_not_deleted')
        ]

    def __str__(self):
        """
        String serializer of the model
        """
        return "Block={}, {}".format(self.name, str(self.floor))
