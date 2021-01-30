from django.contrib.auth.models import Group
from common.permissions import UserGroups
from rest_framework import exceptions


def get_user_from_serializer(serializer, raise_exception=False):
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


def is_organization_admin(user):
    return is_in_group(user, UserGroups.ORGANIZATION_ADMIN_GROUP.name)


def is_employee(user):
    return is_in_group(user, UserGroups.EMPLOYEE_GROUP.name)
