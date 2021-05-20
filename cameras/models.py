# pylint: disable=missing-module-docstring
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import Q, UniqueConstraint
from safedelete.config import SOFT_DELETE_CASCADE
from safedelete.models import SafeDeleteModel


class Camera(SafeDeleteModel):
    """
    A model of a camera associated with a block.
    """
    _safedelete_policy = SOFT_DELETE_CASCADE

    """Camera ip Address."""
    ip_addr = models.CharField(max_length=120)

    """ Pixel coordinates of the camera in the map """
    coords = ArrayField(models.IntegerField(default=0), size=2, null=True)

    """ Block name with which the camera is associated """
    block = models.ForeignKey(
        'locations.Block',
        on_delete=models.PROTECT,
    )

    class Meta:
        """Don't allow non-unique ip addresses for any given block."""
        constraints = [
            UniqueConstraint(fields=["ip_addr", "block"], condition=Q(
                deleted__isnull=True), name='unique_camera_if_not_deleted')
        ]

    # """ Coordinates of the reference points p0, p1, p2, p3 in frame """
    # point_coords_in_frame = ArrayField(
    #     models.IntegerField(default=0), size=8, null=True)

    # """ Coordinates of the all the reference points in camera image pixel
    #     coordinates """
    # point_coords_in_image = ArrayField(
    #     models.IntegerField(default=0), size=8, null=True)

    # """ Frame with which the camera measurements are taken. """
    # measurement_frame = models.ForeignKey(
    #     'measurement_frames.MeasurementFrame',
    #     on_delete=models.PROTECT,
    #     null=True
    # )

    def __str__(self):
        """
        String serializer of the model
        """
        return "Camera={}, {}, {}".format(
            self.ip_addr,
            self.coords,
            str(self.block))
