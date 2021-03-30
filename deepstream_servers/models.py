"""
Defines the model of deepstream servers
"""
import uuid

from django.db import models


class DeepstreamServer(models.Model):
    """
    A model of a camera associated with a block.
    """

    """Unique uuid for each server."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    """Ip address for each server."""
    ip_addr = models.CharField(max_length=120)

    """Block with which this server is associated."""
    block = models.OneToOneField("locations.Block", on_delete=models.CASCADE)


def __str__(self):
    """
    String serializer of the model
    """
    return "DeepstreamServer={}".format(self.ip_addr)
