"""
Registers the Camera Model to the admin interface.
"""

from django.contrib import admin

from .models import Camera

admin.site.register(Camera)
