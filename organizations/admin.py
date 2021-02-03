"""
Registers the models to the admin interface
"""

from django.contrib import admin

from .models import Organization

admin.site.register(Organization)
