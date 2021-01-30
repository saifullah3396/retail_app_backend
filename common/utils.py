from django.contrib.auth.models import Group
from backend.settings import UserGroups


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
