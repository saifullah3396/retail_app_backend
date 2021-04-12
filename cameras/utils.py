from locations.models import Location
from locations.utils import *

from .models import Camera


def get_cameras_in_locations(locations):
    """Returns all locations which present within the given organizations
    queryset."""
    return Camera.objects.filter(block__floor__location__in=locations)


def get_cameras_for_organization_admin(user):
    """Returns all cameras that are authorized to an organization admin."""
    locations = get_locations_for_organization_admin(user, include_self=True)
    return get_cameras_in_locations(locations)


def get_cameras_for_employee(user):
    """Returns all cameras that are authorized to an employee."""
    locations = get_locations_for_employee(user)
    return get_cameras_in_locations(locations)

