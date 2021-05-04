"""
Registers the models to the admin interface.
"""

from django.contrib import admin

from .models import DeepstreamDiagnostics, DeepstreamLogEntry, DeepstreamServer

admin.site.register(DeepstreamServer)
admin.site.register(DeepstreamDiagnostics)
admin.site.register(DeepstreamLogEntry)
