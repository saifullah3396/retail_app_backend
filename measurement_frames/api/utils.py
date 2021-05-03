"""
Defines utility functions for this application.
"""

from core.utils import filter_objects_by_id_list, get_id_list
from measurement_frames.models import MeasurementFrame


def filter_frames_with_locations(request, locations):
    """
    Returns all the frames in the given locations set
    """

    # get all frames in requested locations
    frames_in_locations = \
        MeasurementFrame.objects.filter(
            block__floor__location__in=locations)

    # filter with ids if present
    id_list = get_id_list(request)
    if id_list:
        return filter_objects_by_id_list(
            frames_in_locations, id_list)

    return frames_in_locations
