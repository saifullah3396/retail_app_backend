"""
Defines utility functions for this application.
"""

from cameras.models import Camera
from core.utils import filter_objects_by_id_list, get_id_list


def filter_cameras_with_locations(request, locations):
    """
    Returns all the cameras in the given locations set
    """

    # get all cameras in requested locations
    cameras_in_locations = \
        Camera.objects.filter(
            block__floor__location__in=locations)

    # filter with ids if present
    id_list = get_id_list(request)
    if id_list:
        return filter_objects_by_id_list(
            cameras_in_locations, id_list)

    return cameras_in_locations
