"""
Defines utility functions for this application.
"""

from core.utils import filter_objects_by_id_list, get_id_list


def filter_servers(request, servers):
    """
    Returns all the servers in the given locations set
    """

    # filter with ids if present
    id_list = get_id_list(request)
    if id_list:
        return filter_objects_by_id_list(
            servers, id_list)

    return servers
