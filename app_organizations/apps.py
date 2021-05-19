"""
Defines the application configuration
"""

from enum import Enum

from django.apps import AppConfig


# pylint: disable=missing-class-docstring
class AppOrganizationsConfig(AppConfig):
    name = 'app_organizations'

    def ready(self):
        import app_organizations.signals.handlers
