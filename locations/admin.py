"""
Registers the models to the admin interface.
"""

from django.contrib import admin

from core.admin import BaseAdmin, list_display_fn, list_filter_fn

from .models import Block, Floor, OutletLocation


class OutletLocationAdmin(BaseAdmin):
    """
    Defines custom user admin interface view
    """
    list_display = list_display_fn(())
    list_filter = list_filter_fn(())


class FloorAdmin(BaseAdmin):
    """
    Defines custom user admin interface view
    """
    list_display = list_display_fn(())
    list_filter = list_filter_fn(())


class BlockAdmin(BaseAdmin):
    """
    Defines custom user admin interface view
    """
    list_display = list_display_fn(())
    list_filter = list_filter_fn(())


admin.site.register(OutletLocation, OutletLocationAdmin)
admin.site.register(Floor, FloorAdmin)
admin.site.register(Block, BlockAdmin)
