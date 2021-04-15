"""
Registers the models to the admin interface.
"""

from django.contrib import admin

from .models import MeasurementFrame

admin.site.register(MeasurementFrame)
