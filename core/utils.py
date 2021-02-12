"""
Defines the common utility functions used in our applications.
"""

from django.contrib.auth.models import Group
from rest_framework import exceptions

from core.permissions import UserGroups


def get_user_from_serializer(serializer, raise_exception=False):
    """
    Returns the user from serializer context. Raises permission denied error
    if user is not found.
    """

    # get user requesting for a new registration
    request_user = None
    request = serializer.context.get("request")
    if request and hasattr(request, "user"):
        request_user = request.user
    else:
        if raise_exception:
            # raise unauthorized error if user is not found
            # most probably this will never get called
            raise exceptions.PermissionDenied()
    return request_user


def is_in_group(user, group_name):
    """
    Takes a user and a group name, and returns True if the user is in that
    group.
    """
    try:
        return Group.objects.get(name=group_name).\
            user_set.filter(id=user.id).exists()
    except Group.DoesNotExist:
        return None


def get_fn_by_group(user, group_to_fn_map):
    """
    Returns the function to be called for the user group the user is in
    given the user group to function map.
    """
    get_queryset_fn = None
    for group in UserGroups:
        if is_in_group(user, group.name):
            get_queryset_fn = group_to_fn_map.get(group, None)
            break
    if get_queryset_fn is None:
        raise exceptions.PermissionDenied()
    return get_queryset_fn


def is_organization_admin(user):
    """
    Returns true if the user is in ORGANIZATION_ADMIN_GROUP user group.
    """
    return is_in_group(user, UserGroups.ORGANIZATION_ADMIN_GROUP.name)


def is_employee(user):
    """
    Returns true if the user is in EMPLOYEE_GROUP user group.
    """
    return is_in_group(user, UserGroups.EMPLOYEE_GROUP.name)


def filter_queryset_by_id_list(query_set, id_list):
    """
    Filters a queryset by th given list of ids
    """
    return query_set.filter(id__in=id_list)


def exclude_queryset_by_id_list(query_set, id_list):
    """
    Filters a queryset by excluding the given list of ids
    """
    return query_set.exclude(id__in=id_list)
