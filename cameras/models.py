from django.db import models
from django.contrib.gis.db import models

from mptt.models import MPTTModel, TreeForeignKey
import uuid
from django.contrib.gis.geos import Point
# Create your models here.


class Camera(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    """Location name."""
    place_name = models.CharField(max_length=125, default="Main", unique=True)

    """Camera ip Address."""
    ip_addr = models.CharField(max_length=120)

        # camera coordinates with respect to block frame
    coords = models.PointField(default=Point(0, 0))

    """ block name with which the camera is associated """
    block = models.ForeignKey(
        'locations.Block',
        on_delete=models.CASCADE,
    )

    def __str__(self):
        """
        String serializer of the model
        """
        return "Camera={}, {}".format(self.place_name, str(self.block))
