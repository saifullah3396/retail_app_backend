"""
Defines the models of this application.
"""


from django.db import models
from django.db.models.constraints import Q, UniqueConstraint
from safedelete.models import SafeDeleteModel


# pylint: disable=pointless-string-statement
class MeasurementFrame(SafeDeleteModel):
    """
    A model of a single measurement frame associated with a block
    """

    """Name of the position where frame is assigned."""
    name = models.CharField(max_length=150)

    """Position of the frame on map in pixels."""
    pixel_pose_x = models.IntegerField()
    pixel_pose_y = models.IntegerField()
    pixel_pose_theta = models.IntegerField()

    """Block with which this block is associated."""
    block = models.ForeignKey(
        'locations.Block',
        on_delete=models.PROTECT,
    )

    class Meta:
        """Don't allow non-unique names for any given block."""
        constraints = [
            UniqueConstraint(fields=["name", "block"], condition=Q(
                deleted__isnull=True), name='unique_frame_if_not_deleted')
        ]

    def __str__(self):
        """
        String serializer of the model
        """
        return "Frame = [{}] (X, Y, Yaw) = ({}, {}, {})".format(
            self.name,
            self.pixel_pose_x,
            self.pixel_pose_y,
            self.pixel_pose_theta)
