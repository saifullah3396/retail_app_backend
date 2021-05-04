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


def camera_to_representation(data):
    """
    Defines the re-representation of the camera serialized state.
    """
    if 'coords' in data:
        data['coords'] = {
            "x": data['coords'][0],
            "y": data['coords'][1]
        }

    if 'point_coords_in_frame' in data:
        data['point_coords_in_frame'] = {
            "x1": data['point_coords_in_frame'][0],
            "y1": data['point_coords_in_frame'][1],
            "x2": data['point_coords_in_frame'][2],
            "y2": data['point_coords_in_frame'][3],
            "x3": data['point_coords_in_frame'][4],
            "y3": data['point_coords_in_frame'][5],
            "x4": data['point_coords_in_frame'][6],
            "y4": data['point_coords_in_frame'][7],
        }

    if 'point_coords_in_image' in data:
        data['point_coords_in_image'] = {
            "x1": data['point_coords_in_image'][0],
            "y1": data['point_coords_in_image'][1],
            "x2": data['point_coords_in_image'][2],
            "y2": data['point_coords_in_image'][3],
            "x3": data['point_coords_in_image'][4],
            "y3": data['point_coords_in_image'][5],
            "x4": data['point_coords_in_image'][6],
            "y4": data['point_coords_in_image'][7],
        }

    return data
