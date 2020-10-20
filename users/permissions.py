# permissions.py
from django.contrib.auth.models import Group
from rest_framework import permissions


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


class HasGroupPermission(permissions.BasePermission):
    """
    Ensure user is in required groups.
    """

    def has_permission(self, request, view):

        # Determine the required groups for this particular request method.
        required_groups = self.required_groups_mapping.get(request.method, [])

        # Return True if the user has any of the required groups or is staff.
        return \
            any([
                is_in_group(request.user, group_name)
                if group_name != "__all__"
                else True
                for group_name in required_groups
            ]) or (request.user and request.user.is_staff)


class CanRegisterUser(HasGroupPermission):
    """
    Ensure user is in the organization_admin or sub_organization_admin group
    """
    required_groups_mapping = {
        'GET': ['organization_admin', 'sub_organization_admin'],
        'POST': ['organization_admin', 'sub_organization_admin'],
        'PUT': ['organization_admin', 'sub_organization_admin'],
    }

    def has_permission(self, request, view):
        return super().has_permission(request, view)
