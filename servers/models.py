"""
Defines the model of an servers
"""
import uuid

from django.db import models


class Server(models.Model):
    """
    A model of a camera associated with a block.
    """

    """Unique uuid for each server."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    """Ip address for each server."""
    ip_addr = models.CharField(max_length=120)

    """Block with which this server is associated."""
    block = models.OneToOneField("locations.Block", on_delete=models.CASCADE)

    """Cameras associated with this server."""
    camera = models.ForeignKey(
        'cameras.Camera',
        on_delete=models.CASCADE,
    )


def __str__(self):
    """
    String serializer of the model
    """
    return "Server={}".format(self.ip_addr)
