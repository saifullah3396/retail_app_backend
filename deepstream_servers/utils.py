# pylint: disable=missing-module-docstring
from locations.utils import (get_locations_for_employee,
                             get_locations_for_organization_admin)

from .models import DeepstreamServer


def get_servers_in_locations(locations):
    """
    Returns all locations which present within the given organizations
    queryset
    """
    return DeepstreamServer.objects.filter(block__floor__location__in=locations)


def get_servers_for_organization_admin(user):
    """
    Returns all servers that are authorized to an organization admin
    """
    print('servers_for_organization_admin')

    # Returns all locations that are authorized to an organization admin
    locations = get_locations_for_organization_admin(user, include_self=True)

    return get_servers_in_locations(locations)


def get_servers_for_employee(user):
    """
    Returns all servers that are authorized to an employee
    """
    locations = get_locations_for_employee(user)
    return get_servers_in_locations(locations)
