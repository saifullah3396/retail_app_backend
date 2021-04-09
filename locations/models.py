"""
Defines the models of this application.
"""

import uuid

from django.db import models


class Location(models.Model):
    """
    A model of a location associated with any organization
    """

    """Unique uuid for each location."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    """Location name."""
    name = models.CharField(max_length=120, unique=True)

    """Organization with which this location is associated."""
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.PROTECT,
    )

    def __str__(self):
        """
        String serializer of the model
        """
        return "Location={}, Organization={}".format(
            self.name, self.organization.name)


class Floor(models.Model):
    """
    A model of a floor associated with a location
    """

    """Unique uuid for each location."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    """Floor number."""
    number = models.IntegerField(default=0)

    """Location with which this floor is associated."""
    location = models.ForeignKey(
        'locations.Location',
        on_delete=models.PROTECT,
    )

    class Meta:
        """Don't allow non-unique floors for any given location."""
        unique_together = ('number', 'location',)

    def __str__(self):
        """
        String serializer of the model
        """
        return "Floor={}, {}".format(self.number, str(self.location))


class Block(models.Model):
    """
    A model of a single block floor associated with a location
    """

    """Unique uuid for each location."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    """Name number."""
    name = models.CharField(default='Main Block', max_length=150)

    """Block floor map image."""
    floor_map = models.ImageField(
        upload_to='maps', blank=True, null=True)

    """Pixel to meters resolution of the block from map to real world"""
    pixels_to_m_x = models.FloatField(default=0.0)
    pixels_to_m_y = models.FloatField(default=0.0)

    """Floor with which this block is associated."""
    floor = models.ForeignKey(
        'locations.Floor',
        on_delete=models.PROTECT,
    )

    class Meta:
        """Don't allow non-unique blocks for any given floor."""
        unique_together = ('name', 'floor',)

    def __str__(self):
        """
        String serializer of the model
        """
        return "Block={}, {}".format(self.name, str(self.floor))


class MeasurementFrame(models.Model):
    """
    A model of a single measurement frame associated with a block
    """

    """Unique uuid for each location."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    """Name of the position where frame is assigned."""
    name = models.CharField(default='', max_length=150)

    """Position of the frame on map in pixels."""
    pixel_pose_x = models.IntegerField(default=0)
    pixel_pose_y = models.IntegerField(default=0)
    pixel_pose_theta = models.IntegerField(default=0)

    """Block with which this block is associated."""
    block = models.ForeignKey(
        'locations.Block',
        on_delete=models.PROTECT,
    )

    def __str__(self):
        """
        String serializer of the model
        """
        return "Frame = [{}] (X, Y, Yaw) = ({}, {}, {})".format(
            self.name,
            self.pixel_pose_x,
            self.pixel_pose_y,
            self.pixel_pose_theta)
