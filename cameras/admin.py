"""
Registers the models to the admin interface.
"""

from django.contrib import admin

from cameras.models import Camera

admin.site.register(Camera)
