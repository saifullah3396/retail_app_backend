# permissions.py
from django.contrib.auth.models import Group
from rest_framework import permissions
from backend.permissions import HasGroupPermission

class LocationsRUDPermissions(HasGroupPermission):
    """
    Ensure user has access to sub organizations
    """
    required_groups_mapping = {
        'GET': ['organization_admin'],
        'PUT': ['organization_admin'],
        'PATCH': ['organization_admin'],
        'DELETE': [],
    }

    def has_permission(self, request, view):
        return super().has_permission(request, view)
