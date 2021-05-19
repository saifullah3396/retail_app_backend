"""
Defines the application configuration
"""

from enum import Enum

from django.apps import AppConfig


# pylint: disable=missing-class-docstring
class OutletsConfig(AppConfig):
    name = 'outlets'

    def ready(self):
        import outlets.signals.handlers
