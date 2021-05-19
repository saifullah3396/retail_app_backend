"""
Registers the models to the admin interface.
"""

from django.contrib import admin
from safedelete.admin import SafeDeleteAdmin, highlight_deleted

from backend.settings import DEFAULT_ADMIN_DELETION_POLICY


def list_display_fn(childs):
    return (highlight_deleted, *childs) + SafeDeleteAdmin.list_display


def list_filter_fn(childs):
    return (*childs,) + SafeDeleteAdmin.list_filter


class BaseAdmin(SafeDeleteAdmin):
    """
    Defines custom user location interface view
    """

    # allow hard deletion from admin interface
    def delete_model(self, request, obj):
        """
        Given a model instance delete it from the database.
        """
        obj.delete(force_policy=DEFAULT_ADMIN_DELETION_POLICY)

    def delete_queryset(self, request, queryset):
        """Given a queryset, delete it from the database."""
        queryset.delete(force_policy=DEFAULT_ADMIN_DELETION_POLICY)
