"""
Registers the DeepstreamServer Model to the admin interface.
"""

from django.contrib import admin

from .models import DeepstreamServer

admin.site.register(DeepstreamServer)
