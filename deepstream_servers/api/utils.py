"""
Defines utility functions for this application.
"""

from core.utils import filter_objects_by_id_list, get_id_list
from deepstream_servers.models import DeepstreamServer


def filter_servers_with_locations(request, locations):
    """
    Returns all the servers in the given locations set
    """

    # get all servers in requested locations
    servers_in_locations = \
        DeepstreamServer.objects.filter(
            block__floor__location__in=locations)

    # filter with ids if present
    id_list = get_id_list(request)
    if id_list:
        return filter_objects_by_id_list(
            servers_in_locations, id_list)

    return servers_in_locations
