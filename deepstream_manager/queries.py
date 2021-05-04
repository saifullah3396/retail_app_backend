"""
Defines the database queries that will be used around live data communication
between deepstream and django
"""

from backend.settings import (AMQP_PASSWORD, AMQP_SERVER_ADDRESS,
                              AMQP_SERVER_PORT, AMQP_USER)
from cameras.models import Camera
from cameras.serializers import CameraDetailSerializerDeepstream
from deepstream_servers.models import DeepstreamLogEntry, DeepstreamServer


def create_deepstream_log_entry(message, server_id):
    """
    Returns the deepstream log entry with associatd MAC address from
    the database
    """
    if server_id:
        log_entry = DeepstreamLogEntry.objects.create(
            message=message, deepstream_server_id=server_id)
        log_entry.save()


def generate_deepstream_config(server_id):
    """
    Generates a deepstream configuration for initializing the server data
    processing and streaming.
    """
    try:
        deepstream_server = DeepstreamServer.objects.get(id=server_id)
        cameras = Camera.objects.filter(
            deepstream_server=deepstream_server)
        config = {
            "id": str(deepstream_server.id),
            "cameras": CameraDetailSerializerDeepstream(
                cameras, many=True).data,
            "amqp_config": {
                "username": AMQP_USER,
                "password": AMQP_PASSWORD,
                "hostname": AMQP_SERVER_ADDRESS,
                "port": AMQP_SERVER_PORT
            }
        }
        return config
    except DeepstreamServer.DoesNotExist:
        return None


def get_deepstream_server(mac_addr):
    """
    Returns the deepstream server with associatd MAC address from the database
    """
    try:
        return DeepstreamServer.objects.get(mac_addr=mac_addr)
    except DeepstreamServer.DoesNotExist:
        return None


def get_deepstream_server_block_id(server):
    """
    Returns the deepstream server with associatd MAC address from the database
    """
    return server.block.id


def save_deepstream_server(deepstream_server):
    """
    Saves the given deepstream server to db
    """
    deepstream_server.save()
