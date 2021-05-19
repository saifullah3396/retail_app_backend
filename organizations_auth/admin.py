"""
Registers the models to the admin interface
"""

from django.contrib import admin
from safedelete import HARD_DELETE
from safedelete.admin import SafeDeleteAdmin, highlight_deleted

from core.admin import BaseAdmin, list_display_fn, list_filter_fn

from .models import OrganizationGroup


class OrganizationGroupAdmin(BaseAdmin):
    """
    Defines custom user admin interface view
    """
    list_display = list_display_fn(())
    list_filter = list_filter_fn(())


admin.site.register(OrganizationGroup, OrganizationGroupAdmin)
