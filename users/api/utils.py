"""
Defines utility functions for this application.
"""

from core.utils import filter_objects_by_id_list, get_id_list
from users.models import AppUser


def get_users_in_organizations(organizations):
    """
    Returns all users which present within the given organizations
    queryset
    """
    return AppUser.objects.filter(organization__in=organizations)


def filter_users_with_organizations(request, organizations):
    """
    Returns all floors within the given locations, filtered by id
    """
    users_in_organizations = get_users_in_organizations(organizations)

    # filter with ids if present
    id_list = get_id_list(request)
    if id_list:
        return filter_objects_by_id_list(
            users_in_organizations, id_list)

    return users_in_organizations
