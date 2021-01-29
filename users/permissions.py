# permissions.py
from django.contrib.auth.models import Group
from rest_framework import permissions
from backend.permissions import HasGroupPermission


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


class CanAccessUser(HasGroupPermission):
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
