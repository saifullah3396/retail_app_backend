"""
Defines the model of deepstream servers
"""
import re
import uuid

from core.utils import MAC_ADDRESS_VALIDATOR_REGEX
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator
from django.db import models
from django.utils import timezone


class DeepstreamLogEntry(models.Model):
    """Unique uuid for each message."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    """Message stored in the log entry"""
    message = models.CharField(max_length=500, blank=True, default="")

    """Time at which the log message was received."""
    received_at = models.DateTimeField(default=timezone.now)

    """Server with which the log info is associated with."""
    deepstream_server = models.ForeignKey(
        'deepstream_servers.DeepstreamServer',
        on_delete=models.CASCADE,
        null=True,
    )

    def __str__(self):
        """
        String serializer of the model
        """
        if self.deepstream_server:
            return "{}: [{}] {}".format(
                self.received_at, self.deepstream_server.id, self.message)
        else:
            return "{}: {}".format(
                self.received_at, self.message)


class DeepstreamDiagnostics(models.Model):
    """
    A model of a deepstream server diagnostics information
    """

    """Unique uuid for each diagnostic message."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    """Server with which the diagnostics info is associated with."""
    deepstream_server = models.ForeignKey(
        'deepstream_servers.DeepstreamServer',
        on_delete=models.CASCADE,
    )

    """CPU Utilization of the server."""
    cpu_utilization = \
        models.PositiveIntegerField(
            validators=[MaxValueValidator(100), ])

    """GPU Utilization of the server."""
    gpu_utilization = \
        models.PositiveIntegerField(
            validators=[MaxValueValidator(100), ])

    """Memory usage of the server."""
    memory_usage = \
        models.PositiveIntegerField(
            validators=[MaxValueValidator(100), ])

    """GPU Memory of the server."""
    gpu_memory_usage = \
        models.PositiveIntegerField(
            validators=[MaxValueValidator(100), ])

    """Temperature of the server."""
    temperature = models.IntegerField()

    """Time at which the diagnostics were received."""
    received_at = models.DateTimeField(null=True, blank=True)


class DeepstreamServer(models.Model):
    """
    A model of a deepstream server associated with a block.
    """

    ONLINE = 'online'
    IDLE = 'online-idle'
    IN_ERROR = 'online-in-error'
    STREAMING = 'online-streaming'
    OFFLINE = 'offline'
    STATUS = (
        (ONLINE, 'On-line'),
        (IDLE, 'On-line Idle'),
        (IN_ERROR, 'On-line In Error'),
        (STREAMING, 'On-line Streaming'),
        (OFFLINE, 'Off-line'),
    )

    """Unique uuid for each server."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    """Ip address of the server."""
    ip_addr = models.CharField(max_length=120, blank=True)

    """MAC address of the server."""
    mac_addr = models.CharField(max_length=17)

    """Block with which this server is associated."""
    block = models.ForeignKey("locations.Block", on_delete=models.CASCADE)

    """Status of the server whether it is currently online or offline"""
    status = models.CharField(
        max_length=20, choices=STATUS,
        default=OFFLINE
    )

    """Time field that is updated whenever the associated server makes a
        connection to django."""
    connected_at = models.DateTimeField(null=True, blank=True)

    """Time field that is updated whenever the associated server is
        disconnected"""
    last_response_received_at = models.DateTimeField(null=True, blank=True)

    def clean(self, *args, **kwargs):
        # validate mac address
        if not re.search(
                MAC_ADDRESS_VALIDATOR_REGEX, self.mac_addr):
            raise ValidationError({
                'mac_addr': 'Mac address is invalid.'
            })

        super(DeepstreamServer, self).clean(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.full_clean()
        super(DeepstreamServer, self).save(*args, **kwargs)

    def __str__(self):
        """
        String serializer of the model
        """
        return "Server={}".format(self.mac_addr)
