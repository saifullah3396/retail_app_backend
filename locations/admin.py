"""
Registers the models to the admin interface.
"""

from django.contrib import admin

from .models import Block, Floor, Location

admin.site.register(Location)
admin.site.register(Floor)
admin.site.register(Block)
