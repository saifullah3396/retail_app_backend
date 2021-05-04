"""
Defines utility functions for this application.
"""

from core.utils import filter_objects_by_id_list, get_id_list
from locations.models import Block, Floor


def filter_locations(request, locations):
    """
    Filter input locations by id list.
    """
    id_list = get_id_list(request)
    if id_list:
        return filter_objects_by_id_list(
            locations, id_list)

    return locations


def filter_floors_with_locations(request, locations):
    """
    Returns all floors within the given locations, filtered by id
    """
    floors_in_location = \
        Floor.objects.filter(location__in=locations)

    # filter with ids if present
    id_list = get_id_list(request)
    if id_list:
        return filter_objects_by_id_list(
            floors_in_location, id_list)

    return floors_in_location


def filter_blocks_with_locations(request, locations):
    """
    Returns all blocks within the given locations, filtered by id
    """

    # get all blocks in requested floor
    blocks_in_locations = \
        Block.objects.filter(floor__location__in=locations)

    # filter with ids if present
    id_list = get_id_list(request)
    if id_list:
        return filter_objects_by_id_list(
            blocks_in_locations, id_list)

    return blocks_in_locations
