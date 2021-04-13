"""
Registers the Camera Model to the admin interface.
"""

from django.contrib import admin

from cameras.models import Camera

admin.site.register(Camera)
