"""
Registers the models to the admin interface
"""

from django.contrib import admin

from core.admin import BaseAdmin, list_display_fn, list_filter_fn

from .models import Outlet, OutletOwner, OutletUser


class OutletAdmin(BaseAdmin):
    """
    Defines custom admin interface view
    """
    list_display = list_display_fn(())
    list_filter = list_filter_fn(())


class OutletUserAdmin(BaseAdmin):
    """
    Defines custom admin interface view
    """
    list_display = list_display_fn(("user", "organization",))


class OutletOwnerAdmin(BaseAdmin):
    """
    Defines custom admin interface view
    """

    list_display = list_display_fn(("organization_user", "organization",))


admin.site.register(Outlet, OutletAdmin)
admin.site.register(OutletOwner, OutletOwnerAdmin)
admin.site.register(OutletUser, OutletUserAdmin)
