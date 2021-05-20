"""
Registers the models to the admin interface.
"""

from django.contrib import admin

from core.admin import BaseAdmin, list_display_fn, list_filter_fn

from .models import DSDiagnostics, DSLogEntry, DSServer


class DSServerAdmin(BaseAdmin):
    """
    Defines custom admin interface view
    """
    list_display = list_display_fn(())
    list_filter = list_filter_fn(())


class DSDiagnosticsAdmin(BaseAdmin):
    """
    Defines custom admin interface view
    """
    list_display = list_display_fn(())
    list_filter = list_filter_fn(())


class DSLogEntryAdmin(BaseAdmin):
    """
    Defines custom admin interface view
    """
    list_display = list_display_fn(())
    list_filter = list_filter_fn(())


admin.site.register(DSServer, DSServerAdmin)
admin.site.register(DSDiagnostics, DSDiagnosticsAdmin)
admin.site.register(DSLogEntry, DSLogEntryAdmin)
