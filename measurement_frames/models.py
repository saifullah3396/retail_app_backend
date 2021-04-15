"""
Defines the models of this application.
"""

import uuid

from django.db import models


# pylint: disable=pointless-string-statement
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
