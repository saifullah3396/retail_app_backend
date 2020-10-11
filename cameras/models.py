import uuid
from django.db import models
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point


class Camera(models.Model):
    # generate unique uuid for each camera
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # user understandable identifying name for the place where the camera is
    # mounted
    place_name = models.CharField(default='Main', max_length=120, unique=True)

    # camera ip address
    ip_addr = models.CharField(max_length=120)

    # camera coordinates with respect to block frame
    coords = models.PointField(default=Point(0, 0))

    # block name with which the camera is associated
    block = models.ForeignKey(
        'locations.Block',
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return "{}, {}".format(self.place_name, str(self.block))
