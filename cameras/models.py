import uuid

from django.contrib.gis.db import models


class Camera(models.Model):
    """
    A model of a camera associated with a block.
    """

    """Unique uuid for each camera."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    """Camera ip Address."""
    ip_addr = models.CharField(max_length=120)

    """ Coordinates of the reference point p0 in frame """
    p0_coord_in_frame_x = models.IntegerField(default=0)
    p0_coord_in_frame_y = models.IntegerField(default=0)

    """ Coordinates of the other mapping points p1, p2, p3 wrt, p0 in frame """
    p1_coord_in_frame_x = models.IntegerField(default=0)
    p1_coord_in_frame_y = models.IntegerField(default=0)
    p2_coord_in_frame_x = models.IntegerField(default=0)
    p2_coord_in_frame_y = models.IntegerField(default=0)
    p3_coord_in_frame_x = models.IntegerField(default=0)
    p3_coord_in_frame_y = models.IntegerField(default=0)

    """ Coordinates of the all the reference points in camera image pixel
        coordinates """
    p0_coord_in_image_x = models.IntegerField(default=0)
    p0_coord_in_image_y = models.IntegerField(default=0)
    p1_coord_in_image_x = models.IntegerField(default=0)
    p1_coord_in_image_y = models.IntegerField(default=0)
    p2_coord_in_image_x = models.IntegerField(default=0)
    p2_coord_in_image_y = models.IntegerField(default=0)
    p3_coord_in_image_x = models.IntegerField(default=0)
    p3_coord_in_image_y = models.IntegerField(default=0)

    """ Block name with which the camera is associated """
    block = models.ForeignKey(
        'locations.Block',
        on_delete=models.CASCADE,
    )

    """ Server with which the camera is associated """
    deepstream_server = models.ForeignKey(
        'deepstream_servers.DeepstreamServer',
        on_delete=models.CASCADE,
    )

    """ Frame with which the camera measurements are taken. """
    measurement_frame = models.ForeignKey(
        'locations.MeasurementFrame',
        on_delete=models.CASCADE,
        null=True
    )

    def __str__(self):
        """
        String serializer of the model
        """
        return "Camera={}, {}, {}, {}".format(
            self.ip_addr,
            str(self.deepstream_server),
            str(self.measurement_frame),
            str(self.block))
