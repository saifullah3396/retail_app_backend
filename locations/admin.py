"""
Registers the models to the admin interface.
"""

from django.contrib.gis.db import models as geomodels
from django.contrib import admin

from .models import MeasurementFrame, Block, Floor, Location


admin.site.register(Location)
admin.site.register(Floor)
admin.site.register(Block)
admin.site.register(MeasurementFrame)
