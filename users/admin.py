"""
Registers the models to the admin interface
"""

from django.contrib import admin
from safedelete.admin import SafeDeleteAdmin, highlight_deleted
from safedelete.config import HARD_DELETE

from core.admin import BaseAdmin, list_display_fn, list_filter_fn

from .models import AppUser


class AppUserAdmin(BaseAdmin):
    """
    Defines custom admin interface view
    """
    list_display = list_display_fn(())
    list_filter = list_filter_fn(())


admin.site.register(AppUser, AppUserAdmin)
